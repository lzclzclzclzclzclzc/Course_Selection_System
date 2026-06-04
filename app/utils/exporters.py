from datetime import datetime
from io import BytesIO
from typing import Iterable

import pandas as pd
from flask import render_template


def build_transcript_rows(selections: Iterable):
    rows = []
    total_credit = 0.0
    total_grade = 0.0

    for selection in selections:
        grade = float(selection.grade)
        credit = float(selection.course.credit)
        rows.append(
            {
                "course_no": selection.course.course_no,
                "course_name": selection.course.course_name,
                "grade": grade,
                "credit": credit,
                "teacher": selection.course.teacher.name,
            }
        )
        total_credit += credit
        total_grade += grade

    course_count = len(rows)
    avg_grade = round(total_grade / course_count, 2) if course_count else 0
    return rows, {"course_count": course_count, "total_credit": total_credit, "avg_grade": avg_grade}


def export_transcript_excel(student, rows):
    output = BytesIO()
    data = [
        {
            "学号": student.student_no,
            "姓名": student.name,
            "课程号": row["course_no"],
            "课程名": row["course_name"],
            "成绩": row["grade"],
            "学分": row["credit"],
            "任课教师": row["teacher"],
        }
        for row in rows
    ]
    df = pd.DataFrame(data)
    if df.empty:
        df = pd.DataFrame([{"提示": "暂无已修课程成绩"}])
    df.to_excel(output, index=False)
    output.seek(0)
    return output


def export_transcript_pdf(student, rows, stats):
    try:
        from weasyprint import HTML
    except Exception as exc:
        raise RuntimeError("当前环境未安装或无法加载 WeasyPrint，无法导出 PDF。") from exc

    html = render_template(
        "student/transcript_pdf.html",
        student=student,
        rows=rows,
        stats=stats,
        generated_at=datetime.now(),
    )
    pdf_bytes = HTML(string=html).write_pdf()
    return BytesIO(pdf_bytes)

