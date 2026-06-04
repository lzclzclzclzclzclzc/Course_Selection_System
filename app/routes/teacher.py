from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app.models import Course, CourseSelection, db
from app.utils.auth import role_required

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")


def _teacher():
    return current_user.teacher


@teacher_bp.route("")
@login_required
@role_required("teacher")
def dashboard():
    teacher = _teacher()
    courses = Course.query.filter_by(teacher_id=teacher.id).all()
    return render_template("teacher/dashboard.html", teacher=teacher, courses=courses)


@teacher_bp.route("/load_students", methods=["POST"])
@login_required
@role_required("teacher")
def load_students():
    teacher = _teacher()
    course_id = request.form.get("course_id") or (request.json or {}).get("course_id")
    if not course_id:
        return jsonify({"students": []})

    course = Course.query.get(course_id)
    if not course or course.teacher_id != teacher.id:
        return jsonify({"students": []}), 403

    selections = CourseSelection.query.filter_by(course_id=course.id).all()
    students = [
        {
            "selection_id": s.id,
            "student_no": s.student.student_no,
            "name": s.student.name,
            "department": s.student.department,
            "grade": float(s.grade) if s.grade is not None else None,
        }
        for s in selections
    ]
    return jsonify({"students": students})


@teacher_bp.route("/save_grade", methods=["POST"])
@login_required
@role_required("teacher")
def save_grade():
    teacher = _teacher()
    selection_id = request.form.get("selection_id") or (request.json or {}).get("selection_id")
    grade = request.form.get("grade") or (request.json or {}).get("grade")

    if selection_id is None or grade is None:
        return jsonify({"success": False, "message": "参数不完整。"}), 400

    try:
        grade_float = float(grade)
    except ValueError:
        return jsonify({"success": False, "message": "成绩格式错误。"}), 400

    if not (0 <= grade_float <= 100):
        return jsonify({"success": False, "message": "成绩范围必须在 0-100。"}), 400

    selection = CourseSelection.query.get(selection_id)
    if not selection:
        return jsonify({"success": False, "message": "选课记录不存在。"}), 404

    if selection.course.teacher_id != teacher.id:
        return jsonify({"success": False, "message": "无权操作该课程成绩。"}), 403

    selection.grade = grade_float
    db.session.commit()
    return jsonify({"success": True, "message": "保存成功。"})


@teacher_bp.route("/save_syllabus", methods=["POST"])
@login_required
@role_required("teacher")
def save_syllabus():
    teacher = _teacher()
    course_id = request.form.get("course_id") or (request.json or {}).get("course_id")
    syllabus = request.form.get("syllabus") or (request.json or {}).get("syllabus", "")

    if not course_id:
        return jsonify({"success": False, "message": "参数不完整。"}), 400

    course = Course.query.get(course_id)
    if not course or course.teacher_id != teacher.id:
        return jsonify({"success": False, "message": "无权操作该课程。"}), 403

    course.syllabus = syllabus or ""
    db.session.commit()
    return jsonify({"success": True, "message": "大纲已保存。"})


@teacher_bp.route("/load_syllabus", methods=["POST"])
@login_required
@role_required("teacher")
def load_syllabus():
    teacher = _teacher()
    course_id = request.form.get("course_id") or (request.json or {}).get("course_id")
    if not course_id:
        return jsonify({"syllabus": ""})
    course = Course.query.get(course_id)
    if not course or course.teacher_id != teacher.id:
        return jsonify({"syllabus": ""}), 403
    return jsonify({"syllabus": course.syllabus or ""})


@teacher_bp.route("/statistics")
@login_required
@role_required("teacher")
def statistics():
    teacher = _teacher()
    course_id = request.args.get("course_id", type=int)
    if not course_id:
        return jsonify({"segments": [], "avg_grade": 0, "max_grade": 0, "min_grade": 0, "count": 0})

    course = Course.query.get(course_id)
    if not course or course.teacher_id != teacher.id:
        return jsonify({"segments": [], "avg_grade": 0, "max_grade": 0, "min_grade": 0, "count": 0}), 403

    grades = [
        float(s.grade)
        for s in CourseSelection.query.filter(
            CourseSelection.course_id == course.id,
            CourseSelection.grade.isnot(None),
        ).all()
    ]
    segments = [
        {"range": "0-59", "count": sum(0 <= g <= 59 for g in grades)},
        {"range": "60-69", "count": sum(60 <= g <= 69 for g in grades)},
        {"range": "70-79", "count": sum(70 <= g <= 79 for g in grades)},
        {"range": "80-89", "count": sum(80 <= g <= 89 for g in grades)},
        {"range": "90-100", "count": sum(90 <= g <= 100 for g in grades)},
    ]
    if grades:
        avg_grade = round(sum(grades) / len(grades), 2)
        max_grade = max(grades)
        min_grade = min(grades)
    else:
        avg_grade = max_grade = min_grade = 0
    return jsonify(
        {
            "segments": segments,
            "avg_grade": avg_grade,
            "max_grade": max_grade,
            "min_grade": min_grade,
            "count": len(grades),
        }
    )

