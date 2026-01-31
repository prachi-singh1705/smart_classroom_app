# api/live_session_api.py
from flask import Blueprint
from flask_login import current_user
from datetime import datetime

from utils.auth_utils import db, student_required, teacher_required
from models.classroom_models import LiveSession, SessionAttendance

live_session_api = Blueprint("live_session_api", __name__)


# =====================================
# STUDENT JOINS SESSION (AUTO ATTENDANCE)
# =====================================
@live_session_api.post("/join/<string:session_link>")
@student_required
def join_session(session_link):
    session = LiveSession.query.filter_by(session_link=session_link).first()

    if not session:
        return {"error": "Invalid session"}, 404

    # prevent duplicate join
    existing = SessionAttendance.query.filter_by(
        session_id=session.id,
        student_id=current_user.id
    ).first()

    if existing:
        return {"message": "Already joined"}, 200

    attendance = SessionAttendance(
        session_id=session.id,
        student_id=current_user.id,
        joined_at=datetime.utcnow()
    )

    db.session.add(attendance)
    db.session.commit()

    return {
        "message": "Attendance marked",
        "joined_at": attendance.joined_at.isoformat()
    }, 201


# =====================================
# STUDENT LEAVES SESSION
# =====================================
@live_session_api.post("/leave/<string:session_link>")
@student_required
def leave_session(session_link):
    session = LiveSession.query.filter_by(session_link=session_link).first()

    if not session:
        return {"error": "Invalid session"}, 404

    attendance = SessionAttendance.query.filter_by(
        session_id=session.id,
        student_id=current_user.id,
        left_at=None
    ).first()

    if not attendance:
        return {"error": "Attendance not found"}, 404

    attendance.left_at = datetime.utcnow()
    attendance.duration = int(
        (attendance.left_at - attendance.joined_at).total_seconds()
    )

    db.session.commit()

    return {
        "message": "Left session",
        "duration_seconds": attendance.duration
    }


# =====================================
# TEACHER ENDS SESSION
# =====================================
@live_session_api.post("/end/<string:session_link>")
@teacher_required
def end_session(session_link):
    session = LiveSession.query.filter_by(session_link=session_link).first()

    if not session:
        return {"error": "Invalid session"}, 404

    # prevent double end
    if session.ended_at:
        return {"message": "Session already ended"}, 200

    session.ended_at = datetime.utcnow()
    session.duration = int(
        (session.ended_at - session.started_at).total_seconds()
    )

    db.session.commit()

    return {
        "message": "Session ended",
        "duration_seconds": session.duration
    }
