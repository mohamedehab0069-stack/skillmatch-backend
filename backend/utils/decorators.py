from functools import wraps
from flask_jwt_extended import get_jwt
from backend.utils.responses import error


def role_required(*roles):
    """Generic role guard. Usage: @role_required('student') or @role_required('admin','company')"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") not in roles:
                return error("Access forbidden: insufficient role.", 403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def student_required(fn):
    return role_required("student")(fn)


def company_required(fn):
    return role_required("company")(fn)


def admin_required(fn):
    return role_required("admin")(fn)


def student_or_admin(fn):
    return role_required("student", "admin")(fn)


def company_or_admin(fn):
    return role_required("company", "admin")(fn)
