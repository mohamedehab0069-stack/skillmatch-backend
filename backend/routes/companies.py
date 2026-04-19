from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.company import CompanyProfile
from backend.models.user import User
from backend.utils.responses import success, error
from backend.utils.decorators import company_required

companies_bp = Blueprint("companies", __name__, url_prefix="/api/companies")


@companies_bp.route("/profile", methods=["GET"])
@jwt_required()
@company_required
def get_profile():
    user_id = int(get_jwt_identity())
    company = CompanyProfile.get_by_user(user_id)
    if not company:
        return error("Company profile not found.", 404)
    user = User.find_by_id(user_id)
    return success({**company, "name": user["name"], "email": user["email"]})


@companies_bp.route("/profile", methods=["PUT"])
@jwt_required()
@company_required
def update_profile():
    user_id = int(get_jwt_identity())
    company = CompanyProfile.get_by_user(user_id)
    if not company:
        return error("Company profile not found.", 404)
    data = request.get_json(silent=True) or {}
    CompanyProfile.update(company["id"], **data)
    return success({"message": "Company profile updated."})


@companies_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@company_required
def dashboard():
    """Return unified dashboard data for the company."""
    from backend.models.task import MicroTask
    from backend.models.internship import Internship
    from backend.models.notification import Notification

    user_id = int(get_jwt_identity())
    company = CompanyProfile.get_by_user(user_id)
    if not company:
        return error("Company profile not found.", 404)

    tasks        = MicroTask.get_by_company(company["id"])
    internships  = Internship.get_by_company(company["id"])
    unread       = Notification.unread_count(user_id)

    active_internships = [i for i in internships if i["status"] == "active"]
    active_tasks       = [t for t in tasks       if t["is_active"]]

    return success({
        "company"            : company,
        "total_internships"  : len(internships),
        "active_internships" : len(active_internships),
        "total_tasks"        : len(tasks),
        "active_tasks"       : len(active_tasks),
        "unread_notifications": unread,
        "recent_internships" : internships[:5],
        "recent_tasks"       : tasks[:5],
    })
