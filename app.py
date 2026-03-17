# =========================================================
# app.py
# =========================================================

import os
from flask import Flask
from models import db
from models import *

def create_app():
    app = Flask(__name__)

    # DATABASE CONFIG
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        "DATABASE_URL",
        "sqlite:///urbanhr.db"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # CREATE TABLES (CRITICAL FIX)
    with app.app_context():
        db.create_all()

    # ============================
    # TEST ROUTE
    # ============================
    @app.route("/")
    def home():
        return "UrbanHRPartners Running ✅"

    @app.route("/test-db")
    def test_db():
        client = Client(name="Test Client")
        db.session.add(client)
        db.session.commit()
        return "Database Working ✅"

    return app


# RUN APP
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
