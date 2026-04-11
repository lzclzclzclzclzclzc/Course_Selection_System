from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

from app.models import Course, Student, Teacher, User, db
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
    courses = Course.query.all()
    return render_template(
        "admin/dashboard.html",
        current_admin=current_user,
        users=users,
        students=students,
        teachers=teachers,
        courses=courses,
    )


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
            max_students=max_students if max_students > 0 else 100,
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


@admin_bp.route("/backup")
@login_required
@role_required("admin")
def backup():
    output = build_backup_file()
    return send_file(output, mimetype="application/json", as_attachment=True, download_name="student_course_backup.json")

