from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from backend.models.user import User
from backend.models.student import StudentProfile
from backend.models.company import CompanyProfile
from backend.models.task import MicroTask, TaskSubmission
from backend.models.internship import Internship
from backend.models.notification import Notification
from backend.db import query
from backend.utils.responses import success, error
from backend.utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@admin_required
def dashboard():
    """Platform-wide metrics."""
    def count(table, where=""):
        row = query(f"SELECT COUNT(*) as cnt FROM {table} {where}", fetch="one")
        return row["cnt"] if row else 0

    return success({
        "users"        : {
            "total"    : count("users"),
            "students" : count("users", "WHERE role='student'"),
            "companies": count("users", "WHERE role='company'"),
            "active"   : count("users", "WHERE is_active=TRUE"),
        },
        "assessments"  : count("career_assessments"),
        "personas"     : count("career_personas"),
        "roadmaps"     : count("learning_roadmaps"),
        "tasks"        : {
            "total"   : count("micro_tasks"),
            "active"  : count("micro_tasks", "WHERE is_active=TRUE"),
        },
        "submissions"  : {
            "total"   : count("task_submissions"),
            "pending" : count("task_submissions", "WHERE status='pending'"),
            "approved": count("task_submissions", "WHERE status='approved'"),
            "rejected": count("task_submissions", "WHERE status='rejected'"),
        },
        "portfolio"    : count("portfolio_items"),
        "internships"  : {
            "total"   : count("internships"),
            "active"  : count("internships", "WHERE status='active'"),
        },
        "applications" : {
            "total"   : count("internship_applications"),
            "accepted": count("internship_applications", "WHERE status='accepted'"),
        },
    })


# ── User management ───────────────────────────────────────────────────────────

@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@admin_required
def list_users():
    role  = request.args.get("role")
    users = User.all_users(role)
    return success({"users": users, "total": len(users)})


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
@admin_required
def get_user(user_id):
    user = User.find_by_id(user_id)
    if not user:
        return error("User not found.", 404)

    extra = {}
    if user.get("role") == "student":
        profile = StudentProfile.get_by_user(user_id)
        if profile:
            extra["profile"] = profile
            extra["skills"]  = StudentProfile.get_skills(profile["id"])
    elif user.get("role") == "company":
        profile = CompanyProfile.get_by_user(user_id)
        if profile:
            extra["profile"] = profile

    return success({**user, **extra})


@admin_bp.route("/users/<int:user_id>/activate", methods=["PATCH"])
@jwt_required()
@admin_required
def set_user_active(user_id):
    data   = request.get_json(silent=True) or {}
    active = bool(data.get("is_active", True))
    user   = User.find_by_id(user_id)
    if not user:
        return error("User not found.", 404)
    User.set_active(user_id, active)
    state = "activated" if active else "deactivated"
    return success({"message": f"User {state}."})


@admin_bp.route("/users/<int:user_id>/verify-company", methods=["PATCH"])
@jwt_required()
@admin_required
def verify_company(user_id):
    company = CompanyProfile.get_by_user(user_id)
    if not company:
        return error("Company profile not found.", 404)
    CompanyProfile.verify(company["id"])
    Notification.create(
        user_id = user_id,
        title   = "Company account verified",
        message = "Your company account has been verified by SkillMatch+ admin. "
                  "You can now post internships and tasks.",
        ntype   = "success"
    )
    return success({"message": "Company verified."})


# ── Task approval ─────────────────────────────────────────────────────────────

@admin_bp.route("/tasks/pending-review", methods=["GET"])
@jwt_required()
@admin_required
def pending_tasks():
    """Tasks that are deactivated and awaiting admin approval."""
    rows = query(
        """SELECT mt.*, cp.company_name FROM micro_tasks mt
           JOIN company_profiles cp ON cp.id=mt.company_id
           WHERE mt.is_active=FALSE ORDER BY mt.created_at DESC"""
    )
    return success({"tasks": rows, "total": len(rows)})


@admin_bp.route("/tasks/<int:task_id>/approve", methods=["PATCH"])
@jwt_required()
@admin_required
def approve_task(task_id):
    data    = request.get_json(silent=True) or {}
    approve = bool(data.get("approved", True))
    task    = MicroTask.get_by_id(task_id)
    if not task:
        return error("Task not found.", 404)

    MicroTask.toggle_active(task_id, approve)

    company_user = query(
        "SELECT user_id FROM company_profiles WHERE id=%s", (task["company_id"],), fetch="one"
    )
    if company_user:
        status_text = "approved and is now live" if approve else "rejected by admin"
        Notification.create(
            user_id = company_user["user_id"],
            title   = f"Task '{task['title']}' {('approved' if approve else 'rejected')}",
            message = f"Your task '{task['title']}' has been {status_text}.",
            ntype   = "success" if approve else "warning"
        )

    return success({"message": f"Task {'approved' if approve else 'rejected'}."})


# ── Submissions oversight ─────────────────────────────────────────────────────

@admin_bp.route("/submissions/pending", methods=["GET"])
@jwt_required()
@admin_required
def all_pending_submissions():
    rows = query(
        """SELECT ts.*, mt.title as task_title, u.name as student_name, cp.company_name
           FROM task_submissions ts
           JOIN micro_tasks mt ON mt.id=ts.task_id
           JOIN student_profiles sp ON sp.id=ts.student_id
           JOIN users u ON u.id=sp.user_id
           JOIN company_profiles cp ON cp.id=mt.company_id
           WHERE ts.status='pending'
           ORDER BY ts.submitted_at ASC"""
    )
    return success({"submissions": rows, "total": len(rows)})


# ── Skills and courses management ─────────────────────────────────────────────

@admin_bp.route("/skills", methods=["GET"])
@jwt_required()
@admin_required
def list_skills():
    rows = query("SELECT * FROM skills ORDER BY category, name")
    return success(rows)


@admin_bp.route("/skills", methods=["POST"])
@jwt_required()
@admin_required
def add_skill():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    if not name:
        return error("name is required.", 400)
    from backend.db import query as dbq
    sid = dbq(
        "INSERT INTO skills (name, category, level) VALUES (%s,%s,%s)",
        (name, data.get("category", "General"), data.get("level", "beginner")),
        fetch="none"
    )
    return success({"skill_id": sid, "message": "Skill added."}, 201)


@admin_bp.route("/courses", methods=["GET"])
@jwt_required()
@admin_required
def list_courses():
    rows = query("SELECT * FROM courses WHERE is_active=TRUE ORDER BY category, title")
    return success(rows)


@admin_bp.route("/courses", methods=["POST"])
@jwt_required()
@admin_required
def add_course():
    data    = request.get_json(silent=True) or {}
    missing = [f for f in ["title", "provider", "url", "category"] if not data.get(f)]
    if missing:
        return error(f"Missing fields: {', '.join(missing)}", 400)
    cid = query(
        "INSERT INTO courses (title,provider,url,category,difficulty_level,duration_hours) VALUES (%s,%s,%s,%s,%s,%s)",
        (data["title"], data["provider"], data["url"], data["category"],
         data.get("difficulty_level", "beginner"), data.get("duration_hours", 0)),
        fetch="none"
    )
    return success({"course_id": cid, "message": "Course added."}, 201)
