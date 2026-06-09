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
        from xhtml2pdf import pisa
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import os
    except ImportError as exc:
        raise RuntimeError("当前环境未安装 xhtml2pdf，无法导出 PDF。") from exc

    fonts_to_try = [
        ("SimHei", "C:/Windows/Fonts/simhei.ttf"),
        ("SimSun", "C:/Windows/Fonts/simsunb.ttf"),
        ("SimFang", "C:/Windows/Fonts/simfang.ttf"),
        ("SimKai", "C:/Windows/Fonts/simkai.ttf"),
        ("SimSun-Ext", "C:/Windows/Fonts/SimsunExtG.ttf"),
    ]

    registered_font = None
    for font_name, font_path in fonts_to_try:
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            registered_font = font_name
            break

    html = render_template(
        "student/transcript_pdf.html",
        student=student,
        rows=rows,
        stats=stats,
        generated_at=datetime.now(),
        font_family=registered_font or "SimHei",
    )
    output = BytesIO()
    pisa.CreatePDF(html, dest=output)
    output.seek(0)
    return output

