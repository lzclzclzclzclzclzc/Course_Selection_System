import logging

from flask import Flask, flash, redirect, session, url_for
from flask_login import LoginManager, current_user

from config import Config

from .models import Course, Student, Teacher, User, db

import random

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "请先登录。"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def _register_cli(app: Flask):
    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        print("数据库表创建完成。")

    @app.cli.command("seed-demo")
    def seed_demo():
        db.create_all()
        if User.query.filter_by(username="admin").first():
            print("示例数据已存在，跳过。")
            return

        admin = User(username="admin", role="admin")
        admin.set_password("admin123")

        stu_user = User(username="20240001", role="student")
        stu_user.set_password("123456")
        tea_user = User(username="T0001", role="teacher")
        tea_user.set_password("123456")

        db.session.add_all([admin, stu_user, tea_user])
        db.session.flush()

        student = Student(
            user_id=stu_user.id,
            student_no="20240001",
            name="张三",
            age=20,
            gender="男",
            department="计算机系",
        )
        teacher = Teacher(
            user_id=tea_user.id,
            teacher_no="T0001",
            name="李老师",
            department="计算机系",
        )
        db.session.add_all([student, teacher])
        db.session.flush()

        db.session.add_all(
            [
                Course(
                    course_no="CS101",
                    course_name="程序设计基础",
                    credit=3.0,
                    department="计算机系",
                    teacher_id=teacher.id,
                    max_students=80,
                ),
                Course(
                    course_no="CS201",
                    course_name="数据库原理",
                    credit=3.5,
                    department="计算机系",
                    teacher_id=teacher.id,
                    max_students=60,
                ),
            ]
        )
        db.session.commit()
        print("示例数据创建完成：admin/admin123，学生20240001/123456，教师T0001/123456。")




def create_app(config_class=Config):
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
        flash("请先登录。", "danger")
        return redirect(url_for("auth.login"))

    @app.errorhandler(403)
    def forbidden(_):
        flash("你没有权限访问该页面。", "danger")
        return redirect(url_for("dashboard_redirect"))

    return app
