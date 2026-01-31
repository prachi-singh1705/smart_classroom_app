# models/classroom_models.py
from datetime import datetime
from utils.auth_utils import db

class Classroom(db.Model):
    __tablename__ = "classroom"
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_name = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(200), nullable=True)
    classroom_code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    teacher = db.relationship("User", backref=db.backref("classrooms", lazy="dynamic"))


class ClassMember(db.Model):
    __tablename__ = "class_member"
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    classroom = db.relationship("Classroom", backref=db.backref("members", lazy="dynamic"))
    student = db.relationship("User", backref=db.backref("classes_joined", lazy="dynamic"))


class Session(db.Model):
    __tablename__ = "session"
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_link = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    classroom = db.relationship("Classroom", backref=db.backref("sessions", lazy="dynamic"))
    teacher = db.relationship("User")


class TimetableEntry(db.Model):
    __tablename__ = "timetable_entry"

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey("classroom.id"), nullable=False)

    day = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    period = db.Column(db.Integer, nullable=False)

    subject = db.Column(db.String(100), nullable=False)
    teacher_name = db.Column(db.String(100), nullable=False)

# ===============================
# LIVE SESSION MODELS (PHASE-1)
# ===============================

class LiveSession(db.Model):
    __tablename__ = "live_sessions"

    id = db.Column(db.Integer, primary_key=True)

    class_id = db.Column(db.Integer, db.ForeignKey("classroom.id"), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

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

    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    left_at = db.Column(db.DateTime, nullable=True)

    duration = db.Column(db.Integer, nullable=True)

    def leave(self):
        self.left_at = datetime.utcnow()
        self.duration = int((self.left_at - self.joined_at).total_seconds())
