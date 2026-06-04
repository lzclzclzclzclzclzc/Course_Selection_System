from datetime import date

from sqlalchemy import text

from app import db
from app.models import Course, CourseSelection, Semester


def ensure_academic_schema():
    _ensure_semester_table()

    if _table_exists("course"):
        column_sql = {
            "semester_id": "ALTER TABLE course ADD COLUMN IF NOT EXISTS semester_id INTEGER",
            "course_type": "ALTER TABLE course ADD COLUMN IF NOT EXISTS course_type VARCHAR(20) DEFAULT 'required' NOT NULL",
            "current_students": "ALTER TABLE course ADD COLUMN IF NOT EXISTS current_students INTEGER DEFAULT 0 NOT NULL",
            "status": "ALTER TABLE course ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'open' NOT NULL",
        }
        for column, ddl in column_sql.items():
            if not _column_exists("course", column):
                db.session.execute(text(ddl))
        db.session.commit()

        _ensure_default_semester()
        _sync_course_plan_defaults()

        if db.engine.dialect.name == "postgresql":
            _ensure_opengauss_objects()


def _table_exists(table_name):
    return bool(
        db.session.execute(
            text(
                """
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = :table_name
                """
            ),
            {"table_name": table_name},
        ).first()
    )


def _column_exists(table_name, column_name):
    return bool(
        db.session.execute(
            text(
                """
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = :table_name
                  AND column_name = :column_name
                """
            ),
            {"table_name": table_name, "column_name": column_name},
        ).first()
    )


def _ensure_semester_table():
    db.session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS semester (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE,
                start_date DATE,
                end_date DATE,
                is_active BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )
    db.session.commit()


def _ensure_default_semester():
    if Semester.query.first():
        return

    db.session.add(
        Semester(
            name="2025-2026 Spring",
            start_date=date(2026, 2, 24),
            end_date=date(2026, 7, 5),
            is_active=True,
        )
    )
    db.session.commit()


def _sync_course_plan_defaults():
    active_semester = Semester.query.filter_by(is_active=True).first() or Semester.query.first()
    for course in Course.query.all():
        if active_semester and course.semester_id is None:
            course.semester_id = active_semester.id
        if not course.course_type:
            course.course_type = "required"
        if not course.status:
            course.status = "open"
        course.current_students = CourseSelection.query.filter_by(course_id=course.id).count()
    db.session.commit()


def _ensure_opengauss_objects():
    statements = [
        """
        CREATE OR REPLACE FUNCTION sync_course_current_students_func()
        RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                UPDATE course
                SET current_students = (
                    SELECT COUNT(*) FROM course_selection WHERE course_id = NEW.course_id
                )
                WHERE id = NEW.course_id;
                RETURN NEW;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE course
                SET current_students = (
                    SELECT COUNT(*) FROM course_selection WHERE course_id = OLD.course_id
                )
                WHERE id = OLD.course_id;
                RETURN OLD;
            ELSIF TG_OP = 'UPDATE' THEN
                UPDATE course
                SET current_students = (
                    SELECT COUNT(*) FROM course_selection WHERE course_id = OLD.course_id
                )
                WHERE id = OLD.course_id;
                UPDATE course
                SET current_students = (
                    SELECT COUNT(*) FROM course_selection WHERE course_id = NEW.course_id
                )
                WHERE id = NEW.course_id;
                RETURN NEW;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql
        """,
        "DROP TRIGGER IF EXISTS trg_sync_course_current_students ON course_selection",
        """
        CREATE TRIGGER trg_sync_course_current_students
        AFTER INSERT OR UPDATE OR DELETE ON course_selection
        FOR EACH ROW EXECUTE PROCEDURE sync_course_current_students_func()
        """,
        """
        CREATE OR REPLACE PROCEDURE calculate_student_average_grade(
            IN p_student_id INTEGER,
            OUT p_avg_grade NUMERIC,
            OUT p_total_credit NUMERIC
        )
        AS $$
        BEGIN
            SELECT
                COALESCE(ROUND(SUM(cs.grade * c.credit) / NULLIF(SUM(c.credit), 0), 2), 0),
                COALESCE(SUM(c.credit), 0)
            INTO p_avg_grade, p_total_credit
            FROM course_selection cs
            JOIN course c ON c.id = cs.course_id
            WHERE cs.student_id = p_student_id
              AND cs.grade IS NOT NULL;
        END;
        $$ LANGUAGE plpgsql
        """,
    ]
    for statement in statements:
        db.session.execute(text(statement))
    db.session.commit()
