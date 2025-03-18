import os
from datetime import timedelta

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    DB_PASS = os.getenv("MYSQL_ROOT_PASSWORD")
    DB_PORT = os.getenv("MYSQL_PORT")
    DB_HOST = os.getenv("MYSQL_HOST")
    DB_DB = os.getenv("MYSQL_DATABASE")

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://root:{ DB_PASS }@{DB_HOST}:{DB_PORT}/{DB_DB}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)  # 1 hour expiry
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)  # 7 days expiry
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]  # Default: Authorization Header
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager()
    jwt.init_app(app)
    from flask_jwt_extended.exceptions import NoAuthorizationError
    from werkzeug.exceptions import HTTPException

    @app.errorhandler(NoAuthorizationError)
    def handle_no_authorization_error(e):
        return jsonify({"error": "Authorization token is missing or invalid"}), 401

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = e.get_response()
        response.data = jsonify({"error": e.description}).data
        response.content_type = "application/json"
        return response
        # blueprints

    from src.auth.routes import auth

    app.register_blueprint(auth, url_prefix="/auth")
    return app
