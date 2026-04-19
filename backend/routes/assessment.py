from flask import Blueprint

assessment_bp = Blueprint("assessment", __name__)

@assessment_bp.route("/")
def test():
    return "assessment ok"