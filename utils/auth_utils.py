from flask import request, render_template, redirect, url_for, flash, current_app
from flask_login import UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from functools import wraps

db = SQLAlchemy()
login_manager = LoginManager()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="student")  # 'student' or 'teacher'
    name = db.Column(db.String(120), nullable=True)

    def is_teacher(self):
        return self.role == "teacher"

    def is_student(self):
        return self.role == "student"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---- Decorators for role based access ----
def teacher_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_teacher():
            flash("Access denied: Teacher only area.", "danger")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped

def student_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_student():
            flash("Access denied: Student only area.", "danger")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped


# ---- Login handler: performs role-based redirect ----
def login_user_fn():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            # Role-based redirect
            if user.role == "teacher":
                return redirect(url_for("teacher_dashboard"))
            else:
                return redirect(url_for("student_dashboard"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")


def logout_user_fn():
    logout_user()
    return redirect(url_for("login"))


# ---- Registration handler ----
def register_user_fn():
    if request.method == "POST":
        name = request.form.get("name") or None
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role", "student").lower()
        if role not in ("student", "teacher"):
            role = "student"

        # Basic validation
        if not email or not password:
            flash("Please provide email and password", "danger")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for("login"))

        hashed = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed, role=role)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")
