# =========================================================
# UrbanHRPartners Enterprise Suite
# app.py
# FULL ENTERPRISE CONTROLLER (ALIGNED WITH MODELS)
# RENDER READY / NO SHRINK
# =========================================================

import os
from datetime import datetime

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    jsonify
)

from models import (
    db,
    init_db,
    User,
    EmployeeProfile,
    Department,
    Position,
    Client,
    Task,
    Project,
    Account,
    Transaction,
    Invoice,
    Payment,
    InventoryItem,
    InventoryMovement,
    Candidate,
    JobRequisition,
    RiskMatrix,
    Incident,
    Campaign,
    NotificationLog
)

# =========================================================
# APP CONFIGURATION
# =========================================================

def create_app():
    app = Flask(__name__)

    # -------------------------------
    # BASIC CONFIG
    # -------------------------------
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    # -------------------------------
    # DATABASE CONFIG (RENDER SAFE)
    # -------------------------------
    db_url = os.getenv("DATABASE_URL")

    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://")

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///local.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # -------------------------------
    # INIT DB
    # -------------------------------
    init_db(app)

    # =========================================================
    # DASHBOARD
    # =========================================================

    @app.route("/")
    def home():
        return redirect(url_for("dashboard"))

    @app.route("/dashboard")
    def dashboard():
        stats = {
            "clients": Client.query.count(),
            "employees": EmployeeProfile.query.count(),
            "projects": Project.query.count(),
            "invoices": Invoice.query.count(),
        }
        return render_template("dashboard.html", stats=stats)

    # =========================================================
    # CRM
    # =========================================================

    @app.route("/crm")
    def crm():
        clients = Client.query.all()
        return render_template("crm.html", clients=clients)

    @app.route("/crm/add", methods=["POST"])
    def add_client():
        client = Client(
            legal_name=request.form.get("name"),
            industry=request.form.get("industry"),
            email=request.form.get("email"),
        )
        db.session.add(client)
        db.session.commit()
        return redirect(url_for("crm"))

    # =========================================================
    # HRIS
    # =========================================================

    @app.route("/hris")
    def hris():
        employees = EmployeeProfile.query.all()
        return render_template("hris.html", employees=employees)

    # =========================================================
    # TASKS
    # =========================================================

    @app.route("/tasks")
    def tasks():
        tasks = Task.query.all()
        return render_template("tasks.html", tasks=tasks)

    # =========================================================
    # PROJECTS
    # =========================================================

    @app.route("/projects")
    def projects():
        projects = Project.query.all()
        return render_template("projects.html", projects=projects)

    # =========================================================
    # FINANCE
    # =========================================================

    @app.route("/finance")
    def finance():
        invoices = Invoice.query.all()
        payments = Payment.query.all()

        total_invoices = sum(i.total_amount for i in invoices)
        total_payments = sum(p.amount for p in payments)

        return render_template(
            "finance.html",
            invoices=invoices,
            payments=payments,
            total_invoices=total_invoices,
            total_payments=total_payments
        )

    # =========================================================
    # INVENTORY
    # =========================================================

    @app.route("/inventory")
    def inventory():
        items = InventoryItem.query.all()
        return render_template("inventory.html", items=items)

    # =========================================================
    # ATS
    # =========================================================

    @app.route("/ats")
    def ats():
        candidates = Candidate.query.all()
        return render_template("ats.html", candidates=candidates)

    # =========================================================
    # SG-SST
    # =========================================================

    @app.route("/sgsst")
    def sgsst():
        incidents = Incident.query.all()
        risks = RiskMatrix.query.all()
        return render_template("sgsst.html", incidents=incidents, risks=risks)

    # =========================================================
    # MARKETING
    # =========================================================

    @app.route("/marketing")
    def marketing():
        campaigns = Campaign.query.all()
        return render_template("marketing.html", campaigns=campaigns)

    # =========================================================
    # API HEALTH CHECK
    # =========================================================

    @app.route("/health")
    def health():
        return jsonify({"status": "OK", "time": datetime.utcnow().isoformat()})

    return app


# =========================================================
# RUN APP
# =========================================================

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
