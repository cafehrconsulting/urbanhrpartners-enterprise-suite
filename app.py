# =========================================================
# UrbanHRPartners Enterprise Suite
# CLEAN app.py (NO CONFLICTS / READY TO RUN)
# =========================================================

import os
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
from typing import Any

from flask import (
    Flask, flash, jsonify, redirect, render_template,
    request, session, url_for, send_from_directory
)
from sqlalchemy import func
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from models import db, User

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "urbanhrpartners.db"

UPLOAD_FOLDER = BASE_DIR / "uploads"
STATIC_FOLDER = BASE_DIR / "static"
TEMPLATES_FOLDER = BASE_DIR / "templates"

UPLOAD_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    "pdf","png","jpg","jpeg","gif",
    "doc","docx","xls","xlsx","txt","csv"
}

# =========================================================
# HELPERS
# =========================================================

def normalize_db(url):
    if not url:
        return f"sqlite:///{DB_PATH}"
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://")
    return url

def allowed_file(name):
    return "." in name and name.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

def parse_date(val):
    try:
        return datetime.strptime(val, "%Y-%m-%d").date()
    except:
        return None

def parse_datetime(val):
    if not val:
        return None
    for f in ("%Y-%m-%dT%H:%M","%Y-%m-%d %H:%M","%Y-%m-%d"):
        try:
            return datetime.strptime(val,f)
        except:
            pass
    return None

def commit_ok(msg, fail, route):
    try:
        db.session.commit()
        flash(msg,"success")
    except Exception as e:
        db.session.rollback()
        flash(f"{fail}: {e}","danger")
    return redirect(url_for(route))

# =========================================================
# BOOTSTRAP ADMIN
# =========================================================

def ensure_admin():
    email = "admin@urbanhrconsulting.cloud"
    user = User.query.filter_by(email=email).first()
    if user:
        return
    db.session.add(User(
        email=email,
        password_hash=generate_password_hash("Admin123!"),
        role="Admin"
    ))
    db.session.commit()

# =========================================================
# APP FACTORY
# =========================================================

def create_app():

    app = Flask(
        __name__,
        template_folder=str(TEMPLATES_FOLDER),
        static_folder=str(STATIC_FOLDER)
    )

    app.config["SECRET_KEY"] = "enterprise-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = normalize_db(os.getenv("DATABASE_URL"))
    app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        ensure_admin()

    # =====================================================
    # ROUTES
    # =====================================================

    @app.route("/")
    def home():
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
    # FILE UPLOAD
    # =====================================================

    @app.route("/upload", methods=["POST"])
    def upload():
        f = request.files.get("file")
        if not f or not allowed_file(f.filename):
            flash("Invalid file","danger")
            return redirect("/dashboard")

        name = secure_filename(f.filename)
        f.save(UPLOAD_FOLDER / name)

        flash("Uploaded","success")
        return redirect("/dashboard")

    @app.route("/uploads/<path:name>")
    def files(name):
        return send_from_directory(app.config["UPLOAD_FOLDER"], name)

    # =====================================================
    # ERROR HANDLING
    # =====================================================

    @app.errorhandler(404)
    def not_found(e):
        return "404 Not Found",404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return "500 Internal Server Error",500

    return app

# =========================================================
# ENTRYPOINT
# =========================================================

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
