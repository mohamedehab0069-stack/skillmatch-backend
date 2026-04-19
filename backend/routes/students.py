from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.student import StudentProfile
from backend.models.user import User
from backend.utils.responses import success, error
from backend.utils.decorators import student_required

students_bp = Blueprint("students", __name__, url_prefix="/api/students")


@students_bp.route("/profile", methods=["GET"])
@jwt_required()
@student_required
def get_profile():
    user_id = int(get_jwt_identity())
    student = StudentProfile.get_by_user(user_id)
    if not student:
        return error("Student profile not found.", 404)
    user    = User.find_by_id(user_id)
    skills  = StudentProfile.get_skills(student["id"])
    return success({**student, "name": user["name"], "email": user["email"], "skills": skills})


@students_bp.route("/profile", methods=["PUT"])
@jwt_required()
@student_required
def update_profile():
    user_id = int(get_jwt_identity())
    student = StudentProfile.get_by_user(user_id)
    if not student:
        return error("Student profile not found.", 404)
    data = request.get_json(silent=True) or {}
    StudentProfile.update(student["id"], **data)
    return success({"message": "Profile updated successfully."})


@students_bp.route("/skills", methods=["GET"])
@jwt_required()
@student_required
def get_skills():
    user_id = int(get_jwt_identity())
    student = StudentProfile.get_by_user(user_id)
    if not student:
        return error("Student profile not found.", 404)
    return success(StudentProfile.get_skills(student["id"]))


@students_bp.route("/skills", methods=["POST"])
@jwt_required()
@student_required
def add_skill():
    user_id = int(get_jwt_identity())
    student = StudentProfile.get_by_user(user_id)
    if not student:
        return error("Student profile not found.", 404)
    data = request.get_json(silent=True) or {}
    skill_name  = data.get("skill_name", "").strip()
    proficiency = data.get("proficiency", "beginner")
    if not skill_name:
        return error("skill_name is required.", 400)
    if proficiency not in ("beginner", "intermediate", "advanced"):
        return error("proficiency must be beginner, intermediate, or advanced.", 400)
    StudentProfile.add_skill(student["id"], skill_name, proficiency)
    return success({"message": f"Skill '{skill_name}' added."}, 201)


@students_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@student_required
def dashboard():
    """Return a unified dashboard summary for the student."""
    from backend.models.assessment import CareerPersona, LearningRoadmap
    from backend.models.task import TaskSubmission, PortfolioItem
    from backend.models.internship import Internship
    from backend.models.notification import Notification

    user_id = int(get_jwt_identity())
    student = StudentProfile.get_by_user(user_id)
    if not student:
        return error("Student profile not found.", 404)

    user     = User.find_by_id(user_id)
    persona  = CareerPersona.get_latest(student["id"])
    roadmap  = LearningRoadmap.get_active(student["id"])
    skills   = StudentProfile.get_skills(student["id"])
    subs     = TaskSubmission.get_by_student(student["id"])
    portfolio = PortfolioItem.get_by_student(student["id"])
    apps     = Internship.get_student_applications(student["id"])
    unread   = Notification.unread_count(user_id)

    approved_count = sum(1 for s in subs if s["status"] == "approved")
    pending_count  = sum(1 for s in subs if s["status"] == "pending")

    return success({
        "student"         : {**student, "name": user["name"], "email": user["email"]},
        "has_persona"     : persona is not None,
        "persona_title"   : persona["persona_title"] if persona else None,
        "career_path"     : roadmap["career_path"]   if roadmap else None,
        "roadmap_status"  : roadmap["status"]         if roadmap else None,
        "skills_count"    : len(skills),
        "verified_skills" : sum(1 for s in skills if s["is_verified"]),
        "tasks_submitted" : len(subs),
        "tasks_approved"  : approved_count,
        "tasks_pending"   : pending_count,
        "portfolio_items" : len(portfolio),
        "applications"    : len(apps),
        "unread_notifications": unread,
    })
