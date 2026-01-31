from flask import Blueprint, request, jsonify
from flask_login import current_user
from datetime import datetime
from utils.auth_utils import teacher_required, student_required, db
from models.classroom_models import TimetableEntry, Classroom, ClassMember

timetable_api = Blueprint("timetable_api", __name__)

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# =========================================================
# TEACHER: ADD TIMETABLE ENTRY
# =========================================================
@timetable_api.post("/teacher/timetable/add")
@teacher_required
def add_timetable():
    data = request.get_json()

    class_id = data.get("class_id")
    day = data.get("day")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    period = data.get("period")

    if not all([class_id, day, start_time, end_time, period]):
        return jsonify({"error": "All fields are required"}), 400

    start_time = datetime.strptime(start_time, "%H:%M").time()
    end_time = datetime.strptime(end_time, "%H:%M").time()
    period = int(period)

    classroom = Classroom.query.get_or_404(class_id)

    # ---- students of this class
    student_ids = [
        s.student_id for s in ClassMember.query.filter_by(class_id=class_id).all()
    ]

    # ---- all classes of those students
    other_class_ids = (
        db.session.query(ClassMember.class_id)
        .filter(ClassMember.student_id.in_(student_ids))
        .distinct()
        .all()
    )
    other_class_ids = [c[0] for c in other_class_ids]

    # ---- conflict check
    conflict = TimetableEntry.query.filter(
        TimetableEntry.class_id.in_(other_class_ids),
        TimetableEntry.day == day,
        TimetableEntry.start_time < end_time,
        TimetableEntry.end_time > start_time
    ).first()

    if conflict:
        return jsonify({
            "error": "Time slot already occupied by another class."
        }), 400

    entry = TimetableEntry(
        class_id=class_id,
        day=day,
        start_time=start_time,
        end_time=end_time,
        period=period,
        subject=classroom.subject,
        teacher_name=current_user.name
    )

    db.session.add(entry)
    db.session.commit()

    return jsonify({"message": "Timetable added successfully"}), 201


# =========================================================
# TEACHER: VIEW CLASS TIMETABLE
# =========================================================
@timetable_api.get("/teacher/timetable/<int:class_id>")
@teacher_required
def teacher_view_timetable(class_id):
    entries = TimetableEntry.query.filter_by(class_id=class_id)\
        .order_by(TimetableEntry.day, TimetableEntry.period).all()

    return jsonify([
        {
            "id": e.id,
            "day": e.day,
            "period": e.period,
            "start_time": e.start_time.strftime("%H:%M"),
            "end_time": e.end_time.strftime("%H:%M"),
            "subject": e.subject
        }
        for e in entries
    ])


# =========================================================
# TEACHER: DELETE ENTRY
# =========================================================
@timetable_api.delete("/teacher/timetable/<int:id>")
@teacher_required
def delete_timetable(id):
    entry = TimetableEntry.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Deleted successfully"})


# =========================================================
# STUDENT: GRID VIEW (PSIT STYLE)
# =========================================================
@timetable_api.get("/student/grid")
@student_required
def student_timetable_grid():
    from collections import defaultdict

    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    periods = range(1, 9)

    # student ke classes
    class_ids = (
        db.session.query(ClassMember.class_id)
        .filter_by(student_id=current_user.id)
        .all()
    )
    class_ids = [c[0] for c in class_ids]

    entries = TimetableEntry.query.filter(
        TimetableEntry.class_id.in_(class_ids)
    ).all()

    # grid structure
    grid = {
        day: {p: {"subject": None, "teacher": None} for p in periods}
        for day in days
    }

    period_times = {}

    for e in entries:
        grid[e.day][e.period] = {
            "subject": e.subject,
            "teacher": e.teacher_name
        }

        # period timing store (once is enough)
        if e.period not in period_times:
            period_times[e.period] = f"{e.start_time.strftime('%I:%M %p')} - {e.end_time.strftime('%I:%M %p')}"

    return jsonify({
        "period_times": period_times,
        "grid": grid
    })
