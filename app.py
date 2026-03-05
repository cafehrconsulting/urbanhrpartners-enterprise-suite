import os
import csv
from datetime import datetime
from io import StringIO

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    Response,
    flash,
    current_app,   # ✅ ADDED
)
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def normalize_database_url(raw: str) -> str:
    if not raw:
        return ""
    if raw.startswith("postgres://"):
        return raw.replace("postgres://", "postgresql://", 1)
    return raw


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.secret_key = os.environ.get("SECRET_KEY", "CHANGE_ME_LOCAL_DEV")

    # ---------------------------
    # Database (SQLite local / DATABASE_URL for Render)
    # ---------------------------
    database_url = normalize_database_url(os.environ.get("DATABASE_URL", ""))
    if not database_url:
        database_url = "sqlite:///urbanhr.db"

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    # ---------------------------
    # Branding (ALWAYS available)
    # ---------------------------
    BRAND = {
        "company": os.environ.get("BRAND_COMPANY", "UrbanHRPartners Consulting"),
        "owner_name": os.environ.get("BRAND_OWNER_NAME", "Juan Carlos Urbano"),
        "owner_title": os.environ.get("BRAND_OWNER_TITLE", "PhD(c) Business Psychology"),
        "contact_email": os.environ.get("BRAND_CONTACT_EMAIL", "urbanhrpartnersconsulting@gmail.com"),
        "contact_phone_usa": os.environ.get("BRAND_CONTACT_PHONE_USA", "+15168709645"),
        "contact_phone_co": os.environ.get("BRAND_CONTACT_PHONE_CO", "+573160533654"),
        "logo_static_path": os.environ.get("BRAND_LOGO_PATH", "images/logo.png"),  # static/images/logo.png
    }

    CONTACT_LINE = (
        f"USA WhatsApp: {BRAND['contact_phone_usa']} • "
        f"Colombia WhatsApp: {BRAND['contact_phone_co']} • "
        f"{BRAND['contact_email']}"
    )

    @app.context_processor
    def inject_branding():
        return {
            "BRAND": BRAND,
            "CONTACT_LINE": CONTACT_LINE,
            "LOGO_URL": url_for("static", filename=BRAND.get("logo_static_path", "images/logo.png")),
        }

    # ---------------------------
    # ✅ Route flags (what you asked for)
    # ---------------------------
    @app.context_processor
    def inject_flags():
        return {"has_crm_csv": "crm_csv" in current_app.view_functions}

    # ---------------------------
    # Helpers
    # ---------------------------
    def csv_response(filename: str, header: list[str], rows: list[list]):
        buf = StringIO()
        w = csv.writer(buf)
        w.writerow(header)
        for r in rows:
            w.writerow(r)
        return Response(
            buf.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    # ---------------------------
    # safe_url (REGISTERED TWO WAYS)
    # ---------------------------
    def safe_url(endpoint: str) -> str:
        if endpoint in app.view_functions:
            return url_for(endpoint)
        return "#"

    @app.context_processor
    def inject_safe_url():
        return {"safe_url": safe_url}

    app.jinja_env.globals["safe_url"] = safe_url

    # ---------------------------
    # Models
    # ---------------------------
    class CrmAccount(db.Model):
        __tablename__ = "crm_accounts"
        id = db.Column(db.Integer, primary_key=True)
        account_name = db.Column(db.String(255), nullable=False)
        industry = db.Column(db.String(255), nullable=True)
        status = db.Column(db.String(50), nullable=False, default="Active")
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    with app.app_context():
        db.create_all()

    # ---------------------------
    # Routes (PUBLIC / NO LOGIN)
    # ---------------------------
    @app.get("/health")
    def health():
        return {"status": "ok", "time": datetime.utcnow().isoformat()}

    @app.get("/")
    def home():
        return redirect(url_for("dashboard"))

    @app.get("/dashboard")
    def dashboard():
        totals = {"crm_accounts": CrmAccount.query.count()}
        return render_template("dashboard.html", page_title="Dashboard", totals=totals)

    @app.route("/crm", methods=["GET", "POST"])
    def crm():
        if request.method == "POST":
            name = (request.form.get("account_name") or "").strip()
            industry = (request.form.get("industry") or "").strip()

            if not name:
                flash("Account name is required.", "danger")
            else:
                db.session.add(CrmAccount(account_name=name, industry=industry or None))
                db.session.commit()
                flash("Account added.", "success")

            return redirect(url_for("crm"))

        accounts = CrmAccount.query.order_by(CrmAccount.created_at.desc()).limit(200).all()
        return render_template("crm.html", page_title="CRM", accounts=accounts)

    @app.get("/crm.csv")
    def crm_csv():
        accounts = CrmAccount.query.order_by(CrmAccount.created_at.desc()).all()
        rows = [[a.id, a.account_name, a.industry or "", a.status, a.created_at.isoformat()] for a in accounts]
        return csv_response(
            "crm_accounts.csv",
            ["id", "account_name", "industry", "status", "created_at"],
            rows,
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)