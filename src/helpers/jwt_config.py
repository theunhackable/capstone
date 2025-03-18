import os
from datetime import timedelta

from flask import jsonify
from flask_jwt_extended import JWTManager


def init_jwt(app):
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)  # 1 hour expiry
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)  # 7 days expiry
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]  # Default: Authorization Header
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"

    jwt = JWTManager()
    from flask_jwt_extended.exceptions import NoAuthorizationError
    from werkzeug.exceptions import HTTPException

    # ✅ Handle missing or invalid JWT
    @app.errorhandler(NoAuthorizationError)
    def handle_no_authorization_error(e):
        return jsonify({"error": "Authorization token is missing or invalid"}), 401

    # ✅ Catch-all error handler for other HTTP errors
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = e.get_response()
        response.data = jsonify({"error": e.description}).data
        response.content_type = "application/json"
        return response

    jwt.init_app(app)
