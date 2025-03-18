from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from src.app import db
from src.availability.models import Availability, AvailabilityCreate, AvailabilityUpdate
from src.users.models import User
from src.utils import role_required

availability = Blueprint("availability", __name__)


@availability.get("/")
@role_required(["admin", "doctor", "client"])
def get_all_availabilities():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": " User not found"}), 404
    if user.role == "doctor":
        # doctor sees only their availability
        availabilities_list = Availability.query.filter_by(doctor_id=user_id).all()
    else:
        # admin and user sees all availabilities
        availabilities_list = Availability.query.all()

    return jsonify([availability.to_dict() for availability in availabilities_list])


# ✅ Get availability by ID
@availability.get("/<int:availability_id>")
@role_required(["admin", "doctor", "client"])
def get_availability(availability_id):
    availability = Availability.query.get(availability_id)

    if not availability:
        return jsonify({"error": "Availability not found"}), 404

    # doctor can only access their own availability
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.role == "doctor" and availability.doctor_id != user_id:
        return jsonify({"error": "Unauthorized access"}), 403

    return jsonify({"availability": availability.to_dict()})


# ✅ Create availability (doctor only)
@availability.post("/")
@role_required(["doctor"])
def create_availability():
    try:
        data = request.get_json()
        availability_data = AvailabilityCreate(**data)

        # Check if the logged-in doctor is adding their own availability
        user_id = get_jwt_identity()
        if availability_data.doctor_id != user_id:
            return (
                jsonify({"error": "doctors can only set their own availability"}),
                403,
            )

        new_availability = Availability(
            doctor_id=availability_data.doctor_id,
            date_time=availability_data.date_time,
        )

        db.session.add(new_availability)
        db.session.commit()
        return jsonify({"msg": "Availability created successfully"}), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError:
        return jsonify({"error": "Failed to create availability"}), 500


@availability.put("/<int:availability_id>")
@jwt_required()
@role_required(["doctor"])
def update_availability(availability_id):
    availability = Availability.query.get(availability_id)

    if not availability:
        return jsonify({"error": "Availability not found"}), 404

    # Only the doctor who created the availability can modify it
    user_id = get_jwt_identity()
    if availability.doctor_id != user_id:
        return jsonify({"error": "Unauthorized access"}), 403

    try:
        data = request.get_json()
        update_data = AvailabilityUpdate(**data)

        if update_data.date_time:
            availability.date_time = update_data.date_time

        db.session.commit()
        return jsonify({"msg": "Availability updated successfully"}), 200
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError:
        return jsonify({"error": "Failed to update availability"}), 500


@availability.delete("/<int:availability_id>")
@jwt_required()
@role_required(["admin", "doctor"])
def delete_availability(availability_id):
    availability = Availability.query.get(availability_id)

    if not availability:
        return jsonify({"error": "Availability not found"}), 404

    # doctor can only delete their own availability
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    if user.role == "doctor" and availability.doctor_id != user_id:
        return jsonify({"error": "Unauthorized access"}), 403

    db.session.delete(availability)
    db.session.commit()

    return jsonify({"msg": "Availability deleted successfully"}), 200
