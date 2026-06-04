from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.models import User

auth_bp = Blueprint("auth", __name__)


def _role_home(role: str) -> str:
    if role == "student":
        return "student.dashboard"
    if role == "teacher":
        return "teacher.dashboard"
    return "admin.dashboard"


@auth_bp.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for(_role_home(current_user.role)))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(_role_home(current_user.role)))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "").strip()

        if not username or not password or role not in {"student", "teacher", "admin"}:
            flash("请填写完整登录信息。", "danger")
            return render_template("auth/login.html")

        user = User.query.filter_by(username=username, role=role).first()
        if not user or not user.check_password(password):
            flash("用户名或密码错误。", "danger")
            return render_template("auth/login.html")

        login_user(user)
        return redirect(url_for(_role_home(role)))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

