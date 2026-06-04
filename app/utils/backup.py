import json
from datetime import datetime
from io import BytesIO

from app.models import Course, CourseSelection, Semester, Student, Teacher, User


def _serialize_model(items, fields):
    rows = []
    for item in items:
        row = {}
        for field in fields:
            value = getattr(item, field)
            if isinstance(value, datetime):
                value = value.isoformat()
            row[field] = value
        rows.append(row)
    return rows


def build_backup_file():
    data = {
        "generated_at": datetime.now().isoformat(),
        "user": _serialize_model(User.query.all(), ["id", "username", "role", "created_at"]),
        "student": _serialize_model(
            Student.query.all(),
            ["id", "user_id", "student_no", "name", "age", "gender", "department"],
        ),
        "teacher": _serialize_model(
            Teacher.query.all(),
            ["id", "user_id", "teacher_no", "name", "department"],
        ),
        "semester": _serialize_model(
            Semester.query.all(),
            ["id", "name", "start_date", "end_date", "is_active", "created_at"],
        ),
        "course": _serialize_model(
            Course.query.all(),
            [
                "id",
                "course_no",
                "course_name",
                "credit",
                "department",
                "teacher_id",
                "semester_id",
                "course_type",
                "max_students",
                "current_students",
                "status",
            ],
        ),
        "course_selection": _serialize_model(
            CourseSelection.query.all(),
            ["id", "student_id", "course_id", "grade", "selected_at"],
        ),
    }
    output = BytesIO()
    output.write(json.dumps(data, ensure_ascii=False, indent=2, default=str).encode("utf-8"))
    output.seek(0)
    return output
