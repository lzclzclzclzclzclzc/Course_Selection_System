from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("student", "teacher", "admin"), nullable=False, index=True)
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
    gender = db.Column(db.Enum("男", "女"))
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


class Course(db.Model):
    __tablename__ = "course"

    id = db.Column(db.Integer, primary_key=True)
    course_no = db.Column(db.String(20), unique=True, nullable=False, index=True)
    course_name = db.Column(db.String(100), nullable=False)
    credit = db.Column(db.DECIMAL(3, 1), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"), nullable=False)
    max_students = db.Column(db.Integer, default=100, nullable=False)

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
