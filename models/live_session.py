from datetime import datetime
from utils.auth_utils import db   # ✅ FIXED IMPORT


class LiveSession(db.Model):
    __tablename__ = "live_sessions"

    id = db.Column(db.Integer, primary_key=True)

    class_id = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, nullable=False)

    session_link = db.Column(db.String(255), unique=True, nullable=False)

    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)

    duration = db.Column(db.Integer, nullable=True)  # seconds

    attendances = db.relationship(
        "SessionAttendance",
        backref="session",
        cascade="all, delete-orphan"
    )

    def end_session(self):
        self.ended_at = datetime.utcnow()
        self.duration = int((self.ended_at - self.started_at).total_seconds())


class SessionAttendance(db.Model):
    __tablename__ = "session_attendance"

    id = db.Column(db.Integer, primary_key=True)

    session_id = db.Column(
        db.Integer,
        db.ForeignKey("live_sessions.id"),
        nullable=False
    )

    student_id = db.Column(db.Integer, nullable=False)

    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    left_at = db.Column(db.DateTime, nullable=True)

    duration = db.Column(db.Integer, nullable=True)  # seconds

    def leave(self):
        self.left_at = datetime.utcnow()
        self.duration = int((self.left_at - self.joined_at).total_seconds())
