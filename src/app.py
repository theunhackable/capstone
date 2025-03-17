import os

from flask import Flask
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
    db.init_app(app)
    migrate = Migrate(app, db)

    return app
