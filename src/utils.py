from functools import wraps

from flask import has_request_context, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.users.models import User


def role_required(roles):
    """Role-based access decorator."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return jsonify({"error": "User not found"}), 404

            if user.blocked:
                return (
                    jsonify({"error": "Your account is blocked. Contact Admin."}),
                    403,
                )

            if user.role not in roles:
                return jsonify({"error": "Unauthorized access"}), 403

            return func(*args, **kwargs)

        return wrapper

    return decorator
