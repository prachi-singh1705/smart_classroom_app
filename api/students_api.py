from flask import Blueprint, jsonify

students_api = Blueprint("students_api", __name__)

@students_api.route("/all")
def get_students():
    return jsonify({"message": "Students API working"})
