# api/classes_api.py
from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from utils.auth_utils import teacher_required, student_required, db

from models.classroom_models import (
    Classroom,
    ClassMember,
    TimetableEntry,
    LiveSession,          # ✅ use ONLY LiveSession
    SessionAttendance     # ✅ attendance for LiveSession
)

import secrets
import string

classes_api = Blueprint("classes_api", __name__)

# -------------------------
# HELPERS
# -------------------------
def generate_class_code(length=6):
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_session_token():
    return secrets.token_urlsafe(6)

# -------------------------
# CREATE CLASS (TEACHER)
# -------------------------
@classes_api.post("/create")
@teacher_required
def create_class():
    data = request.get_json() or {}
    class_name = data.get("class_name", "").strip()
    subject = data.get("subject", "").strip()

    if not class_name:
        return {"error": "class_name required"}, 400

    code = generate_class_code()
    classroom = Classroom(
        teacher_id=current_user.id,
        class_name=class_name,
        subject=subject,
        classroom_code=code
    )

    db.session.add(classroom)
    db.session.commit()

    return {
        "message": "created",
        "class_id": classroom.id,
        "classroom_code": classroom.classroom_code
    }, 201

# -------------------------
# STUDENT JOIN CLASS
# -------------------------
@classes_api.post("/join-class")
@login_required
def join_class():
    code = (request.json or {}).get("classroom_code", "").upper()
    classroom = Classroom.query.filter_by(classroom_code=code).first()

    if not classroom:
        return {"error": "Invalid code"}, 404

    exists = ClassMember.query.filter_by(
        class_id=classroom.id,
        student_id=current_user.id
    ).first()

    if exists:
        return {"message": "already joined"}

    member = ClassMember(
        class_id=classroom.id,
        student_id=current_user.id
    )
    db.session.add(member)
    db.session.commit()

    return {"message": "joined", "class_id": classroom.id}

# -------------------------
# TEACHER CLASS LIST
# -------------------------
@classes_api.get("/teacher/list")
@teacher_required
def teacher_classes():
    classes = Classroom.query.filter_by(
        teacher_id=current_user.id
    ).all()

    return [
        {
            "id": c.id,
            "class_name": c.class_name,
            "subject": c.subject,
            "code": c.classroom_code,
            "student_count": c.members.count()
        }
        for c in classes
    ]

# -------------------------
# GENERATE LIVE SESSION (PHASE-1)
# -------------------------
@classes_api.post("/teacher/<int:class_id>/generate_session")
@teacher_required
def generate_live_session(class_id):
    classroom = Classroom.query.filter_by(
        id=class_id,
        teacher_id=current_user.id
    ).first_or_404()

    token = generate_session_token()

    session = LiveSession(
        class_id=classroom.id,
        teacher_id=current_user.id,
        session_link=token
    )

    db.session.add(session)
    db.session.commit()

    # ✅ FULL ABSOLUTE URL (THIS IS THE FIX)
    full_url = f"{request.scheme}://{request.host}/session/{token}"

    return {
        "message": "Live session created",
        "session_id": session.id,
        "session_token": token,
        "session_link": full_url
    }, 201


# -------------------------
# STUDENT JOINED CLASSES
# -------------------------
@classes_api.get("/student/joined")
@student_required
def student_joined_classes():

    memberships = ClassMember.query.filter_by(
        student_id=current_user.id
    ).all()

    if not memberships:
        return []

    class_ids = [m.class_id for m in memberships]

    classes = Classroom.query.filter(
        Classroom.id.in_(class_ids)
    ).all()

    result = []

    for c in classes:
        teacher = c.teacher  # requires relationship in model

        result.append({
            "class_id": c.id,
            "class_name": c.class_name,
            "subject": c.subject,
            "code": c.classroom_code,
            "teacher_name": teacher.name if teacher else "Unknown",
            "teacher_photo": teacher.photo_url if teacher else None
        })

    return result
