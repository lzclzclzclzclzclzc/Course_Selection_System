from flask import Blueprint, flash, jsonify, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

from app.models import Course, CourseSelection, db
from app.utils.auth import role_required
from app.utils.exporters import build_transcript_rows, export_transcript_excel, export_transcript_pdf

student_bp = Blueprint("student", __name__, url_prefix="/student")


def _current_student():
    return current_user.student


@student_bp.route("")
@login_required
@role_required("student")
def dashboard():
    student = _current_student()
    selected = CourseSelection.query.filter_by(student_id=student.id).all()
    selected_course_ids = {s.course_id for s in selected}

    available_courses = Course.query.filter(~Course.id.in_(selected_course_ids)).all() if selected_course_ids else Course.query.all()
    completed = [s for s in selected if s.grade is not None]

    return render_template(
        "student/dashboard.html",
        student=student,
        available_courses=available_courses,
        selected_courses=selected,
        completed_courses=completed,
    )


@student_bp.route("/select_course", methods=["POST"])
@login_required
@role_required("student")
def select_course():
    student = _current_student()
    course_id = request.form.get("course_id") or (request.json or {}).get("course_id")
    if not course_id:
        return jsonify({"success": False, "message": "缺少课程ID。"}), 400

    course = Course.query.get(course_id)
    if not course:
        return jsonify({"success": False, "message": "课程不存在。"}), 404

    exists = CourseSelection.query.filter_by(student_id=student.id, course_id=course.id).first()
    if exists:
        return jsonify({"success": False, "message": "你已经选择了该课程。"}), 400

    selected_count = CourseSelection.query.filter_by(course_id=course.id).count()
    if selected_count >= course.max_students:
        return jsonify({"success": False, "message": "课程人数已满。"}), 400

    db.session.add(CourseSelection(student_id=student.id, course_id=course.id))
    db.session.commit()
    return jsonify({"success": True, "message": "选课成功。"})


@student_bp.route("/drop_course", methods=["POST"])
@login_required
@role_required("student")
def drop_course():
    student = _current_student()
    course_id = request.form.get("course_id") or (request.json or {}).get("course_id")
    if not course_id:
        return jsonify({"success": False, "message": "缺少课程ID。"}), 400

    selection = CourseSelection.query.filter_by(student_id=student.id, course_id=course_id).first()
    if not selection:
        return jsonify({"success": False, "message": "你未选择该课程。"}), 400

    db.session.delete(selection)
    db.session.commit()
    return jsonify({"success": True, "message": "退课成功。"})


@student_bp.route("/transcript")
@login_required
@role_required("student")
def transcript():
    student = _current_student()
    completed = (
        CourseSelection.query.filter(
            CourseSelection.student_id == student.id,
            CourseSelection.grade.isnot(None),
        )
        .order_by(CourseSelection.selected_at.desc())
        .all()
    )
    rows, stats = build_transcript_rows(completed)
    return render_template("student/transcript.html", student=student, rows=rows, stats=stats)


@student_bp.route("/transcript/excel")
@login_required
@role_required("student")
def transcript_excel():
    student = _current_student()
    completed = CourseSelection.query.filter(
        CourseSelection.student_id == student.id,
        CourseSelection.grade.isnot(None),
    ).all()
    rows, _ = build_transcript_rows(completed)
    output = export_transcript_excel(student, rows)
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"{student.student_no}_transcript.xlsx",
    )


@student_bp.route("/transcript/pdf")
@login_required
@role_required("student")
def transcript_pdf():
    student = _current_student()
    completed = CourseSelection.query.filter(
        CourseSelection.student_id == student.id,
        CourseSelection.grade.isnot(None),
    ).all()
    rows, stats = build_transcript_rows(completed)
    try:
        output = export_transcript_pdf(student, rows, stats)
    except RuntimeError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("student.transcript"))
    return send_file(output, mimetype="application/pdf", as_attachment=True, download_name=f"{student.student_no}_transcript.pdf")
