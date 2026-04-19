from flask import Blueprint, jsonify

bp = Blueprint("ai", __name__)

@bp.route("/ai")
def ai():
    return jsonify({"message": "AI working"})