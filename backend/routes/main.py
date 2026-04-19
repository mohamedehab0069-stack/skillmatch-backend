from flask import Blueprint

bp = Blueprint("main", __name__)

@bp.route("/")
def home():
    return "Server is running 🚀"

@bp.route("/test")
def test():
    return "TEST OK"