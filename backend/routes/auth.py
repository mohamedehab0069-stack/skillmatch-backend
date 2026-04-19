from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from backend.models.user import User
from backend.models.student import StudentProfile
from backend.models.company import CompanyProfile
from backend.utils.responses import success, error
from backend.utils.validators import is_valid_email, is_strong_password, require_fields

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    missing = require_fields(data, ["name", "email", "password", "role"])
    if missing:
        return error(f"Missing fields: {', '.join(missing)}", 400)

    name     = data["name"].strip()
    email    = data["email"].strip().lower()
    password = data["password"]
    role     = data["role"]

    if role not in ("student", "company"):
        return error("Role must be 'student' or 'company'.", 400)
    if not is_valid_email(email):
        return error("Invalid email address.", 400)
    if not is_strong_password(password):
        return error("Password must be at least 8 characters and contain a letter and a number.", 400)
    if User.find_by_email(email):
        return error("Email already registered.", 409)

    hashed  = User.hash_password(password)
    user_id = User.create(name=name, email=email, password_hash=hashed,
                          role=role, phone=data.get("phone"))

    # Auto-create profile
    if role == "student":
        StudentProfile.create(
            user_id         = user_id,
            university      = data.get("university"),
            major           = data.get("major"),
            graduation_year = data.get("graduation_year"),
        )
    elif role == "company":
        company_name = data.get("company_name", name)
        CompanyProfile.create(
            user_id      = user_id,
            company_name = company_name,
            industry     = data.get("industry"),
            website      = data.get("website"),
        )

    token = create_access_token(
        identity=str(user_id),
        additional_claims={"role": role, "name": name}
    )
    return success({"token": token, "user_id": user_id, "role": role, "name": name}, 201)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    missing = require_fields(data, ["email", "password"])
    if missing:
        return error(f"Missing fields: {', '.join(missing)}", 400)

    email = data["email"].strip().lower()
    pw    = data["password"]

    user = User.find_by_email(email)
    if not user or not User.check_password(pw, user["password_hash"]):
        return error("Invalid email or password.", 401)
    if not user["is_active"]:
        return error("Account is deactivated. Contact support.", 403)

    token = create_access_token(
        identity=str(user["id"]),
        additional_claims={"role": user["role"], "name": user["name"]}
    )
    return success({
        "token"  : token,
        "user_id": user["id"],
        "role"   : user["role"],
        "name"   : user["name"],
    })


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user    = User.find_by_id(user_id)
    if not user:
        return error("User not found.", 404)
    return success(user)
