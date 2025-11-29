from flask import Blueprint, request, jsonify, current_app, url_for, redirect, render_template
from utils.auth_utils import teacher_required, student_required
from utils.auth_utils import db, User
from models.classroom_models import Classroom, ClassMember, Session, SessionAttendance
from flask_login import current_user, login_required
import secrets
import string
from datetime import datetime

classes_api = Blueprint("classes_api", __name__)

def generate_class_code(length=6):
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_session_token(length=9):
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# ---------- Teacher: create class ----------
@classes_api.route("/create", methods=["POST"])
@teacher_required
def create_class():
    data = request.get_json() or {}
    class_name = data.get("class_name", "").strip()
    if not class_name:
        return jsonify({"error":"class_name required"}), 400

    # generate unique code
    for _ in range(10):
        code = generate_class_code(6)
        if not Classroom.query.filter_by(classroom_code=code).first():
            break

    c = Classroom(teacher_id=current_user.id, class_name=class_name, classroom_code=code)
    db.session.add(c)
    db.session.commit()
    return jsonify({
        "message":"created",
        "class_id": c.id,
        "class_name": c.class_name,
        "classroom_code": c.classroom_code,
        "created_at": c.created_at.isoformat()
    }), 201

# ---------- Student: join class by code ----------
@classes_api.route("/join-class", methods=["POST"])
@login_required
def join_class():
    data = request.get_json() or {}
    classroom_code = (data.get("classroom_code") or "").strip().upper()
    if not classroom_code:
        return jsonify({"error":"classroom_code required"}), 400

    classroom = Classroom.query.filter_by(classroom_code=classroom_code).first()
    if not classroom:
        return jsonify({"error":"invalid code"}), 404

    # prevent duplicate membership
    existing = ClassMember.query.filter_by(class_id=classroom.id, student_id=current_user.id).first()
    if existing:
        return jsonify({"message":"already joined", "class_id": classroom.id})

    member = ClassMember(class_id=classroom.id, student_id=current_user.id)
    db.session.add(member)
    db.session.commit()
    return jsonify({"message":"joined", "class_id":classroom.id, "joined_at": member.joined_at.isoformat()})

# ---------- Teacher: list their classrooms ----------
@classes_api.route("/teacher/list", methods=["GET"])
@teacher_required
def teacher_list():
    classes = Classroom.query.filter_by(teacher_id=current_user.id).order_by(Classroom.created_at.desc()).all()
    out = []
    for c in classes:
        out.append({
            "id": c.id,
            "class_name": c.class_name,
            "code": c.classroom_code,
            "created_at": c.created_at.isoformat(),
            "student_count": c.members.count(),
            "sessions": c.sessions.count()
        })
    return jsonify(out)

# ---------- Teacher: classroom detail ----------
@classes_api.route("/teacher/<int:class_id>/detail", methods=["GET"])
@teacher_required
def classroom_detail(class_id):
    classroom = Classroom.query.filter_by(id=class_id, teacher_id=current_user.id).first_or_404()
    members = [{
        "id": m.student.id,
        "name": m.student.name or m.student.email,
        "email": m.student.email,
        "joined_at": m.joined_at.isoformat()
    } for m in classroom.members.order_by(ClassMember.joined_at.desc()).all()]

    sessions = [{
        "id": s.id,
        "link": s.session_link,
        "created_at": s.created_at.isoformat(),
        "attendance_count": s.attendances.count()
    } for s in classroom.sessions.order_by(Session.created_at.desc()).all()]

    return jsonify({
        "class": {
            "id": classroom.id,
            "name": classroom.class_name,
            "code": classroom.classroom_code,
            "created_at": classroom.created_at.isoformat()
        },
        "members": members,
        "sessions": sessions
    })

# ---------- Teacher: generate session link ----------
@classes_api.route("/teacher/<int:class_id>/generate_session", methods=["POST"])
@teacher_required
def generate_session(class_id):
    classroom = Classroom.query.filter_by(id=class_id, teacher_id=current_user.id).first_or_404()
    # generate unique session token
    for _ in range(10):
        token = generate_session_token(9)
        link = token
        if not Session.query.filter_by(session_link=link).first():
            break

    s = Session(class_id=class_id, teacher_id=current_user.id, session_link=link)
    db.session.add(s)
    db.session.commit()

    # build full URL (if your domain set later, update accordingly)
    full_url = request.host_url.rstrip("/") + "/session/" + s.session_link
    return jsonify({
        "message":"session_created",
        "session_id": s.id,
        "session_link": full_url,
        "created_at": s.created_at.isoformat()
    }), 201

# ---------- Student: join by session link ----------
@classes_api.route("/session/<string:session_link>", methods=["GET", "POST"])
@login_required
def session_join(session_link):
    s = Session.query.filter_by(session_link=session_link).first_or_404()
    # if student, save attendance
    if current_user.is_authenticated:
        # prevent duplicate attendance
        exists = SessionAttendance.query.filter_by(session_id=s.id, student_id=current_user.id).first()
        if not exists:
            att = SessionAttendance(session_id=s.id, student_id=current_user.id)
            db.session.add(att)
            db.session.commit()
    # Redirect to a live class placeholder page (implement UI later)
    return render_template("live_session.html", session=s)
