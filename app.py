# =========================================================
# UrbanHRPartners Enterprise Suite
# CLEAN APP.PY (RUNTIME-SAFE)
# =========================================================

import os
from pathlib import Path

from flask import Flask, redirect, render_template, send_from_directory
from jinja2 import TemplateNotFound
from sqlalchemy import inspect
from werkzeug.security import generate_password_hash

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
STATIC_FOLDER.mkdir(exist_ok=True)
TEMPLATES_FOLDER.mkdir(exist_ok=True)

# =========================================================
# HELPERS
# =========================================================

def normalize_database_url(raw_url: str | None) -> str:
    if not raw_url:
        return f"sqlite:///{DB_PATH}"
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql://", 1)
    return raw_url


def template_exists(app: Flask, template_name: str) -> bool:
    try:
        app.jinja_env.get_template(template_name)
        return True
    except TemplateNotFound:
        return False
    except Exception:
        return False


def safe_render(app: Flask, template_name: str, page_title: str):
    try:
        return render_template(template_name)
    except TemplateNotFound:
        return (
            "<!doctype html>"
            "<html><head><title>UrbanHRPartners</title></head>"
            "<body style='font-family:Arial;padding:30px'>"
            f"<h1>{page_title}</h1>"
            f"<p>Template <strong>{template_name}</strong> is not present yet.</p>"
            "<p>The route is active and the backend is working.</p>"
            "</body></html>"
        )
    except Exception as exc:
        return (
            "<!doctype html>"
            "<html><head><title>UrbanHRPartners</title></head>"
            "<body style='font-family:Arial;padding:30px'>"
            f"<h1>{page_title}</h1>"
            f"<p>Template error while loading <strong>{template_name}</strong>.</p>"
            f"<pre>{exc}</pre>"
            "</body></html>"
        ), 500


def bootstrap_admin():
    admin_email = "admin@urbanhrconsulting.cloud"
    existing = User.query.filter_by(email=admin_email).first()
    if existing:
        return existing

    cols = {c.key for c in inspect(User).columns}
    payload = {}

    if "email" in cols:
        payload["email"] = admin_email
    if "password_hash" in cols:
        payload["password_hash"] = generate_password_hash("Admin123!")
    elif "password" in cols:
        payload["password"] = generate_password_hash("Admin123!")
    if "role" in cols:
        payload["role"] = "Admin"
    if "full_name" in cols:
        payload["full_name"] = "UrbanHRPartners Administrator"
    elif "name" in cols:
        payload["name"] = "UrbanHRPartners Administrator"
    if "status" in cols:
        payload["status"] = "Active"
    if "is_active" in cols:
        payload["is_active"] = True
    if "language" in cols:
        payload["language"] = "English"
    if "timezone" in cols:
        payload["timezone"] = "America/New_York"

    admin = User(**payload)
    db.session.add(admin)
    db.session.commit()
    return admin

# =========================================================
# APP FACTORY
# =========================================================

def create_app():
    app = Flask(
        __name__,
        template_folder=str(TEMPLATES_FOLDER),
        static_folder=str(STATIC_FOLDER),
    )

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "enterprise-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = normalize_database_url(os.getenv("DATABASE_URL"))
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        try:
            bootstrap_admin()
        except Exception:
            db.session.rollback()

    @app.route("/")
    def home():
        return redirect("/dashboard")

    @app.route("/dashboard")
    def dashboard():
        return safe_render(app, "dashboard.html", "Dashboard")

    @app.route("/crm")
    def crm():
        return safe_render(app, "crm.html", "CRM")

    @app.route("/hris")
    def hris():
        return safe_render(app, "hris.html", "HRIS")

    @app.route("/ats")
    def ats():
        return safe_render(app, "ats.html", "ATS")

    @app.route("/orientation")
    def orientation():
        return safe_render(app, "orientation.html", "Orientation")

    @app.route("/sgsst")
    def sgsst():
        return safe_render(app, "sgsst.html", "SG-SST")

    @app.route("/finance")
    def finance():
        return safe_render(app, "finance.html", "Finance")

    @app.route("/inventory")
    def inventory():
        return safe_render(app, "inventory.html", "Inventory")

    @app.route("/marketing")
    def marketing():
        return safe_render(app, "marketing.html", "Marketing")

    @app.route("/calendar")
    def calendar():
        return safe_render(app, "calendar.html", "Calendar")

    @app.route("/reports")
    def reports():
        if template_exists(app, "reports_analytics.html"):
            return safe_render(app, "reports_analytics.html", "Reports")
        return safe_render(app, "reports.html", "Reports")

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @app.errorhandler(404)
    def not_found(error):
        return "404 Not Found", 404

    @app.errorhandler(500)
    def server_error(error):
        try:
            db.session.rollback()
        except Exception:
            pass
        return (
            "<!doctype html>"
            "<html><head><title>UrbanHRPartners</title></head>"
            "<body style='font-family:Arial;padding:30px'>"
            "<h1>500 - Internal Server Error</h1>"
            "<p>The backend is running, but a route raised an exception.</p>"
            "<p>This usually means a missing template, a model-field mismatch, or a database issue.</p>"
            "</body></html>"
        ), 500

    return app

# =========================================================
# ENTRYPOINT
# =========================================================

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
