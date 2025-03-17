import os

from dotenv import load_dotenv

from src.app import create_app, db

load_dotenv()
ENV = os.getenv("ENV", "development")
DEBUG = bool(os.getenv("DEBUG", True if ENV == "development" else False))
PORT = int(os.getenv("PORT", 3000))


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", debug=DEBUG, port=PORT)
