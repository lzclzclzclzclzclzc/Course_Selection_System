import os
import random
import sys
from urllib.parse import quote_plus

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime


def _patch_opengauss_version():
    try:
        from sqlalchemy.dialects.postgresql.base import PGDialect
        original_get_server_version_info = PGDialect._get_server_version_info

        def patched_get_server_version_info(self, connection):
            try:
                return original_get_server_version_info(self, connection)
            except AssertionError:
                return (14, 0, 0)

        PGDialect._get_server_version_info = patched_get_server_version_info
    except ImportError:
        pass


_patch_opengauss_version()


app = Flask(__name__)

db_user = os.getenv('DB_USER', 'gaussdb')
db_password = quote_plus(os.getenv('DB_PASSWORD', 'Enmo@123'))
db_host = os.getenv('DB_HOST', 'opengauss')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME', 'student_course_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

role_enum = PgEnum("student", "teacher", "admin", name="role_enum")
gender_enum = PgEnum("男", "女", name="gender_enum")


class User(db.Model):
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


class Teacher(db.Model):
    __tablename__ = "teacher"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    teacher_no = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), nullable=False)

    user = db.relationship("User", backref=db.backref("teacher", uselist=False))


class Course(db.Model):
    __tablename__ = "course"

    id = db.Column(db.Integer, primary_key=True)
    course_no = db.Column(db.String(20), unique=True, nullable=False, index=True)
    course_name = db.Column(db.String(100), nullable=False)
    credit = db.Column(db.DECIMAL(3, 1), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"), nullable=False)
    max_students = db.Column(db.Integer, default=100, nullable=False)

    teacher = db.relationship("Teacher", backref=db.backref("courses", lazy=True))


class CourseSelection(db.Model):
    __tablename__ = "course_selection"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    grade = db.Column(db.DECIMAL(5, 2), nullable=True)
    selected_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    student = db.relationship("Student", backref=db.backref("selections", lazy=True))
    course = db.relationship("Course", backref=db.backref("selections", lazy=True))

    __table_args__ = (
        db.UniqueConstraint("student_id", "course_id", name="_student_course_uc"),
    )


def seed_demo():
    with app.app_context():
        db.create_all()

        if User.query.filter_by(username="admin").first():
            print("Demo data already exists. Skip.")
            return

        admin = User(username="admin", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)

        student_users = []
        teacher_users = []

        for i in range(1, 21):
            username = f"20240{i:03d}"
            user = User(username=username, role="student")
            user.set_password("123456")
            db.session.add(user)
            student_users.append(user)

        for i in range(1, 6):
            username = f"T{i:04d}"
            user = User(username=username, role="teacher")
            user.set_password("123456")
            db.session.add(user)
            teacher_users.append(user)

        db.session.flush()

        student_profiles = []
        for i, user in enumerate(student_users, start=1):
            profile = Student(
                user_id=user.id,
                student_no=user.username,
                name=f"Student{i}",
                age=random.randint(18, 23),
                gender=random.choice(["男", "女"]),
                department=random.choice(["计算机系", "软件工程系"]),
            )
            student_profiles.append(profile)
        db.session.add_all(student_profiles)

        teacher_profiles = []
        for i, user in enumerate(teacher_users, start=1):
            profile = Teacher(
                user_id=user.id,
                teacher_no=user.username,
                name=f"Teacher{i}",
                department="计算机系",
            )
            teacher_profiles.append(profile)
        db.session.add_all(teacher_profiles)
        db.session.flush()

        course_specs = [
            ("CS101", "程序设计基础", 3.0),
            ("CS102", "数据结构", 3.5),
            ("CS201", "数据库原理", 3.5),
            ("CS202", "操作系统", 4.0),
            ("CS301", "计算机网络", 3.0),
            ("CS302", "编译原理", 4.0),
            ("CS303", "人工智能导论", 2.5),
        ]
        course_objects = []
        for course_no, course_name, credit in course_specs:
            course = Course(
                course_no=course_no,
                course_name=course_name,
                credit=credit,
                department="计算机系",
                teacher_id=random.choice(teacher_profiles).id,
                max_students=random.randint(50, 100),
            )
            course_objects.append(course)
        db.session.add_all(course_objects)
        db.session.flush()

        selection_objects = []
        for student in student_profiles:
            select_count = random.randint(2, min(5, len(course_objects)))
            selected_courses = random.sample(course_objects, k=select_count)
            for course in selected_courses:
                selection_objects.append(
                    CourseSelection(
                        student_id=student.id,
                        course_id=course.id,
                        grade=round(random.uniform(55, 100), 2),
                    )
                )
        db.session.add_all(selection_objects)

        db.session.commit()

        print("Demo data created.")
        print("Admin: admin / admin123")
        print("Students: 2024001-20240020 / 123456")
        print("Teachers: T0001-T0005 / 123456")
        print(f"Course selections: {len(selection_objects)} records")


if __name__ == "__main__":
    seed_demo()
