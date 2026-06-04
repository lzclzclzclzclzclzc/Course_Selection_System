-- Run this after the application tables have been created.
-- It implements the database trigger and stored procedure required by the project.

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
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sync_course_current_students ON course_selection;

CREATE TRIGGER trg_sync_course_current_students
AFTER INSERT OR UPDATE OR DELETE ON course_selection
FOR EACH ROW EXECUTE PROCEDURE sync_course_current_students_func();

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
$$ LANGUAGE plpgsql;
