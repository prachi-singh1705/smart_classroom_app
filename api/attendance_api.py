from flask import Blueprint, jsonify

attendance_api = Blueprint("attendance_api", __name__)

@attendance_api.route("/status")
def attendance_status():
    return jsonify({"message": "Attendance API working"})
