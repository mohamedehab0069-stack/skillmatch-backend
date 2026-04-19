from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.student import StudentProfile
from backend.models.task import PortfolioItem
from backend.utils.responses import success, error
from backend.utils.decorators import student_required

portfolio_bp = Blueprint("portfolio", __name__, url_prefix="/api/portfolio")


@portfolio_bp.route("/", methods=["GET"])
@jwt_required()
@student_required
def get_portfolio():
    user_id = int(get_jwt_identity())
    student = StudentProfile.get_by_user(user_id)
    if not student:
        return error("Student profile not found.", 404)
    items = PortfolioItem.get_by_student(student["id"])
    return success({"items": items, "total": len(items)})


@portfolio_bp.route("/public/<int:student_id>", methods=["GET"])
def get_public_portfolio(student_id):
    """Public endpoint — no auth required. Returns only public items."""
    student = StudentProfile.get_by_id(student_id)
    if not student:
        return error("Student not found.", 404)
    items = PortfolioItem.get_by_student(student_id, public_only=True)
    return success({"items": items, "total": len(items)})


@portfolio_bp.route("/<int:item_id>/visibility", methods=["PATCH"])
@jwt_required()
@student_required
def toggle_visibility(item_id):
    user_id   = int(get_jwt_identity())
    student   = StudentProfile.get_by_user(user_id)
    if not student:
        return error("Student profile not found.", 404)
    data      = request.get_json(silent=True) or {}
    is_public = bool(data.get("is_public", True))
    PortfolioItem.toggle_public(item_id, student["id"], is_public)
    state = "public" if is_public else "private"
    return success({"message": f"Portfolio item is now {state}."})
