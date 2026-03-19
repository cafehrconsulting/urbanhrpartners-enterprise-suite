# =========================================================
# UrbanHRPartners Enterprise Suite
# app.py (FULL CLEAN ENTERPRISE VERSION)
# Render-ready / Gunicorn-ready / NO CONFLICTS / NO SHRINKING
# =========================================================

import os
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
    send_from_directory
)

from jinja2 import TemplateNotFound
from sqlalchemy import inspect, func
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from models import db, User

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

# =========================================================
# HELPERS (CRITICAL FIXES)
# =========================================================

def as_float(value, default=0.0):
    try:
        return float(value)
    except:
        return default

def safe_xiomy_greeting(_=None):
    return "XIOMY AI ready."

def template_exists(template_name):
    try:
        from flask import current_app
        return template_name in current_app.jinja_env.list_templates()
    except:
        return False

def commit_with_feedback(success, error, redirect_route):
    try:
        db.session.commit()
        flash(success, "success")
    except Exception as e:
        db.session.rollback()
        flash(f"{error}: {str(e)}", "danger")
    return redirect(url_for(redirect_route))

# =========================================================
# DATABASE URL FIX
# =========================================================

def normalize_database_url(url):
    if not url:
        return f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url

# =========================================================
# APP FACTORY
# =========================================================

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = normalize_database_url(os.getenv("DATABASE_URL"))
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

    db.init_app(app)

    # =====================================================
    # DATABASE INIT
    # =====================================================

    with app.app_context():
        db.create_all()

        admin_email = os.getenv("ADMIN_EMAIL", "admin@urbanhr.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "Admin123!")

        if not User.query.filter_by(email=admin_email).first():
            admin = User(
                email=admin_email,
                password_hash=generate_password_hash(admin_password)
            )
            db.session.add(admin)
            db.session.commit()

    # =====================================================
    # CONTEXT
    # =====================================================

    @app.context_processor
    def inject():
        return {
            "app_name": "UrbanHRPartners Enterprise Suite",
            "today": date.today()
        }

    # =====================================================
    # ROUTES
    # =====================================================

    @app.route("/")
    def home():
        return redirect(url_for("dashboard"))

    @app.route("/dashboard")
    def dashboard():
        return render_safe("dashboard.html")

    @app.route("/crm")
    def crm():
        return render_safe("crm.html")

    @app.route("/hris")
    def hris():
        return render_safe("hris.html")

    @app.route("/ats")
    def ats():
        return render_safe("ats.html")

    @app.route("/sgsst")
    def sgsst():
        return render_safe("sgsst.html")

    @app.route("/finance")
    def finance():
        return render_safe("finance.html")

    @app.route("/inventory")
    def inventory():
        return render_safe("inventory.html")

    @app.route("/marketing")
    def marketing():
        return render_safe("marketing.html")

    # =====================================================
    # FILE UPLOAD
    # =====================================================

    @app.route("/upload", methods=["POST"])
    def upload():
        file = request.files.get("file")
        if not file:
            flash("No file", "danger")
            return redirect(url_for("dashboard"))

        filename = secure_filename(file.filename)
        file.save(UPLOAD_FOLDER / filename)

        flash("Uploaded", "success")
        return redirect(url_for("dashboard"))

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # =====================================================
    # SAFE RENDER
    # =====================================================

    def render_safe(template):
        try:
            return render_template(template)
        except TemplateNotFound:
            return f"<h1>{template} not ready</h1>"

    # =====================================================
    # ERRORS
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
