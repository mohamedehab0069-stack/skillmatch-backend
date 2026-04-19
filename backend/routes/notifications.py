from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.notification import Notification
from backend.utils.responses import success, error

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


@notifications_bp.route("/", methods=["GET"])
@jwt_required()
def get_notifications():
    user_id     = int(get_jwt_identity())
    unread_only = request.args.get("unread") == "true"
    items       = Notification.get_for_user(user_id, unread_only)
    unread_cnt  = Notification.unread_count(user_id)
    return success({"notifications": items, "unread_count": unread_cnt})


@notifications_bp.route("/<int:notification_id>/read", methods=["PATCH"])
@jwt_required()
def mark_read(notification_id):
    user_id = int(get_jwt_identity())
    Notification.mark_read(notification_id, user_id)
    return success({"message": "Notification marked as read."})


@notifications_bp.route("/read-all", methods=["PATCH"])
@jwt_required()
def mark_all_read():
    user_id = int(get_jwt_identity())
    Notification.mark_all_read(user_id)
    return success({"message": "All notifications marked as read."})
