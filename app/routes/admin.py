from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required
from sqlalchemy import case, func

from app.models import Course, CourseSelection, Semester, Student, Teacher, User, db
from app.utils.auth import role_required
from app.utils.backup import build_backup_file

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("")
@login_required
@role_required("admin")
def dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    students = Student.query.all()
    teachers = Teacher.query.all()
    courses = Course.query.order_by(Course.course_no).all()
    semesters = Semester.query.order_by(Semester.id.desc()).all()
    active_semester = Semester.query.filter_by(is_active=True).first()
    stats = _build_admin_statistics()
    return render_template(
        "admin/dashboard.html",
        current_admin=current_user,
        users=users,
        students=students,
        teachers=teachers,
        courses=courses,
        semesters=semesters,
        active_semester=active_semester,
        stats=stats,
    )


def _parse_date(value):
    value = (value or "").strip()
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def _build_admin_statistics():
    course_rows = (
        db.session.query(
            Course.id,
            Course.course_no,
            Course.course_name,
            Course.credit,
            Course.max_students,
            Course.current_students,
            Semester.name.label("semester_name"),
            func.count(CourseSelection.id).label("selected_count"),
            func.avg(CourseSelection.grade).label("avg_grade"),
        )
        .outerjoin(CourseSelection, CourseSelection.course_id == Course.id)
        .outerjoin(Semester, Semester.id == Course.semester_id)
        .group_by(
            Course.id,
            Course.course_no,
            Course.course_name,
            Course.credit,
            Course.max_students,
            Course.current_students,
            Semester.name,
        )
        .order_by(Course.course_no)
        .all()
    )

    teacher_rows = (
        db.session.query(
            Teacher.teacher_no,
            Teacher.name,
            func.count(Course.id).label("course_count"),
            func.coalesce(func.sum(Course.current_students), 0).label("student_count"),
        )
        .outerjoin(Course, Course.teacher_id == Teacher.id)
        .group_by(Teacher.id, Teacher.teacher_no, Teacher.name)
        .order_by(Teacher.teacher_no)
        .all()
    )

    grade_rows = (
        db.session.query(
            Course.course_no,
            Course.course_name,
            func.sum(case((CourseSelection.grade < 60, 1), else_=0)).label("fail_count"),
            func.sum(case(((CourseSelection.grade >= 60) & (CourseSelection.grade < 70), 1), else_=0)).label("pass_count"),
            func.sum(case(((CourseSelection.grade >= 70) & (CourseSelection.grade < 80), 1), else_=0)).label("mid_count"),
            func.sum(case(((CourseSelection.grade >= 80) & (CourseSelection.grade < 90), 1), else_=0)).label("good_count"),
            func.sum(case((CourseSelection.grade >= 90, 1), else_=0)).label("excellent_count"),
        )
        .join(CourseSelection, CourseSelection.course_id == Course.id)
        .filter(CourseSelection.grade.isnot(None))
        .group_by(Course.id, Course.course_no, Course.course_name)
        .order_by(Course.course_no)
        .all()
    )

    credit_rows = (
        db.session.query(
            Student.student_no,
            Student.name,
            func.coalesce(
                func.sum(case((CourseSelection.grade >= 60, Course.credit), else_=0)),
                0,
            ).label("completed_credits"),
            func.avg(CourseSelection.grade).label("avg_grade"),
        )
        .outerjoin(CourseSelection, CourseSelection.student_id == Student.id)
        .outerjoin(Course, Course.id == CourseSelection.course_id)
        .group_by(Student.id, Student.student_no, Student.name)
        .order_by(Student.student_no)
        .all()
    )

    selected_count = db.session.query(func.count(CourseSelection.id)).scalar() or 0
    graded_count = (
        db.session.query(func.count(CourseSelection.id))
        .filter(CourseSelection.grade.isnot(None))
        .scalar()
        or 0
    )

    return {
        "summary": {
            "students": Student.query.count(),
            "teachers": Teacher.query.count(),
            "courses": Course.query.count(),
            "selections": selected_count,
            "graded": graded_count,
        },
        "courses": course_rows,
        "teachers": teacher_rows,
        "grades": grade_rows,
        "credits": credit_rows,
    }


