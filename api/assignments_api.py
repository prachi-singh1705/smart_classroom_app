# api/assignments_api.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from utils.auth_utils import teacher_required, student_required
from utils.auth_utils import db
from models.assignment_models import Assignment, AssignmentSubmission
from models.classroom_models import Classroom
from datetime import datetime
import os, uuid

assign_api = Blueprint("assign_api", __name__)

# get all assignments (merged) for student
@assign_api.route("/student/all", methods=["GET"])
@student_required
def student_assignments():
    # For now return all assignments — you can filter by student's classes
    assignments = Assignment.query.order_by(Assignment.due_date.desc().nullslast()).all()
    out = []
    for a in assignments:
        out.append({
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "subject": a.subject,
            "teacher_name": a.teacher.name or a.teacher.email,
            "teacher_photo": a.teacher.photo_url,
            "due_date": a.due_date.isoformat() if a.due_date else None,
            "file_url": a.file_url
        })
    return jsonify(out)

# submit assignment (student) — expects multipart/form-data (file + comment + assignment_id)
@assign_api.route("/student/submit", methods=["POST"])
@student_required
def submit_assignment():
    assignment_id = request.form.get("assignment_id")
    comment = request.form.get("comment")
    file = request.files.get("file")

    if not assignment_id:
        return jsonify({"error":"assignment_id required"}), 400

    file_url = None
    if file:
        # save file to static/uploads/assignments/
        upload_dir = os.path.join("static", "uploads", "assignments")
        os.makedirs(upload_dir, exist_ok=True)
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        file_url = "/" + filepath.replace("\\","/")

    sub = AssignmentSubmission(assignment_id=int(assignment_id), student_id=current_user.id, file_url=file_url, comment=comment, submitted_at=datetime.utcnow())
    db.session.add(sub); db.session.commit()
    return jsonify({"message":"submitted", "submission_id": sub.id})
@assign_api.post("/teacher/create")
@teacher_required
def create_assignment():
    class_id = request.form.get("class_id")
    title = request.form.get("title")
    description = request.form.get("description")
    due_date = request.form.get("due_date")

    if not class_id or not title:
        return jsonify({"error": "class_id and title required"}), 400

    # handle files
    file_urls = []
    files = request.files.getlist("file")
    os.makedirs("static/uploads/assignments", exist_ok=True)

    for f in files:
        if f.filename:
            path = f"static/uploads/assignments/{f.filename}"
            f.save(path)
            file_urls.append(path)

    assignment = Assignment(
        class_id=class_id,
        teacher_id=current_user.id,
        title=title,
        description=description,
        due_date=due_date,
        attachments=",".join(file_urls)
    )
    db.session.add(assignment)
    db.session.commit()

    return jsonify({"message": "Assignment created"}), 201
