from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.student import StudentProfile
from backend.models.assessment import LearningRoadmap
from backend.db import query
from backend.utils.responses import success, error
from backend.utils.decorators import student_required

roadmap_bp = Blueprint("roadmap", __name__, url_prefix="/api/roadmap")


@roadmap_bp.route("/", methods=["GET"])
@jwt_required()
@student_required
def get_roadmap():
    user_id = int(get_jwt_identity())
    student = StudentProfile.get_by_user(user_id)
    if not student:
        return error("Student profile not found.", 404)

    roadmap = LearningRoadmap.get_active(student["id"])
    if not roadmap:
        return error("No active roadmap found. Complete the career assessment first.", 404)

    # Attach courses from the DB catalog that match roadmap step titles
    courses = query(
        """SELECT rc.id, rc.order_index, rc.status, rc.completed_at,
                  c.title, c.provider, c.url, c.difficulty_level, c.duration_hours
           FROM roadmap_courses rc
           JOIN courses c ON c.id = rc.course_id
           WHERE rc.roadmap_id = %s
           ORDER BY rc.order_index ASC""",
        (roadmap["id"],)
    )

    completed = sum(1 for c in courses if c["status"] == "completed")
    total     = len(courses)
    progress  = round((completed / total * 100), 1) if total > 0 else 0

    return success({
        "roadmap" : roadmap,
        "courses" : courses,
        "progress": {"completed": completed, "total": total, "percent": progress}
    })


@roadmap_bp.route("/courses/<int:course_entry_id>/complete", methods=["PATCH"])
@jwt_required()
@student_required
def mark_course_complete(course_entry_id):
    """Mark a roadmap course entry as completed."""
    from datetime import datetime
    user_id = int(get_jwt_identity())
    student = StudentProfile.get_by_user(user_id)
    if not student:
        return error("Student profile not found.", 404)

    # Verify this entry belongs to this student's roadmap
    row = query(
        """SELECT rc.id FROM roadmap_courses rc
           JOIN learning_roadmaps lr ON lr.id = rc.roadmap_id
           WHERE rc.id = %s AND lr.student_id = %s""",
        (course_entry_id, student["id"]), fetch="one"
    )
    if not row:
        return error("Course entry not found or does not belong to your roadmap.", 404)

    query(
        "UPDATE roadmap_courses SET status='completed', completed_at=%s WHERE id=%s",
        (datetime.utcnow(), course_entry_id), fetch="none"
    )
    return success({"message": "Course marked as completed."})


@roadmap_bp.route("/courses/<int:course_entry_id>/start", methods=["PATCH"])
@jwt_required()
@student_required
def mark_course_in_progress(course_entry_id):
    user_id = int(get_jwt_identity())
    student = StudentProfile.get_by_user(user_id)
    if not student:
        return error("Student profile not found.", 404)

    row = query(
        """SELECT rc.id FROM roadmap_courses rc
           JOIN learning_roadmaps lr ON lr.id = rc.roadmap_id
           WHERE rc.id = %s AND lr.student_id = %s""",
        (course_entry_id, student["id"]), fetch="one"
    )
    if not row:
        return error("Course entry not found.", 404)

    query("UPDATE roadmap_courses SET status='in_progress' WHERE id=%s",
          (course_entry_id,), fetch="none")
    return success({"message": "Course marked as in progress."})


@roadmap_bp.route("/status", methods=["PATCH"])
@jwt_required()
@student_required
def update_roadmap_status():
    user_id = int(get_jwt_identity())
    student = StudentProfile.get_by_user(user_id)
    if not student:
        return error("Student profile not found.", 404)

    data   = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in ("active", "completed", "paused"):
        return error("status must be active, completed, or paused.", 400)

    roadmap = LearningRoadmap.get_active(student["id"])
    if not roadmap:
        return error("No active roadmap found.", 404)

    LearningRoadmap.update_status(roadmap["id"], status)
    return success({"message": f"Roadmap status updated to '{status}'."})
