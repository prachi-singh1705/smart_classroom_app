# ===============================
# app.py (FINAL FULL VERSION)
# ===============================

from flask import Flask, render_template, redirect, url_for
from config import Config
import os

# Ensure all models are registered
import models.classroom_models

# Auth + User
from utils.auth_utils import (
    db, login_manager,
    login_user_fn, logout_user_fn, register_user_fn,
    teacher_required, student_required
)

# API Blueprints
from api.students_api import students_api
from api.attendance_api import attendance_api
from api.dashboard_api import dashboard_api
from api.emotions_api import emotions_api
from api.classes_api import classes_api   # 👈 NEW (Classrooms + Sessions)

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Ensure instance folder exists
    os.makedirs("instance", exist_ok=True)

    # Init DB + Login manager
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"

    # Register all API blueprints
    app.register_blueprint(students_api, url_prefix="/api/students")
    app.register_blueprint(attendance_api, url_prefix="/api/attendance")
    app.register_blueprint(dashboard_api, url_prefix="/api/dashboard")
    app.register_blueprint(emotions_api, url_prefix="/api/emotions")
    app.register_blueprint(classes_api, url_prefix="/api/classes")  # 👈 NEW

    # -----------------------------
    # MAIN ROUTES
    # -----------------------------

    @app.route("/")
    def home():
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        return login_user_fn()

    @app.route("/register", methods=["GET", "POST"])
    def register():
        return register_user_fn()

    @app.route("/logout")
    def logout():
        return logout_user_fn()

    # Role-based smart redirect
    @app.route("/dashboard")
    def dashboard():
        from flask_login import current_user
        if current_user.is_authenticated:
            if current_user.role == "teacher":
                return redirect(url_for("teacher_dashboard"))
            else:
                return redirect(url_for("student_dashboard"))
        return redirect(url_for("login"))

    # -----------------------------
    # TEACHER DASHBOARD
    # -----------------------------

    @app.route("/teacher/dashboard")
    @teacher_required
    def teacher_dashboard():
        return render_template("teacher_dashboard.html")

    @app.route("/teacher/classes")
    @teacher_required
    def teacher_classes_page():
        return render_template("teacher_classes.html")

    @app.route("/teacher/classroom/<int:class_id>")
    @teacher_required
    def teacher_classroom_detail_page(class_id):
        return render_template("teacher_classroom_detail.html")

    # -----------------------------
    # STUDENT DASHBOARD
    # -----------------------------

    @app.route("/student/dashboard")
    @student_required
    def student_dashboard():
        return render_template("student_dashboard.html")

    @app.route("/join-class")
    @student_required
    def join_class_page():
        return render_template("join_class.html")

    # -----------------------------
    # ATTENDANCE AND REPORTS
    # -----------------------------

    @app.route("/take_attendance")
    @teacher_required
    def take_attendance():
        return render_template("take_attendance.html")

    @app.route("/reports")
    def reports():
        return render_template("reports.html")

    # -----------------------------
    # LIVE SESSION VIEW (STUDENT/T)
    # -----------------------------

    @app.route("/session/<string:session_link>")
    def live_session_page(session_link):
        # Render placeholder (API handles attendance)
        return render_template("live_session.html", session_link=session_link)

    # Initialize DB tables
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
