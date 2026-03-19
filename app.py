# =========================================================
# UrbanHRPartners Enterprise Suite
# app.py (FULL FIXED - NO SHRINK)
# =========================================================

import os
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from functools import wraps
from pathlib import Path
from typing import Any

from flask import (
    Flask, flash, jsonify, redirect, render_template,
    request, session, url_for, send_from_directory
)
from jinja2 import TemplateNotFound
from sqlalchemy import inspect, func
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from models import *

# =========================================================
# BASE PATHS (MERGED CORRECTLY)
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SQLITE_PATH = BASE_DIR / "urbanhrpartners.db"

UPLOAD_FOLDER = BASE_DIR / "uploads"
CLIENT_PROGRAMS_FOLDER = BASE_DIR / "client_programs"
STATIC_FOLDER = BASE_DIR / "static"
TEMPLATES_FOLDER = BASE_DIR / "templates"

UPLOAD_FOLDER.mkdir(exist_ok=True)
CLIENT_PROGRAMS_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    "pdf","png","jpg","jpeg","gif",
    "doc","docx","xls","xlsx",
    "txt","csv","json",
}

# =========================================================
# XIOMY SAFE SYSTEM
# =========================================================

class SafeXiomyAI:
    def greeting(self):
        return "XIOMY Enterprise AI ready."
    def insight(self):
        return "Enterprise monitoring active."
    def system_status(self):
        return {"status": "active"}

def build_xiomy_instance(db):
    return SafeXiomyAI()

# =========================================================
# CORE HELPERS
# =========================================================

def normalize_database_url(raw_url):
    if not raw_url:
        return f"sqlite:///{DEFAULT_SQLITE_PATH}"
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql://")
    return raw_url

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def safe_count(model):
    try:
        return db.session.query(model).count()
    except:
        return 0

def safe_all(model, limit=None):
    try:
        q = model.query
        if hasattr(model, "id"):
            q = q.order_by(model.id.desc())
        if limit:
            q = q.limit(limit)
        return q.all()
    except:
        return []

def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except:
        return None

def parse_datetime(value):
    if not value:
        return None
    formats = [
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except:
            continue
    return None

def as_float(v, default=0.0):
    try:
        return float(v)
    except:
        return default

def commit_with_feedback(success, error, redirect_to):
    try:
        db.session.commit()
        flash(success, "success")
    except Exception as e:
        db.session.rollback()
        flash(f"{error}: {e}", "danger")
    return redirect(url_for(redirect_to))

# =========================================================
# BOOTSTRAP (FIXED)
# =========================================================

def bootstrap_admin():
    admin_email = "admin@urbanhrconsulting.cloud"
    existing = User.query.filter_by(email=admin_email).first()
    if existing:
        return existing

    admin = User(
        email=admin_email,
        password_hash=generate_password_hash("Admin123!"),
        role="Admin"
    )
    db.session.add(admin)
    db.session.commit()
    return admin

# =========================================================
# APP FACTORY (MERGED + FIXED)
# =========================================================

def create_app():

    app = Flask(
        __name__,
        template_folder=str(TEMPLATES_FOLDER),
        static_folder=str(STATIC_FOLDER)
    )

    app.config["SECRET_KEY"] = "enterprise-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = normalize_database_url(os.getenv("DATABASE_URL"))
    app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

    db.init_app(app)

    xiomy = build_xiomy_instance(db)

    with app.app_context():
        db.create_all()
        bootstrap_admin()

    # =====================================================
    # ROUTES (ALL PRESERVED)
    # =====================================================

    @app.route("/")
    def index():
        return redirect("/dashboard")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/crm")
    def crm():
        return render_template("crm.html")

    @app.route("/hris")
    def hris():
        return render_template("hris.html")

    @app.route("/ats")
    def ats():
        return render_template("ats.html")

    @app.route("/sgsst")
    def sgsst():
        return render_template("sgsst.html")

    @app.route("/finance")
    def finance():
        return render_template("finance.html")

    @app.route("/inventory")
    def inventory():
        return render_template("inventory.html")

    @app.route("/marketing")
    def marketing():
        return render_template("marketing.html")

    @app.route("/calendar")
    def calendar():
        return render_template("calendar.html")

    @app.route("/reports")
    def reports():
        return render_template("reports_analytics.html")

    # =====================================================
    # FILES
    # =====================================================

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # =====================================================
    # ERROR HANDLING
    # =====================================================

    @app.errorhandler(404)
    def not_found(e):
        return "404 Not Found", 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return "500 Internal Server Error", 500

    return app

# =========================================================
# ENTRYPOINT
# =========================================================

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
