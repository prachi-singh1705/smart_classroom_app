# models/assignment_models.py
from datetime import datetime
from utils.auth_utils import db

class Assignment(db.Model):
    __tablename__ = "assignment"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject = db.Column(db.String(200), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_url = db.Column(db.String(400), nullable=True)  # optional attached file

    teacher = db.relationship("User", backref=db.backref("assignments", lazy="dynamic"))

class AssignmentSubmission(db.Model):
    __tablename__ = "assignment_submission"
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_url = db.Column(db.String(400), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(30), default="submitted")  # could be pending/reviewed etc.

    assignment = db.relationship("Assignment", backref=db.backref("submissions", lazy="dynamic"))
    student = db.relationship("User")
