from flask import Blueprint, jsonify

dashboard_api = Blueprint("dashboard_api", __name__)

@dashboard_api.route("/stats")
def get_stats():
    return jsonify({"present": 0, "attention": 0})
