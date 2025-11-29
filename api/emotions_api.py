from flask import Blueprint, jsonify

emotions_api = Blueprint("emotions_api", __name__)

@emotions_api.route("/test")
def test_emotions():
    return jsonify({"message": "Emotion API working"})