@admin_bp.route("/user/create", methods=["POST"])
@login_required
@role_required("admin")
def create_user():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    role = request.form.get("role", "").strip()
    name = request.form.get("name", "").strip()
    department = request.form.get("department", "").strip()
    no = request.form.get("no", "").strip()
    gender = request.form.get("gender", "").strip() or None
    age = request.form.get("age", type=int)

    if not username or not password or role not in {"student", "teacher", "admin"}:
        flash("用户信息不完整。", "danger")
        return redirect(url_for("admin.dashboard"))

    if User.query.filter_by(username=username).first():
        flash("用户名已存在。", "danger")
        return redirect(url_for("admin.dashboard"))

    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    if role == "student":
        if not (no and name and department):
            flash("学生信息不完整。", "danger")
            db.session.rollback()
            return redirect(url_for("admin.dashboard"))
        db.session.add(
            Student(
                user_id=user.id,
                student_no=no,
                name=name,
                age=age,
                gender=gender if gender in {"男", "女"} else None,
                department=department,
            )
        )
    elif role == "teacher":
        if not (no and name and department):
            flash("教师信息不完整。", "danger")
            db.session.rollback()
            return redirect(url_for("admin.dashboard"))
        db.session.add(
            Teacher(
                user_id=user.id,
                teacher_no=no,
                name=name,
                department=department,
            )
        )

    db.session.commit()
    flash("用户创建成功。", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/user/<int:user_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_user(user_id):
    if current_user.id == user_id:
        flash("不能删除当前登录管理员。", "danger")
        return redirect(url_for("admin.dashboard"))

    user = User.query.get_or_404(user_id)
    if user.student:
        db.session.delete(user.student)
    if user.teacher:
        for course in user.teacher.courses:
            db.session.delete(course)
        db.session.delete(user.teacher)
    db.session.delete(user)
    db.session.commit()
    flash("用户删除成功。", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/user/<int:user_id>/reset_password", methods=["POST"])
@login_required
@role_required("admin")
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    new_password = request.form.get("new_password", "").strip() or "123456"
    user.set_password(new_password)
    db.session.commit()
    flash(f"用户 {user.username} 密码已重置。", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/course/create", methods=["POST"])
@login_required
@role_required("admin")
def create_course():
    try:
        credit = float(request.form.get("credit", 0))
        max_students = int(request.form.get("max_students", 100))
    except ValueError:
        flash("课程参数格式错误。", "danger")
        return redirect(url_for("admin.dashboard"))

    course_no = request.form.get("course_no", "").strip()
    course_name = request.form.get("course_name", "").strip()
    department = request.form.get("department", "").strip()
    teacher_id = request.form.get("teacher_id", type=int)
    semester_id = request.form.get("semester_id", type=int)
    course_type = request.form.get("course_type", "required").strip() or "required"
    status = request.form.get("status", "open").strip() or "open"

    if not all([course_no, course_name, department, teacher_id]):
        flash("课程信息不完整。", "danger")
        return redirect(url_for("admin.dashboard"))
    if Course.query.filter_by(course_no=course_no).first():
        flash("课程号已存在。", "danger")
        return redirect(url_for("admin.dashboard"))

    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        flash("教师不存在。", "danger")
        return redirect(url_for("admin.dashboard"))

    db.session.add(
        Course(
            course_no=course_no,
            course_name=course_name,
            credit=credit,
            department=department,
            teacher_id=teacher.id,
            semester_id=semester_id,
            course_type=course_type,
            max_students=max_students if max_students > 0 else 100,
            status=status,
        )
    )
    db.session.commit()
    flash("课程创建成功。", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/course/<int:course_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash("课程删除成功。", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/semester/create", methods=["POST"])
@login_required
@role_required("admin")
def create_semester():
    name = request.form.get("name", "").strip()
    if not name:
        flash("学期名称不能为空。", "danger")
        return redirect(url_for("admin.dashboard"))
    if Semester.query.filter_by(name=name).first():
        flash("学期名称已存在。", "danger")
        return redirect(url_for("admin.dashboard"))

    try:
        start_date = _parse_date(request.form.get("start_date"))
        end_date = _parse_date(request.form.get("end_date"))
    except ValueError:
        flash("日期格式应为 YYYY-MM-DD。", "danger")
        return redirect(url_for("admin.dashboard"))

    is_active = request.form.get("is_active") == "on"
    if is_active:
        Semester.query.update({Semester.is_active: False})

    db.session.add(Semester(name=name, start_date=start_date, end_date=end_date, is_active=is_active))
    db.session.commit()
    flash("学期创建成功。", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/semester/<int:semester_id>/activate", methods=["POST"])
@login_required
@role_required("admin")
def activate_semester(semester_id):
    semester = Semester.query.get_or_404(semester_id)
    Semester.query.update({Semester.is_active: False})
    semester.is_active = True
    db.session.commit()
    flash("当前学期已切换。", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/semester/<int:semester_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_semester(semester_id):
    semester = Semester.query.get_or_404(semester_id)
    Course.query.filter_by(semester_id=semester.id).update({Course.semester_id: None})
    db.session.delete(semester)
    db.session.commit()
    flash("学期删除成功，相关课程已改为未分配学期。", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/backup")
@login_required
@role_required("admin")
def backup():
    output = build_backup_file()
    return send_file(output, mimetype="application/json", as_attachment=True, download_name="student_course_backup.json")
