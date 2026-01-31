# ===============================
# app.py (FINAL – CLEAN & CORRECT)
# ===============================

from flask import Flask, render_template, redirect, url_for
from config import Config
import os

# -----------------------------
# DATABASE + LOGIN
# -----------------------------
from utils.auth_utils import (
    db, login_manager,
    login_user_fn, logout_user_fn, register_user_fn,
    teacher_required, student_required
)

# -----------------------------
# REGISTER MODELS (ONCE)
# -----------------------------
import models.classroom_models

# -----------------------------
# API BLUEPRINTS
# -----------------------------
from api.timetable_api import timetable_api
from api.assignments_api import assign_api
from api.students_api import students_api
from api.attendance_api import attendance_api
from api.dashboard_api import dashboard_api
from api.emotions_api import emotions_api
from api.classes_api import classes_api
from api.live_session_api import live_session_api


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    os.makedirs("instance", exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"

    # -----------------------------
    # REGISTER BLUEPRINTS
    # -----------------------------
    app.register_blueprint(assign_api, url_prefix="/api/assignments")
    app.register_blueprint(students_api, url_prefix="/api/students")
    app.register_blueprint(attendance_api, url_prefix="/api/attendance")
    app.register_blueprint(dashboard_api, url_prefix="/api/dashboard")
    app.register_blueprint(emotions_api, url_prefix="/api/emotions")
    app.register_blueprint(classes_api, url_prefix="/api/classes")
    app.register_blueprint(timetable_api, url_prefix="/api/timetable")
    app.register_blueprint(live_session_api, url_prefix="/api/session")

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

    # -----------------------------
    # DASHBOARD REDIRECT
    # -----------------------------
    @app.route("/dashboard")
    def dashboard():
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(
                url_for("teacher_dashboard")
                if current_user.role == "teacher"
                else url_for("student_dashboard")
            )
        return redirect(url_for("login"))

    # -----------------------------
    # TEACHER ROUTES
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
        return render_template("teacher_classroom_detail.html", class_id=class_id)

    # -----------------------------
    # STUDENT ROUTES
    # -----------------------------
    @app.route("/student/dashboard")
    @student_required
    def student_dashboard():
        return render_template("student_dashboard.html")

    @app.route("/join-class")
    @student_required
    def join_class_page():
        return render_template("join_class.html")

    @app.route("/join-session")
    @student_required
    def join_session_page():
        return render_template("join_session.html")

    @app.route("/student/class/<int:class_id>")
    @student_required
    def student_class_detail(class_id):
        return render_template("student_class_detail.html", class_id=class_id)

    @app.route("/timetable")
    @student_required
    def timetable_page():
        return render_template("timetable.html")

    @app.route("/assignments")
    @student_required
    def assignments_page():
        return render_template("assignments.html")

    # -----------------------------
    # LIVE SESSION VIEW
    # -----------------------------
    @app.route("/session/<string:session_link>")
    def live_session_page(session_link):
        from models.classroom_models import LiveSession, Classroom

        session_obj = LiveSession.query.filter_by(session_link=session_link).first()
        if not session_obj:
            return "Invalid session link", 404

        classroom = Classroom.query.get(session_obj.class_id)

        return render_template(
            "live_session.html",
            session_obj=session_obj,
            classroom=classroom
        )


    # -----------------------------
    # CREATE TABLES
    # -----------------------------
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
