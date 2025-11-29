from datetime import datetime
from utils.auth_utils import db

class Classroom(db.Model):
    __tablename__ = "classroom"
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_name = db.Column(db.String(200), nullable=False)
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

class SessionAttendance(db.Model):
    __tablename__ = "session_attendance"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    session = db.relationship("Session", backref=db.backref("attendances", lazy="dynamic"))
    student = db.relationship("User")
