from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.student import StudentProfile
from backend.models.company import CompanyProfile
from backend.models.internship import Internship
from backend.models.notification import Notification
from backend.models.user import User
from backend.services.ai_service import calculate_match_score
from backend.utils.responses import success, error
from backend.utils.decorators import student_required, company_required, company_or_admin
from backend.utils.validators import require_fields

internships_bp = Blueprint("internships", __name__, url_prefix="/api/internships")


# ── Student endpoints ─────────────────────────────────────────────────────────

@internships_bp.route("/", methods=["GET"])
@jwt_required()
@student_required
def list_internships():
    """
    Return all active internships with AI match scores for this student.
    Sorted by match score descending.
    """
    user_id = int(get_jwt_identity())
    student = StudentProfile.get_by_user(user_id)
    if not student:
        return error("Student profile not found.", 404)

    internships   = Internship.get_active()
    student_skills = StudentProfile.get_skills(student["id"])

    scored = []
    for internship in internships:
        try:
            match = calculate_match_score(
                student_skills,
                internship.get("required_skills", [])
            )
        except Exception:
            match = {"match_score": 0.0, "matched_skills": [], "missing_skills": [],
                     "recommendation": "Match score unavailable."}

        scored.append({**internship, "ai_match": match})

    scored.sort(key=lambda x: x["ai_match"]["match_score"], reverse=True)
    return success({"internships": scored, "total": len(scored)})


@internships_bp.route("/<int:internship_id>", methods=["GET"])
@jwt_required()
def get_internship(internship_id):
    internship = Internship.get_by_id(internship_id)
    if not internship:
        return error("Internship not found.", 404)
    return success(internship)


@internships_bp.route("/<int:internship_id>/apply", methods=["POST"])
@jwt_required()
@student_required
def apply(internship_id):
    user_id = int(get_jwt_identity())
    student = StudentProfile.get_by_user(user_id)
    if not student:
        return error("Student profile not found.", 404)

    internship = Internship.get_by_id(internship_id)
    if not internship:
        return error("Internship not found.", 404)
    if internship["status"] != "active":
        return error("This internship is no longer accepting applications.", 400)
    if Internship.already_applied(student["id"], internship_id):
        return error("You have already applied to this internship.", 409)

    data       = request.get_json(silent=True) or {}
    cover_note = data.get("cover_note", "").strip()

    # Calculate match score at moment of application
    student_skills = StudentProfile.get_skills(student["id"])
    try:
        match = calculate_match_score(student_skills, internship.get("required_skills", []))
    except Exception:
        match = {"match_score": 0.0, "matched_skills": [], "missing_skills": [],
                 "recommendation": "Score unavailable at time of application."}

    app_id = Internship.apply(
        student_id      = student["id"],
        internship_id   = internship_id,
        match_score     = match["match_score"],
        match_breakdown = match,
        cover_note      = cover_note,
    )

    # Notify company
    company_user = _get_company_user(internship["company_id"])
    if company_user:
        user = User.find_by_id(user_id)
        Notification.create(
            user_id = company_user["id"],
            title   = "New internship application",
            message = f"{user['name']} applied to '{internship['title']}' "
                      f"with a match score of {match['match_score']}%.",
            ntype   = "info"
        )

    return success({
        "application_id": app_id,
        "match_score"   : match["match_score"],
        "breakdown"     : match,
        "message"       : "Application submitted successfully.",
    }, 201)


@internships_bp.route("/my-applications", methods=["GET"])
@jwt_required()
@student_required
def my_applications():
    user_id = int(get_jwt_identity())
    student = StudentProfile.get_by_user(user_id)
    if not student:
        return error("Student profile not found.", 404)
    return success(Internship.get_student_applications(student["id"]))


# ── Company endpoints ─────────────────────────────────────────────────────────

