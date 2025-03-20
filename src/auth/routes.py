from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from pydantic import ValidationError

from src.app import db
from src.users.models import User, UserCreate, UserLogin

auth = Blueprint("auth", __name__)


@auth.post("/signup")
def signup():
    try:
        data = UserCreate(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    existing_user = User.query.filter_by(email=data.email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409

    # Create new user
    new_user = User(
        role=data.role,
        first_name=data.first_name,
        last_name=data.last_name,
        address=data.address,
        profile_desc=data.profile_desc,
        email=data.email,
        password=data.password,
    )

    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=str(new_user.id))
    refresh_token = create_refresh_token(identity=str(new_user.id))

    return jsonify(
        {
            "msg": "User registered successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": new_user.to_dict(),
        }
    )


# ✅ User login route
@auth.post("/login")
def login():
    try:
        data = UserLogin(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    email = data.email
    password = data.password

    # Get user by email
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    if user.blocked:
        return jsonify({"message": "You are blocked"}), 403
    return jsonify(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict(),
        }
    )


@auth.get("/user/me")
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Return user data as a dictionary
    return jsonify({"user": user.to_dict()})


@auth.get("/refresh")
@jwt_required(refresh=True)
def refresh_token():
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=str(user_id))
    return jsonify({"access_token": new_access_token})


@auth.post("/logout")
@jwt_required()
def logout():
    return jsonify({"msg": "Successfully logged out"})
