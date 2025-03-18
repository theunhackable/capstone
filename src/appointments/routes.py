from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from src.app import db
from src.appointments.models import Appointment, AppointmentCreate
from src.users.models import User
from src.utils import role_required

appointments = Blueprint("appointments", __name__)


# ✅ Get all appointments for any user (admin, doctor, client)
@appointments.get("/")
@jwt_required()
@role_required(["admin", "doctor", "client"])
def get_all_appointments():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "user not found"}), 404

    if user.role == "doctor":
        # doctor's view: Get all appointments assigned to them
        appointments_list = Appointment.query.filter_by(doctor_id=user_id).all()
    elif user.role == "client":
        # client's view: Get all their appointments
        appointments_list = Appointment.query.filter_by(user_id=user_id).all()
    else:
        # admin's view: Get all appointments
        appointments_list = Appointment.query.all()

    return jsonify([appointment.to_dict() for appointment in appointments_list])


@appointments.get("/<int:appointment_id>")
@jwt_required()
@role_required(["admin", "doctor", "client"])
def get_appointment(appointment_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "user not found"}), 404

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404

    # Authorization: doctor can only view their own appointments
    if user.role == "doctor" and appointment.doctor_id != user_id:
        return jsonify({"error": "Unauthorized access"}), 403

    # client can only view their own appointments
    if user.role == "client" and appointment.user_id != user_id:
        return jsonify({"error": "Unauthorized access"}), 403

    return jsonify({"appointment": appointment.to_dict()})


@appointments.post("/")
@jwt_required()
@role_required(["client"])
def create_appointment():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        appointment_data = AppointmentCreate(**data)
        user = User.query.get(appointment_data.user_id)
        doctor = User.query.get(appointment_data.doctor_id)

        if not user or not doctor or user.role != "client" or doctor.role != "doctor":
            return jsonify({"message": "One id must be a doctor"}), 400
        if str(user.id) != current_user:
            return jsonify({"message": "Not Allowed"}), 403
        new_appointment = Appointment(
            user_id=appointment_data.user_id,
            doctor_id=appointment_data.doctor_id,
            date_time=appointment_data.date_time,
            client_requirements=appointment_data.client_requirements,
        )

        db.session.add(new_appointment)
        db.session.commit()
        return jsonify({"msg": "Appointment created successfully"}), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError:
        return jsonify({"error": "Failed to create appointment"}), 500


@appointments.put("/cancel/<int:appointment_id>")
@jwt_required()
@role_required(["doctor", "client"])
def cancel_appointment(appointment_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "user not found"}), 404

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404

    # Authorization: doctor can only cancel their own appointments
    if user.role == "doctor" and appointment.doctor_id != user_id:
        return jsonify({"error": "Unauthorized access"}), 403

    # client can only cancel their own appointments
    if user.role == "client" and appointment.user_id != user_id:
        return jsonify({"error": "Unauthorized access"}), 403

    appointment.status = "canceled"
    db.session.commit()

    return jsonify({"msg": "Appointment canceled successfully"}), 200