@internships_bp.route("/", methods=["POST"])
@jwt_required()
@company_required
def create_internship():
    user_id = int(get_jwt_identity())
    company = CompanyProfile.get_by_user(user_id)
    if not company:
        return error("Company profile not found.", 404)

    data    = request.get_json(silent=True) or {}
    missing = require_fields(data, ["title", "description", "required_skills", "duration_weeks"])
    if missing:
        return error(f"Missing fields: {', '.join(missing)}", 400)

    if not isinstance(data["required_skills"], list):
        return error("required_skills must be a list.", 400)

    iid = Internship.create(
        company_id      = company["id"],
        title           = data["title"],
        description     = data["description"],
        location        = data.get("location", ""),
        is_remote       = bool(data.get("is_remote", False)),
        required_skills = data["required_skills"],
        duration_weeks  = int(data["duration_weeks"]),
        deadline        = data.get("application_deadline"),
    )
    return success({"internship_id": iid, "message": "Internship posted."}, 201)


@internships_bp.route("/company", methods=["GET"])
@jwt_required()
@company_required
def company_internships():
    user_id = int(get_jwt_identity())
    company = CompanyProfile.get_by_user(user_id)
    if not company:
        return error("Company profile not found.", 404)
    return success(Internship.get_by_company(company["id"]))


@internships_bp.route("/<int:internship_id>/status", methods=["PATCH"])
@jwt_required()
@company_required
def update_status(internship_id):
    user_id = int(get_jwt_identity())
    company = CompanyProfile.get_by_user(user_id)
    if not company:
        return error("Company profile not found.", 404)

    internship = Internship.get_by_id(internship_id)
    if not internship or internship["company_id"] != company["id"]:
        return error("Internship not found or access denied.", 404)

    data   = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in ("active", "closed", "draft"):
        return error("status must be active, closed, or draft.", 400)

    Internship.update_status(internship_id, status)
    return success({"message": f"Internship status updated to '{status}'."})


@internships_bp.route("/<int:internship_id>/applicants", methods=["GET"])
@jwt_required()
@company_required
def get_applicants(internship_id):
    user_id = int(get_jwt_identity())
    company = CompanyProfile.get_by_user(user_id)
    if not company:
        return error("Company profile not found.", 404)

    internship = Internship.get_by_id(internship_id)
    if not internship or internship["company_id"] != company["id"]:
        return error("Internship not found or access denied.", 404)

    applicants  = Internship.get_applications_for_internship(internship_id)
    min_score   = float(request.args.get("min_score", 0))
    if min_score > 0:
        applicants = [a for a in applicants if a["ai_match_score"] >= min_score]

    return success({"applicants": applicants, "total": len(applicants)})


@internships_bp.route("/applications/<int:application_id>/status", methods=["PATCH"])
@jwt_required()
@company_or_admin
def update_application_status(application_id):
    data   = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in ("reviewed", "accepted", "rejected"):
        return error("status must be reviewed, accepted, or rejected.", 400)

    Internship.update_application_status(application_id, status)

    # Notify student
    from backend.db import query
    app_row = query(
        """SELECT ia.student_id, i.title, sp.user_id
           FROM internship_applications ia
           JOIN internships i ON i.id = ia.internship_id
           JOIN student_profiles sp ON sp.id = ia.student_id
           WHERE ia.id = %s""",
        (application_id,), fetch="one"
    )
    if app_row:
        msg_map = {
            "reviewed": f"Your application for '{app_row['title']}' has been reviewed.",
            "accepted": f"Congratulations! You have been accepted for '{app_row['title']}'.",
            "rejected": f"Your application for '{app_row['title']}' was not selected this time.",
        }
        Notification.create(
            user_id = app_row["user_id"],
            title   = f"Application {status}",
            message = msg_map[status],
            ntype   = "success" if status == "accepted" else "info"
        )

    return success({"message": f"Application status updated to '{status}'."})


# ── Helper ────────────────────────────────────────────────────────────────────

def _get_company_user(company_id: int):
    from backend.db import query
    row = query(
        "SELECT u.id FROM company_profiles cp JOIN users u ON u.id=cp.user_id WHERE cp.id=%s",
        (company_id,), fetch="one"
    )
    return row
