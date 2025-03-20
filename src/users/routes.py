from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from src.app import db
from src.users.models import User, UserUpdate
from src.utils import role_required

users = Blueprint("users", __name__)


@users.get("/")
@jwt_required()
@role_required(["admin"])
def get_all_users():
    users = User.query.filter_by(role="client").all()
    return jsonify({"users": [user.to_dict() for user in users]}), 200


@users.get("/doctors")
@jwt_required()
@role_required(["admin", "client"])
def get_all_doctors():
    first_name = request.args.get("first_name", "").strip()
    last_name = request.args.get("last_name", "").strip()

    query = User.query.filter_by(role="doctor").all()
    if len(first_name) == 0 and len(last_name) == 0:
        return jsonify({"doctors": [doctor.to_dict() for doctor in query]})
    doctors = filter(
        lambda doc: (first_name != "" and first_name in doc.first_name)
        or (last_name != "" and last_name in doc.last_name),
        query,
    )
    return jsonify({"doctors": [doctor.to_dict() for doctor in doctors]})


@users.get("/<int:user_id>")
@jwt_required()
@role_required(["admin", "doctor", "client"])
def get_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({"user": user.to_dict()})


@users.put("/<int:user_id>")
@jwt_required()
@role_required(["admin", "doctor", "client"])
def update_user(user_id):
    current_user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    current_user = User.query.get(current_user_id)

    if not user or not current_user:
        return jsonify({"message": "User not found"}), 404

    if current_user.role != "admin" and user.id != current_user_id:
        return jsonify({"message": "Access forbidden"}), 403

    try:
        data = request.get_json()
        validated_data = UserUpdate(**data)

        # Prevent role changes unless admin
        if (
            "role" in validated_data.model_dump(exclude_unset=True)
            and user.role != "admin"
        ):
            return jsonify({"message": "You cannot change the role"}), 403

        # Apply updates to the user object
        for field, value in validated_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        db.session.commit()
        return (
            jsonify({"message": "User updated successfully", "user": user.to_dict()}),
            200,
        )

    except ValidationError as e:
        return jsonify({"message": e.errors()}), 400
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"message": "Failed to update user"}), 500


@users.delete("/<int:user_id>")
@jwt_required()
@role_required(["admin", "client", "doctor"])
def delete_user(user_id):
    user = User.query.get(user_id)
    current_user = get_jwt_identity()
    if not user:
        return jsonify({"message": "User not found"}), 404
    if user.role != "admin" or str(user.id) != current_user:

        return jsonify({"message": "User can access only his account"}), 403
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "User deleted successfully"}), 200

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"message": "Failed to delete user"}), 500
