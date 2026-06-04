from datetime import datetime

from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from werkzeug.security import check_password_hash, generate_password_hash

from . import db

role_enum = PgEnum("student", "teacher", "admin", name="role_enum")
gender_enum = PgEnum("男", "女", name="gender_enum")


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(role_enum, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Student(db.Model):
    __tablename__ = "student"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    student_no = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(gender_enum)
    department = db.Column(db.String(100), nullable=False)

    user = db.relationship("User", backref=db.backref("student", uselist=False))
    courses = db.relationship(
        "CourseSelection",
        backref="student",
        lazy=True,
        cascade="all, delete-orphan",
    )


class Teacher(db.Model):
    __tablename__ = "teacher"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    teacher_no = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), nullable=False)

    user = db.relationship("User", backref=db.backref("teacher", uselist=False))
    courses = db.relationship("Course", backref="teacher", lazy=True, cascade="all, delete-orphan")


class Semester(db.Model):
    __tablename__ = "semester"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    courses = db.relationship("Course", backref="semester", lazy=True)


class Course(db.Model):
    __tablename__ = "course"

    id = db.Column(db.Integer, primary_key=True)
    course_no = db.Column(db.String(20), unique=True, nullable=False, index=True)
    course_name = db.Column(db.String(100), nullable=False)
    credit = db.Column(db.DECIMAL(3, 1), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"), nullable=False)
    semester_id = db.Column(db.Integer, db.ForeignKey("semester.id"), nullable=True, index=True)
    course_type = db.Column(db.String(20), default="required", nullable=False)
    max_students = db.Column(db.Integer, default=100, nullable=False)
    current_students = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.String(20), default="open", nullable=False)

    selections = db.relationship(
        "CourseSelection",
        backref="course",
        lazy=True,
        cascade="all, delete-orphan",
    )


class CourseSelection(db.Model):
    __tablename__ = "course_selection"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    grade = db.Column(db.DECIMAL(5, 2), nullable=True)
    selected_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("student_id", "course_id", name="_student_course_uc"),
        db.Index("idx_course_selection_student_course", "student_id", "course_id"),
    )
