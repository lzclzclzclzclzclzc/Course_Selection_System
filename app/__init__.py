import logging
import random

from flask import Flask, flash, redirect, session, url_for
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please login first."


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


@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))


def _register_cli(app: Flask):
    @app.cli.command("init-db")
    def init_db():
        from .models import Course, CourseSelection, Semester, Student, Teacher, User
        from .utils.db_objects import ensure_academic_schema

        ensure_academic_schema()
        print("Database tables created.")

    @app.cli.command("seed-demo")
    def seed_demo():
        from .models import Course, CourseSelection, Semester, Student, Teacher, User
        from .utils.db_objects import ensure_academic_schema
        
        ensure_academic_schema()

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
        print("Students: 20240001-20240020 / 123456")
        print("Teachers: T0001-T0005 / 123456")
        print(f"Course selections: {len(selection_objects)} records")


def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    db.init_app(app)
    login_manager.init_app(app)

    from .routes.admin import admin_bp
    from .routes.auth import auth_bp
    from .routes.student import student_bp
    from .routes.teacher import teacher_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(admin_bp)

    _register_cli(app)

    with app.app_context():
        try:
            from .utils.db_objects import ensure_academic_schema

            ensure_academic_schema()
        except Exception:
            app.logger.exception("Failed to ensure academic database schema.")

    @app.context_processor
    def inject_role():
        role = current_user.role if current_user.is_authenticated else None
        return {"current_role": role}

    @app.route("/dashboard")
    def dashboard_redirect():
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if current_user.role == "student":
            return redirect(url_for("student.dashboard"))
        if current_user.role == "teacher":
            return redirect(url_for("teacher.dashboard"))
        return redirect(url_for("admin.dashboard"))

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    @app.errorhandler(401)
    def unauthorized(_):
        flash("Please login first.", "danger")
        return redirect(url_for("auth.login"))

    @app.errorhandler(403)
    def forbidden(_):
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("dashboard_redirect"))

    return app
