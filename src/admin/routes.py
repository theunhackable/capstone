from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from src.app import db
from src.users.models import User
from src.utils import role_required

admin = Blueprint("admin", __name__)


@admin.get("/users/")
@jwt_required()
@role_required(["admin"])
def get_all_users():
    """Fetch all users."""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@admin.put("/users/block/<int:user_id>")
@jwt_required()
@role_required(["admin"])
def block_unblock_user(user_id):
    """Block or unblock a user."""
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    user.blocked = not user.blocked
    db.session.commit()
    status = "blocked" if user.blocked else "unblocked"
    return jsonify({"message": f"User {user.email} has been {status}."})
