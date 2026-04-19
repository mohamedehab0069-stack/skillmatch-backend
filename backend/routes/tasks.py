from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.student import StudentProfile
from backend.models.company import CompanyProfile
from backend.models.task import MicroTask, TaskSubmission
from backend.models.user import User
from backend.models.notification import Notification
from backend.services.portfolio_service import auto_generate_portfolio
from backend.utils.responses import success, error
from backend.utils.decorators import student_required, company_required, company_or_admin
from backend.utils.validators import require_fields

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")


# ── Student endpoints ─────────────────────────────────────────────────────────

@tasks_bp.route("/", methods=["GET"])
@jwt_required()
def list_tasks():
    """Return active micro-tasks. Accessible by all authenticated users."""
    category = request.args.get("category")
    tasks    = MicroTask.get_active(category)
    return success(tasks)


@tasks_bp.route("/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    task = MicroTask.get_by_id(task_id)
    if not task:
        return error("Task not found.", 404)
    return success(task)


@tasks_bp.route("/<int:task_id>/submit", methods=["POST"])
@jwt_required()
@student_required
def submit_task(task_id):
    user_id = int(get_jwt_identity())
    student = StudentProfile.get_by_user(user_id)
    if not student:
        return error("Student profile not found.", 404)

    task = MicroTask.get_by_id(task_id)
    if not task:
        return error("Task not found.", 404)
    if not task["is_active"]:
        return error("This task is no longer accepting submissions.", 400)

    data    = request.get_json(silent=True) or {}
    content = data.get("submission_content", "").strip()
    url     = data.get("submission_url", "").strip()

    if not content and not url:
        return error("Provide either submission_content or submission_url.", 400)

    sub_id = TaskSubmission.create(student["id"], task_id, content, url)

    # Notify company
    company_user_id = _get_user_id_for_company(task["company_id"])
    if company_user_id:
        user = User.find_by_id(user_id)
        Notification.create(
            user_id = company_user_id,
            title   = "New task submission received",
            message = f"{user['name']} submitted a solution for '{task['title']}'.",
            ntype   = "info"
        )

    return success({"submission_id": sub_id, "message": "Submission received."}, 201)


@tasks_bp.route("/my-submissions", methods=["GET"])
@jwt_required()
@student_required
def my_submissions():
    user_id = int(get_jwt_identity())
    student = StudentProfile.get_by_user(user_id)
    if not student:
        return error("Student profile not found.", 404)
    return success(TaskSubmission.get_by_student(student["id"]))


# ── Company endpoints ─────────────────────────────────────────────────────────

@tasks_bp.route("/", methods=["POST"])
@jwt_required()
@company_required
def create_task():
    user_id = int(get_jwt_identity())
    company = CompanyProfile.get_by_user(user_id)
    if not company:
        return error("Company profile not found.", 404)

    data    = request.get_json(silent=True) or {}
    missing = require_fields(data, ["title", "description", "difficulty"])
    if missing:
        return error(f"Missing fields: {', '.join(missing)}", 400)

    if data["difficulty"] not in ("easy", "medium", "hard"):
        return error("difficulty must be easy, medium, or hard.", 400)

    task_id = MicroTask.create(
        company_id  = company["id"],
        title       = data["title"],
        description = data["description"],
        category    = data.get("category", "General"),
        difficulty  = data["difficulty"],
        points      = int(data.get("points", 10)),
    )
    return success({"task_id": task_id, "message": "Task created."}, 201)


@tasks_bp.route("/company", methods=["GET"])
@jwt_required()
@company_required
def company_tasks():
    user_id = int(get_jwt_identity())
    company = CompanyProfile.get_by_user(user_id)
    if not company:
        return error("Company profile not found.", 404)
    return success(MicroTask.get_by_company(company["id"]))


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
@jwt_required()
@company_required
def deactivate_task(task_id):
    user_id = int(get_jwt_identity())
    company = CompanyProfile.get_by_user(user_id)
    if not company:
        return error("Company profile not found.", 404)

    task = MicroTask.get_by_id(task_id)
    if not task or task["company_id"] != company["id"]:
        return error("Task not found or access denied.", 404)

    MicroTask.toggle_active(task_id, False)
    return success({"message": "Task deactivated."})


@tasks_bp.route("/submissions/<int:task_id>", methods=["GET"])
@jwt_required()
@company_required
def get_submissions_for_task(task_id):
    user_id = int(get_jwt_identity())
    company = CompanyProfile.get_by_user(user_id)
    if not company:
        return error("Company profile not found.", 404)

    task = MicroTask.get_by_id(task_id)
    if not task or task["company_id"] != company["id"]:
        return error("Task not found or access denied.", 404)

    return success(TaskSubmission.get_pending_for_task(task_id))


@tasks_bp.route("/submissions/<int:submission_id>/review", methods=["PATCH"])
@jwt_required()
@company_or_admin
def review_submission(submission_id):
    data   = request.get_json(silent=True) or {}
    status = data.get("status")
    score  = int(data.get("score", 0))
    feedback = data.get("feedback", "").strip()

    if status not in ("approved", "rejected"):
        return error("status must be 'approved' or 'rejected'.", 400)
    if not 0 <= score <= 100:
        return error("score must be between 0 and 100.", 400)

    submission = TaskSubmission.get_by_id(submission_id)
    if not submission:
        return error("Submission not found.", 404)

    TaskSubmission.review(submission_id, status, score, feedback)

    # Auto-generate portfolio on approval
    portfolio_id = None
    if status == "approved":
        student = StudentProfile.get_by_id(submission["student_id"])
        if student:
            try:
                portfolio_id = auto_generate_portfolio(submission_id, student)
            except Exception:
                pass  # portfolio generation failure is non-fatal

    return success({
        "message"     : f"Submission {status}.",
        "portfolio_id": portfolio_id,
    })


# ── Helper ────────────────────────────────────────────────────────────────────

def _get_user_id_for_company(company_id: int):
    from backend.db import query
    row = query("SELECT user_id FROM company_profiles WHERE id=%s",
                (company_id,), fetch="one")
    return row["user_id"] if row else None
