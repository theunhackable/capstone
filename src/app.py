from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from src.helpers.db import init_db
from src.helpers.jwt_config import init_jwt

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    CORS(app)

    init_db(app, db)
    init_jwt(app)

    @app.route("/")
    def home():
        return {"message": "CORS is configured for Next.js!"}

    from src.admin.routes import admin
    from src.appointments.routes import appointments
    from src.auth.routes import auth
    from src.availability.routes import availability
    from src.users.routes import users

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(appointments, url_prefix="/appointments")
    app.register_blueprint(availability, url_prefix="/availability")
    app.register_blueprint(users, url_prefix="/users")
    return app
