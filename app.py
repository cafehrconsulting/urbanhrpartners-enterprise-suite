# =========================================================
# UrbanHRPartners Enterprise Suite
# app.py
# Full enterprise-safe application controller
# Render-ready / HTML deploy-ready / no shrinking
# =========================================================

import os
from datetime import datetime, date
from pathlib import Path
from typing import Any

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from jinja2 import TemplateNotFound
from sqlalchemy import inspect, text
from werkzeug.utils import secure_filename

# =========================================================
# DATABASE
# =========================================================

db = SQLAlchemy()

# =========================================================
# HELPERS / PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
CLIENT_PROGRAMS_FOLDER = BASE_DIR / "client_programs"
STATIC_FOLDER = BASE_DIR / "static"
TEMPLATES_FOLDER = BASE_DIR / "templates"

UPLOAD_FOLDER.mkdir(exist_ok=True)
CLIENT_PROGRAMS_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    "pdf",
    "png",
    "jpg",
    "jpeg",
    "gif",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "txt",
    "csv",
}

# =========================================================
# CRM GLOBAL OPTION SETS
# =========================================================

COUNTRY_OPTIONS = [
    "Colombia",
    "United States",
    "Canada",
    "Mexico",
    "Argentina",
    "Brazil",
    "Chile",
    "Peru",
    "Ecuador",
    "Panama",
    "Costa Rica",
    "Dominican Republic",
    "Spain",
    "United Kingdom",
    "Germany",
    "France",
    "Italy",
    "Netherlands",
    "Portugal",
    "Other",
]

LANGUAGE_OPTIONS = [
    "Spanish",
    "English",
    "Portuguese",
    "French",
    "German",
    "Italian",
    "Dutch",
    "Mandarin Chinese",
    "Cantonese",
    "Japanese",
    "Korean",
    "Hebrew",
    "Other",
]

COMMON_INDUSTRIES = [
    "Accounting",
    "Advertising",
    "Aerospace",
    "Agriculture",
    "Architecture",
    "Artificial Intelligence",
    "Automotive",
    "Aviation",
    "Banking",
    "Biotechnology",
    "Business Consulting",
    "Cannabis",
    "Chemical",
    "Civil Engineering",
    "Cleaning Services",
    "Cloud Computing",
    "Construction",
    "Consumer Goods",
    "Cybersecurity",
    "Data Analytics",
    "Defense",
    "Dental",
    "Distribution",
    "E-commerce",
    "Education",
    "Electrical",
    "Electronics",
    "Energy",
    "Engineering",
    "Entertainment",
    "Environmental Services",
    "Event Management",
    "Fashion",
    "Finance",
    "Financial Services",
    "Food and Beverage",
    "Forestry",
    "Freight",
    "Gaming",
    "Government",
    "Graphic Design",
    "Health and Safety",
    "Healthcare",
    "Home Services",
    "Hospitality",
    "Human Resources",
    "Import / Export",
    "Industrial Services",
    "Information Technology",
    "Insurance",
    "Interior Design",
    "International Trade",
    "Investment",
    "Janitorial",
    "Legal Services",
    "Logistics",
    "Luxury Goods",
    "Machinery",
    "Manufacturing",
    "Marine",
    "Marketing",
    "Media",
    "Medical Devices",
    "Mining",
    "Mobile Technology",
    "Nonprofit",
    "Oil and Gas",
    "Packaging",
    "Payroll Services",
    "Pet Services",
    "Pharmaceutical",
    "Printing",
    "Private Security",
    "Public Relations",
    "Real Estate",
    "Recruiting",
    "Renewable Energy",
    "Research",
    "Restaurant",
    "Retail",
    "Risk Management",
    "SaaS",
    "Safety Training",
    "Security Services",
    "Software Development",
    "Sports",
    "Staffing",
    "Supply Chain",
    "Tattoo Supplies",
    "Tax Services",
    "Telecommunications",
    "Textiles",
    "Tourism",
    "Training and Development",
    "Transportation",
    "Travel",
    "Veterinary",
    "Warehousing",
    "Wholesale",
    "Wellness",
    "Other",
]

TAX_ID_OPTIONS_BY_COUNTRY = {
    "Colombia": ["RUT", "NIT", "CEDULA", "PASSPORT", "OTHER"],
    "United States": ["EIN", "TIN", "SSN", "ITIN", "OTHER"],
    "Canada": ["BN", "GST/HST", "OTHER"],
    "Mexico": ["RFC", "CURP", "OTHER"],
    "Brazil": ["CNPJ", "CPF", "OTHER"],
    "Argentina": ["CUIT", "CUIL", "OTHER"],
    "Chile": ["RUT", "OTHER"],
    "Peru": ["RUC", "DNI", "OTHER"],
    "Spain": ["NIF", "CIF", "NIE", "OTHER"],
    "United Kingdom": ["UTR", "VAT", "COMPANY NUMBER", "OTHER"],
    "Germany": ["VAT", "STEUERNUMMER", "OTHER"],
    "France": ["SIREN", "SIRET", "VAT", "OTHER"],
    "Italy": ["PIVA", "CF", "OTHER"],
    "Netherlands": ["VAT", "KVK", "OTHER"],
    "Portugal": ["NIF", "OTHER"],
    "Other": ["VAT", "TIN", "TAX ID", "OTHER"],
}

DEFAULT_TAX_ID_OPTIONS = ["RUT", "NIT", "EIN", "TIN", "VAT", "OTHER"]

# =========================================================
# OPTIONAL XIOMY IMPORT
# =========================================================

try:
    from services.xiomy_ai import XiomyAI as ImportedXiomyAI
except Exception:
    ImportedXiomyAI = None


class SafeXiomyAI:
    def __init__(self, db_instance):
        self.db = db_instance
        self.name = "XIOMY"
        self.version = "1.0 Enterprise"
        self.status = "active"
        self.created = datetime.utcnow()

    def system_status(self):
        return {
            "ai_name": self.name,
            "version": self.version,
            "status": self.status,
            "created": self.created.isoformat(),
        }

    def greeting(self):
        hour = datetime.now().hour
        if hour < 12:
            period = "Good morning"
        elif hour < 18:
            period = "Good afternoon"
        else:
            period = "Good evening"
        return f"{period}. XIOMY Executive AI is ready to assist UrbanHRPartners Enterprise operations."

    def insight(self):
        return (
            "Cross-module intelligence is active. Monitor CRM pipeline, HR performance, "
            "recruiting velocity, SG-SST compliance, finance forecasting, and enterprise "
            "growth indicators from one executive environment."
        )


def build_xiomy_instance(db_instance):
    if ImportedXiomyAI is None:
        return SafeXiomyAI(db_instance)

    try:
        instance = ImportedXiomyAI(db_instance)
        return instance
    except Exception:
        return SafeXiomyAI(db_instance)


# =========================================================
# OPTIONAL MODELS IMPORT
# =========================================================

Client = None
CommunicationLog = None
Project = None
InventoryItem = None
Finance = None
Invoice = None
Task = None
MarketingCampaign = None
CalendarEvent = None
Candidate = None
EmployeeProfile = None
PointLog = None
SOPRequirement = None
DisciplinaryRecord = None
OrientationChecklist = None
AssetAssignment = None
PolicyAcknowledgement = None
RiskMatrixItem = None
InspectionRecord = None
IncidentRecord = None
TrainingRecord = None
User = None
models_db = None

try:
    from models import (
        db as models_db,
        Client,
        CommunicationLog,
        Project,
        InventoryItem,
        Finance,
        Invoice,
        Task,
        MarketingCampaign,
        CalendarEvent,
        Candidate,
        EmployeeProfile,
        PointLog,
        SOPRequirement,
        DisciplinaryRecord,
        OrientationChecklist,
        AssetAssignment,
        PolicyAcknowledgement,
        RiskMatrixItem,
        InspectionRecord,
        IncidentRecord,
        TrainingRecord,
        User,
    )
except Exception:
    try:
        from models import db as models_db  # type: ignore
    except Exception:
        models_db = None

# =========================================================
# CORE UTILITIES
# =========================================================


def normalize_database_url(raw_url: str | None) -> str:
    if not raw_url:
        return f"sqlite:///{BASE_DIR / 'urbanhrpartners.db'}"
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql://", 1)
    return raw_url


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def safe_count(model: Any) -> int:
    try:
        if model is None:
            return 0
        return db.session.query(model).count()
    except Exception:
        return 0


def safe_all(model: Any, limit: int | None = None, order_attr: str | None = None):
    try:
        if model is None:
            return []
        query = model.query
        if order_attr and hasattr(model, order_attr):
            query = query.order_by(getattr(model, order_attr).desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    except Exception:
        return []


def safe_first(model: Any, **filters):
    try:
        if model is None:
            return None
        return model.query.filter_by(**filters).first()
    except Exception:
        return None


def parse_date(value: str | None):
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def parse_datetime(value: str | None):
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(value, fmt)
            if fmt == "%Y-%m-%d":
                return datetime.combine(parsed.date(), datetime.min.time())
            return parsed
        except ValueError:
            continue
    return None


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except Exception:
        return default


def as_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, ""):
            return default
        return int(value)
    except Exception:
        return default


def template_exists(template_name: str) -> bool:
    return (TEMPLATES_FOLDER / template_name).exists()


def render_or_fallback(template_name: str, **context):
    if template_exists(template_name):
        try:
            return render_template(template_name, **context)
        except TemplateNotFound:
            pass
    fallback_template = "template_missing.html"
    if template_exists(fallback_template):
        return render_template(fallback_template, template_name=template_name, **context)
    return f"Missing template: {template_name}", 500


def commit_with_feedback(success_message: str, error_prefix: str, redirect_endpoint: str):
    try:
        db.session.commit()
        flash(success_message, "success")
    except Exception as exc:
        db.session.rollback()
        flash(f"{error_prefix}: {exc}", "danger")
    return redirect(url_for(redirect_endpoint))


def get_tax_id_options_for_country(country: str | None) -> list[str]:
    if not country:
        return DEFAULT_TAX_ID_OPTIONS
    return TAX_ID_OPTIONS_BY_COUNTRY.get(country, DEFAULT_TAX_ID_OPTIONS)


# =========================================================
# XIOMY SAFE HELPERS
# =========================================================

def safe_xiomy_greeting(xiomy_ai):
    try:
        if hasattr(xiomy_ai, "greeting") and callable(getattr(xiomy_ai, "greeting")):
            return xiomy_ai.greeting()
    except Exception:
        pass

    return "XIOMY Executive AI is ready to support UrbanHRPartners operations."


def safe_xiomy_insight(xiomy_ai):
    try:
        if hasattr(xiomy_ai, "insight") and callable(getattr(xiomy_ai, "insight")):
            return xiomy_ai.insight()
    except Exception:
        pass

    return (
        "Executive enterprise monitoring is active. Review CRM performance, workforce data, "
        "recruiting progress, SG-SST compliance, financial health, and growth indicators "
        "from the dashboard."
    )


def safe_xiomy_status(xiomy_ai):
    try:
        if hasattr(xiomy_ai, "system_status") and callable(getattr(xiomy_ai, "system_status")):
            status = xiomy_ai.system_status()
            if isinstance(status, dict):
                return status
    except Exception:
        pass

    return {
        "ai_name": "XIOMY",
        "version": "1.0 Enterprise",
        "status": "active",
        "created": datetime.utcnow().isoformat(),
    }


# =========================================================
# MODEL FIELD HELPERS
# =========================================================

def model_columns(model: Any) -> set[str]:
    try:
        return {c.key for c in inspect(model).columns}
    except Exception:
        return set()


def filter_payload_by_columns(model: Any, payload: dict) -> dict:
    cols = model_columns(model)
    return {k: v for k, v in payload.items() if k in cols}


# =========================================================
# STARTUP SCHEMA SAFETY
# =========================================================

def ensure_clients_table_extensions():
    """
    Ensures legacy deployed databases receive the new CRM columns required
    by the updated client intake form.
    """
    try:
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()
        if "clients" not in table_names:
            return

        existing_columns = {col["name"] for col in inspector.get_columns("clients")}
        statements = []

        if "industry" not in existing_columns:
            statements.append("ALTER TABLE clients ADD COLUMN industry VARCHAR(200)")
        if "country" not in existing_columns:
            statements.append("ALTER TABLE clients ADD COLUMN country VARCHAR(100)")
        if "language" not in existing_columns:
            statements.append("ALTER TABLE clients ADD COLUMN language VARCHAR(100)")
        if "tax_id_type" not in existing_columns:
            statements.append("ALTER TABLE clients ADD COLUMN tax_id_type VARCHAR(50)")
        if "tax_id_number" not in existing_columns:
            statements.append("ALTER TABLE clients ADD COLUMN tax_id_number VARCHAR(100)")

        for stmt in statements:
            db.session.execute(text(stmt))

        if statements:
            db.session.commit()

        # Backfill safe defaults
        try:
            if "country" in {col["name"] for col in inspect(db.engine).get_columns("clients")}:
                db.session.execute(
                    text("UPDATE clients SET country = 'Colombia' WHERE country IS NULL OR country = ''")
                )
            if "language" in {col["name"] for col in inspect(db.engine).get_columns("clients")}:
                db.session.execute(
                    text("UPDATE clients SET language = 'Spanish' WHERE language IS NULL OR language = ''")
                )
            db.session.commit()
        except Exception:
            db.session.rollback()

    except Exception:
        db.session.rollback()


# =========================================================
# DASHBOARD / MODULE CONTEXT BUILDERS
# =========================================================

def build_dashboard_stats():
    total_clients = safe_count(Client)
    total_projects = safe_count(Project)
    total_tasks = safe_count(Task)
    total_candidates = safe_count(Candidate)
    total_employees = safe_count(EmployeeProfile)
    total_campaigns = safe_count(MarketingCampaign)
    total_incidents = safe_count(IncidentRecord)
    total_invoices = safe_count(Invoice)
    inventory_items = safe_count(InventoryItem)

    open_tasks = 0
    total_revenue = 0.0

    try:
        if Task is not None:
            tasks = Task.query.all()
            open_tasks = len([
                t for t in tasks
                if str(getattr(t, "status", "")).lower() not in {"completed", "closed", "done"}
            ])
    except Exception:
        open_tasks = 0

    try:
        if Invoice is not None:
            invoices = Invoice.query.all()
            total_revenue = sum(as_float(getattr(i, "amount", 0.0), 0.0) for i in invoices)
    except Exception:
        total_revenue = 0.0

    return {
        "total_clients": total_clients,
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "open_tasks": open_tasks,
        "inventory_items": inventory_items,
        "total_invoices": total_invoices,
        "total_revenue": round(total_revenue, 2),
        "total_candidates": total_candidates,
        "total_employees": total_employees,
        "total_campaigns": total_campaigns,
        "total_incidents": total_incidents,
    }


def build_crm_context():
    clients = safe_all(Client, order_attr="id")
    communication_logs = safe_all(CommunicationLog, limit=50, order_attr="id")
    projects = safe_all(Project, limit=50, order_attr="id")
    tasks = safe_all(Task, limit=50, order_attr="id")

    pipeline_value = 0.0
    try:
        for project in projects:
            pipeline_value += as_float(getattr(project, "budget", getattr(project, "estimated_value", 0.0)), 0.0)
    except Exception:
        pipeline_value = 0.0

    crm_stats = {
        "total_clients": len(clients),
        "active_projects": len(projects),
        "communications": len(communication_logs),
        "tasks": len(tasks),
        "pipeline_value": round(pipeline_value, 2),
    }

    return {
        "clients": clients,
        "communication_logs": communication_logs,
        "communications": communication_logs,
        "projects": projects,
        "tasks": tasks,
        "crm_stats": crm_stats,
        "country_options": COUNTRY_OPTIONS,
        "language_options": LANGUAGE_OPTIONS,
        "industry_options": COMMON_INDUSTRIES,
        "default_tax_id_options": DEFAULT_TAX_ID_OPTIONS,
        "tax_id_options_by_country": TAX_ID_OPTIONS_BY_COUNTRY,
    }


def build_hris_context():
    employees = safe_all(EmployeeProfile, order_attr="id")
    point_logs = safe_all(PointLog, limit=50, order_attr="id")
    sop_requirements = safe_all(SOPRequirement, limit=50, order_attr="id")
    disciplinary_records = safe_all(DisciplinaryRecord, limit=50, order_attr="id")

    active_employees = 0
    try:
        active_employees = len([
            e for e in employees
            if str(getattr(e, "status", "Active")).lower() in {"active", "current", "working"}
        ])
    except Exception:
        active_employees = 0

    workforce_stats = {
        "total_employees": len(employees),
        "active_employees": active_employees,
        "disciplinary_cases": len(disciplinary_records),
        "point_logs": len(point_logs),
        "sop_requirements": len(sop_requirements),
    }

    return {
        "employees": employees,
        "point_logs": point_logs,
        "sop_requirements": sop_requirements,
        "disciplinary_records": disciplinary_records,
        "workforce_stats": workforce_stats,
    }


def build_ats_context():
    candidates = safe_all(Candidate, order_attr="id")
    orientation_items = safe_all(OrientationChecklist, limit=50, order_attr="id")

    ats_stats = {
        "total_candidates": len(candidates),
        "interview_stage": len([
            c for c in candidates
            if str(getattr(c, "stage", "")).lower() in {"interview", "interviewing"}
        ]),
        "offers": len([
            c for c in candidates
            if str(getattr(c, "stage", "")).lower() in {"offer", "offered"}
        ]),
        "onboarding_ready": len(orientation_items),
    }

    return {
        "candidates": candidates,
        "orientation_items": orientation_items,
        "ats_stats": ats_stats,
    }


def build_orientation_context():
    checklists = safe_all(OrientationChecklist, limit=100, order_attr="id")
    acknowledgements = safe_all(PolicyAcknowledgement, limit=100, order_attr="id")
    assignments = safe_all(AssetAssignment, limit=100, order_attr="id")

    orientation_stats = {
        "checklists": len(checklists),
        "acknowledgements": len(acknowledgements),
        "assets_assigned": len(assignments),
    }

    return {
        "orientation_checklists": checklists,
        "policy_acknowledgements": acknowledgements,
        "asset_assignments": assignments,
        "orientation_stats": orientation_stats,
    }


def build_sgsst_context():
    risk_items = safe_all(RiskMatrixItem, limit=100, order_attr="id")
    inspections = safe_all(InspectionRecord, limit=100, order_attr="id")
    incidents = safe_all(IncidentRecord, limit=100, order_attr="id")
    trainings = safe_all(TrainingRecord, limit=100, order_attr="id")

    sgsst_stats = {
        "risk_items": len(risk_items),
        "inspections": len(inspections),
        "incidents": len(incidents),
        "trainings": len(trainings),
    }

    return {
        "risk_items": risk_items,
        "inspections": inspections,
        "incidents": incidents,
        "trainings": trainings,
        "sgsst_stats": sgsst_stats,
    }


def build_inventory_context():
    items = safe_all(InventoryItem, limit=200, order_attr="id")

    total_value = 0.0
    low_stock = 0
    try:
        for item in items:
            qty = as_float(getattr(item, "quantity", 0), 0)
            unit_cost = as_float(getattr(item, "unit_cost", 0), 0)
            total_value += qty * unit_cost
            if qty <= as_float(getattr(item, "reorder_level", 0), 0):
                low_stock += 1
    except Exception:
        total_value = 0.0
        low_stock = 0

    inventory_stats = {
        "total_items": len(items),
        "low_stock_items": low_stock,
        "inventory_value": round(total_value, 2),
    }

    return {
        "inventory_items": items,
        "inventory_stats": inventory_stats,
    }


def build_finance_context():
    invoices = safe_all(Invoice, limit=200, order_attr="id")
    ledger_entries = safe_all(Finance, limit=200, order_attr="id")

    invoice_total = 0.0
    ledger_total = 0.0
    paid_total = 0.0
    outstanding_total = 0.0

    try:
        for invoice in invoices:
            amount = as_float(getattr(invoice, "amount", 0.0), 0.0)
            invoice_total += amount
            status = str(getattr(invoice, "status", "")).lower()
            if status in {"paid", "closed", "collected"}:
                paid_total += amount
            else:
                outstanding_total += amount
    except Exception:
        pass

    try:
        for entry in ledger_entries:
            ledger_total += as_float(getattr(entry, "amount", 0.0), 0.0)
    except Exception:
        pass

    finance_stats = {
        "invoice_count": len(invoices),
        "ledger_entries": len(ledger_entries),
        "invoice_total": round(invoice_total, 2),
        "paid_total": round(paid_total, 2),
        "outstanding_total": round(outstanding_total, 2),
        "ledger_total": round(ledger_total, 2),
    }

    return {
        "invoices": invoices,
        "ledger_entries": ledger_entries,
        "finance_stats": finance_stats,
    }


def build_marketing_context():
    campaigns = safe_all(MarketingCampaign, limit=100, order_attr="id")
    marketing_stats = {
        "total_campaigns": len(campaigns),
        "active_campaigns": len([
            c for c in campaigns
            if str(getattr(c, "status", "")).lower() in {"active", "running", "live"}
        ]),
    }
    return {
        "campaigns": campaigns,
        "marketing_stats": marketing_stats,
    }


def build_calendar_context():
    events = safe_all(CalendarEvent, limit=100, order_attr="id")
    calendar_stats = {
        "upcoming_events": len(events),
    }
    return {
        "calendar_events": events,
        "calendar_stats": calendar_stats,
    }


def build_reports_context():
    dashboard_stats = build_dashboard_stats()
    return {
        "dashboard_stats": dashboard_stats,
        "generated_at": datetime.utcnow(),
    }


# =========================================================
# APP FACTORY
# =========================================================

def create_app():
    app = Flask(
        __name__,
        template_folder=str(TEMPLATES_FOLDER),
        static_folder=str(STATIC_FOLDER),
    )

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "urbanhrpartners-enterprise-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = normalize_database_url(os.getenv("DATABASE_URL"))
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
    app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

    db.init_app(app)

    if models_db is not None and models_db is not db:
        try:
            models_db.init_app(app)
        except Exception:
            pass

    xiomy_ai = build_xiomy_instance(db)

    @app.context_processor
    def inject_globals():
        return {
            "current_year": datetime.utcnow().year,
            "today": date.today(),
            "dashboard_quick_stats": build_dashboard_stats(),
        }

    @app.before_request
    def ensure_directories():
        UPLOAD_FOLDER.mkdir(exist_ok=True)
        CLIENT_PROGRAMS_FOLDER.mkdir(exist_ok=True)

    # =====================================================
    # STARTUP DATABASE SAFETY
    # =====================================================

    with app.app_context():
        try:
            db.create_all()
        except Exception:
            pass

        try:
            ensure_clients_table_extensions()
        except Exception:
            db.session.rollback()

        if User is not None:
            try:
                admin_email = os.getenv("ADMIN_EMAIL", "admin@urbanhrconsulting.cloud")
                admin_password = os.getenv("ADMIN_PASSWORD", "Admin123!")
                existing_admin = User.query.filter_by(email=admin_email).first()
                if not existing_admin:
                    user_kwargs = {}
                    columns = model_columns(User)

                    if "name" in columns:
                        user_kwargs["name"] = "System Administrator"
                    if "email" in columns:
                        user_kwargs["email"] = admin_email
                    if "password" in columns:
                        user_kwargs["password"] = admin_password
                    elif "password_hash" in columns:
                        user_kwargs["password_hash"] = admin_password
                    if "role" in columns:
                        user_kwargs["role"] = "admin"
                    if "is_admin" in columns:
                        user_kwargs["is_admin"] = True

                    db.session.add(User(**user_kwargs))
                    db.session.commit()
            except Exception:
                db.session.rollback()

    # =====================================================
    # CORE ROUTES
    # =====================================================

    @app.route("/")
    def index():
        return redirect(url_for("dashboard"))

    @app.route("/health")
    def health():
        return jsonify({
            "status": "ok",
            "application": "UrbanHRPartners Enterprise Suite",
            "timestamp": datetime.utcnow().isoformat(),
        })

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # =====================================================
    # DASHBOARD
    # =====================================================

    @app.route("/dashboard")
    def dashboard():
        dashboard_stats = build_dashboard_stats()
        recent_clients = safe_all(Client, limit=5, order_attr="id")
        recent_projects = safe_all(Project, limit=5, order_attr="id")
        recent_candidates = safe_all(Candidate, limit=5, order_attr="id")
        recent_invoices = safe_all(Invoice, limit=5, order_attr="id")
        recent_incidents = safe_all(IncidentRecord, limit=5, order_attr="id")

        return render_or_fallback(
            "dashboard.html",
            dashboard_stats=dashboard_stats,
            recent_clients=recent_clients,
            recent_projects=recent_projects,
            recent_candidates=recent_candidates,
            recent_invoices=recent_invoices,
            recent_incidents=recent_incidents,
            xiomy_greeting=safe_xiomy_greeting(xiomy_ai),
            xiomy_insight=safe_xiomy_insight(xiomy_ai),
        )

    # =====================================================
    # CRM ROUTES
    # =====================================================

    @app.route("/crm")
    def crm():
        return render_or_fallback("crm.html", **build_crm_context())

    @app.route("/crm/client/create", methods=["POST"])
    def create_client():
        if Client is None:
            flash("Client model is not available in models.py.", "danger")
            return redirect(url_for("crm"))

        country = (request.form.get("country") or "Colombia").strip()
        language = (request.form.get("language") or "Spanish").strip()
        submitted_tax_id_type = (request.form.get("tax_id_type") or "").strip()
        tax_id_options = get_tax_id_options_for_country(country)

        tax_id_type = submitted_tax_id_type if submitted_tax_id_type in tax_id_options else (
            tax_id_options[0] if tax_id_options else "OTHER"
        )

        raw_payload = {
            "name": (request.form.get("name") or "").strip(),
            "company_name": (request.form.get("company_name") or "").strip(),
            "contact_person": (request.form.get("contact_person") or "").strip(),
            "email": (request.form.get("email") or "").strip(),
            "phone": (request.form.get("phone") or "").strip(),
            "industry": (request.form.get("industry") or "").strip(),
            "country": country,
            "language": language,
            "tax_id_type": tax_id_type,
            "tax_id_number": (request.form.get("tax_id_number") or "").strip(),
            "status": (request.form.get("status") or "Prospect").strip(),
            "address": (request.form.get("address") or "").strip(),
            "region": (request.form.get("region") or "").strip(),
            "risk_level": (request.form.get("risk_level") or "").strip(),
            "needs": (request.form.get("needs") or "").strip(),
            "notes": (request.form.get("notes") or "").strip(),
        }

        if not raw_payload["name"] and not raw_payload["company_name"]:
            flash("Client name or company name is required.", "danger")
            return redirect(url_for("crm"))

        payload = filter_payload_by_columns(Client, raw_payload)
        client_columns = model_columns(Client)

        if "name" in client_columns and not payload.get("name"):
            payload["name"] = raw_payload["company_name"] or "Unnamed Client"

        db.session.add(Client(**payload))
        return commit_with_feedback("Client created successfully.", "Unable to create client", "crm")

    @app.route("/crm/communication-log/create", methods=["POST"])
    def create_communication_log():
        if CommunicationLog is None:
            flash("CommunicationLog model is not available in models.py.", "danger")
            return redirect(url_for("crm"))

        client_id = request.form.get("client_id", type=int)
        if not client_id:
            flash("Client is required before saving a communication log.", "danger")
            return redirect(url_for("crm"))

        if Client is not None:
            client = Client.query.get(client_id)
            if not client:
                flash("Selected client was not found.", "danger")
                return redirect(url_for("crm"))

        raw_payload = {
            "client_id": client_id,
            "client_name": (request.form.get("client_name") or "").strip(),
            "channel": (request.form.get("channel") or request.form.get("communication_type") or "General").strip(),
            "communication_type": (request.form.get("communication_type") or request.form.get("channel") or "General").strip(),
            "direction": (request.form.get("direction") or "Outbound").strip(),
            "contact_person": (request.form.get("contact_person") or "").strip(),
            "subject": (request.form.get("subject") or "").strip(),
            "summary": (request.form.get("summary") or "").strip(),
            "message": (request.form.get("message") or "").strip(),
            "action_items": (request.form.get("action_items") or "").strip(),
            "action_required": request.form.get("action_required") == "on",
            "log_date": parse_date(request.form.get("log_date")) or date.today(),
            "follow_up_date": parse_date(request.form.get("follow_up_date")),
        }

        payload = filter_payload_by_columns(CommunicationLog, raw_payload)
        db.session.add(CommunicationLog(**payload))
        return commit_with_feedback("Communication log created successfully.", "Unable to save communication log", "crm")

    @app.route("/crm/project/create", methods=["POST"])
    def create_project():
        if Project is None:
            flash("Project model is not available in models.py.", "danger")
            return redirect(url_for("crm"))

        raw_payload = {
            "client_id": request.form.get("client_id", type=int),
            "client_name": (request.form.get("client_name") or "").strip(),
            "name": (request.form.get("name") or request.form.get("project_name") or "").strip(),
            "project_name": (request.form.get("project_name") or request.form.get("name") or "").strip(),
            "description": (request.form.get("description") or "").strip(),
            "status": (request.form.get("status") or "Planned").strip(),
            "estimated_value": as_float(request.form.get("estimated_value"), 0.0),
            "budget": as_float(request.form.get("budget") or request.form.get("estimated_value"), 0.0),
            "start_date": parse_date(request.form.get("start_date")),
            "end_date": parse_date(request.form.get("end_date")),
        }

        payload = filter_payload_by_columns(Project, raw_payload)
        db.session.add(Project(**payload))
        return commit_with_feedback("Project created successfully.", "Unable to create project", "crm")

    @app.route("/crm/task/create", methods=["POST"])
    def create_task():
        if Task is None:
            flash("Task model is not available in models.py.", "danger")
            return redirect(url_for("crm"))

        raw_payload = {
            "title": (request.form.get("title") or "").strip(),
            "description": (request.form.get("description") or request.form.get("notes") or "").strip(),
            "notes": (request.form.get("notes") or "").strip(),
            "status": (request.form.get("status") or "Open").strip(),
            "priority": (request.form.get("priority") or "Normal").strip(),
            "due_date": parse_date(request.form.get("due_date")),
            "client_id": request.form.get("client_id", type=int),
            "client_name": (request.form.get("client_name") or "").strip(),
            "project_id": request.form.get("project_id", type=int),
        }

        if not raw_payload["title"]:
            flash("Task title is required.", "danger")
            return redirect(url_for("crm"))

        payload = filter_payload_by_columns(Task, raw_payload)
        db.session.add(Task(**payload))
        return commit_with_feedback("Task created successfully.", "Unable to create task", "crm")

    # =====================================================
    # HRIS ROUTES
    # =====================================================

    @app.route("/hris")
    def hris():
        return render_or_fallback("hris.html", **build_hris_context())

    @app.route("/hris/employee/create", methods=["POST"])
    def create_employee_profile():
        if EmployeeProfile is None:
            flash("EmployeeProfile model is not available in models.py.", "danger")
            return redirect(url_for("hris"))

        raw_payload = {
            "employee_id": (request.form.get("employee_id") or "").strip(),
            "first_name": (request.form.get("first_name") or "").strip(),
            "last_name": (request.form.get("last_name") or "").strip(),
            "full_name": (request.form.get("full_name") or "").strip(),
            "email": (request.form.get("email") or "").strip(),
            "phone": (request.form.get("phone") or "").strip(),
            "position": (request.form.get("position") or "").strip(),
            "department": (request.form.get("department") or "").strip(),
            "status": (request.form.get("status") or "Active").strip(),
            "hire_date": parse_date(request.form.get("hire_date")),
            "salary": as_float(request.form.get("salary"), 0.0),
        }

        employee_columns = model_columns(EmployeeProfile)
        if "full_name" in employee_columns and not raw_payload["full_name"]:
            raw_payload["full_name"] = f"{raw_payload['first_name']} {raw_payload['last_name']}".strip()

        payload = filter_payload_by_columns(EmployeeProfile, raw_payload)
        db.session.add(EmployeeProfile(**payload))
        return commit_with_feedback("Employee profile created successfully.", "Unable to create employee profile", "hris")

    @app.route("/hris/point-log/create", methods=["POST"])
    def create_point_log():
        if PointLog is None:
            flash("PointLog model is not available in models.py.", "danger")
            return redirect(url_for("hris"))

        raw_payload = {
            "employee_id": request.form.get("employee_id", type=int),
            "points": as_int(request.form.get("points"), 0),
            "reason": (request.form.get("reason") or "").strip(),
            "category": (request.form.get("category") or "Performance").strip(),
            "log_date": parse_date(request.form.get("log_date")) or date.today(),
        }

        payload = filter_payload_by_columns(PointLog, raw_payload)
        db.session.add(PointLog(**payload))
        return commit_with_feedback("Point log created successfully.", "Unable to create point log", "hris")

    @app.route("/hris/disciplinary-record/create", methods=["POST"])
    def create_disciplinary_record():
        if DisciplinaryRecord is None:
            flash("DisciplinaryRecord model is not available in models.py.", "danger")
            return redirect(url_for("hris"))

        raw_payload = {
            "employee_id": request.form.get("employee_id", type=int),
            "case_type": (request.form.get("case_type") or "").strip(),
            "description": (request.form.get("description") or "").strip(),
            "action_taken": (request.form.get("action_taken") or "").strip(),
            "record_date": parse_date(request.form.get("record_date")) or date.today(),
            "status": (request.form.get("status") or "Open").strip(),
        }

        payload = filter_payload_by_columns(DisciplinaryRecord, raw_payload)
        db.session.add(DisciplinaryRecord(**payload))
        return commit_with_feedback("Disciplinary record created successfully.", "Unable to create disciplinary record", "hris")

    @app.route("/hris/sop-requirement/create", methods=["POST"])
    def create_sop_requirement():
        if SOPRequirement is None:
            flash("SOPRequirement model is not available in models.py.", "danger")
            return redirect(url_for("hris"))

        raw_payload = {
            "job_title": (request.form.get("job_title") or "").strip(),
            "title": (request.form.get("title") or "").strip(),
            "requirement": (request.form.get("requirement") or "").strip(),
            "description": (request.form.get("description") or "").strip(),
            "required": request.form.get("required") == "on",
        }

        payload = filter_payload_by_columns(SOPRequirement, raw_payload)
        db.session.add(SOPRequirement(**payload))
        return commit_with_feedback("SOP requirement created successfully.", "Unable to create SOP requirement", "hris")

    # =====================================================
    # ATS ROUTES
    # =====================================================

    @app.route("/ats")
    def ats():
        return render_or_fallback("ats.html", **build_ats_context())

    @app.route("/ats/candidate/create", methods=["POST"])
    def create_candidate():
        if Candidate is None:
            flash("Candidate model is not available in models.py.", "danger")
            return redirect(url_for("ats"))

        resume_filename = None
        uploaded_resume = request.files.get("resume")
        if uploaded_resume and uploaded_resume.filename and allowed_file(uploaded_resume.filename):
            resume_filename = secure_filename(uploaded_resume.filename)
            uploaded_resume.save(UPLOAD_FOLDER / resume_filename)

        raw_payload = {
            "first_name": (request.form.get("first_name") or "").strip(),
            "last_name": (request.form.get("last_name") or "").strip(),
            "full_name": (request.form.get("full_name") or "").strip(),
            "email": (request.form.get("email") or "").strip(),
            "phone": (request.form.get("phone") or "").strip(),
            "position_applied": (request.form.get("position_applied") or "").strip(),
            "stage": (request.form.get("stage") or "Applied").strip(),
            "status": (request.form.get("status") or "New").strip(),
            "notes": (request.form.get("notes") or "").strip(),
            "resume_filename": resume_filename,
        }

        candidate_columns = model_columns(Candidate)
        if "full_name" in candidate_columns and not raw_payload["full_name"]:
            raw_payload["full_name"] = f"{raw_payload['first_name']} {raw_payload['last_name']}".strip()

        payload = filter_payload_by_columns(Candidate, raw_payload)
        db.session.add(Candidate(**payload))
        return commit_with_feedback("Candidate created successfully.", "Unable to create candidate", "ats")

    @app.route("/ats/candidate/<int:candidate_id>/promote", methods=["POST"])
    def promote_candidate_to_orientation(candidate_id: int):
        if Candidate is None:
            flash("Candidate model is not available in models.py.", "danger")
            return redirect(url_for("ats"))

        candidate = Candidate.query.get_or_404(candidate_id)

        try:
            if hasattr(candidate, "stage"):
                candidate.stage = "Orientation"
            if hasattr(candidate, "status"):
                candidate.status = "Onboarding"

            if OrientationChecklist is not None:
                checklist_payload = {
                    "candidate_id": candidate_id,
                    "employee_name": getattr(candidate, "full_name", None) or getattr(candidate, "first_name", ""),
                    "title": "Pre-Orientation Readiness",
                    "status": "Pending",
                }
                checklist_payload = filter_payload_by_columns(OrientationChecklist, checklist_payload)
                db.session.add(OrientationChecklist(**checklist_payload))

            db.session.commit()
            flash("Candidate promoted to orientation successfully.", "success")
        except Exception as exc:
            db.session.rollback()
            flash(f"Unable to promote candidate: {exc}", "danger")

        return redirect(url_for("ats"))

    # =====================================================
    # ORIENTATION ROUTES
    # =====================================================

    @app.route("/orientation")
    def orientation():
        return render_or_fallback("orientation.html", **build_orientation_context())

    @app.route("/orientation/checklist/create", methods=["POST"])
    def create_orientation_checklist():
        if OrientationChecklist is None:
            flash("OrientationChecklist model is not available in models.py.", "danger")
            return redirect(url_for("orientation"))

        raw_payload = {
            "candidate_id": request.form.get("candidate_id", type=int),
            "employee_id": request.form.get("employee_id", type=int),
            "employee_name": (request.form.get("employee_name") or "").strip(),
            "title": (request.form.get("title") or "Orientation Task").strip(),
            "description": (request.form.get("description") or "").strip(),
            "status": (request.form.get("status") or "Pending").strip(),
            "due_date": parse_date(request.form.get("due_date")),
        }

        payload = filter_payload_by_columns(OrientationChecklist, raw_payload)
        db.session.add(OrientationChecklist(**payload))
        return commit_with_feedback("Orientation checklist item created successfully.", "Unable to create orientation checklist item", "orientation")

    @app.route("/orientation/policy-acknowledgement/create", methods=["POST"])
    def create_policy_acknowledgement():
        if PolicyAcknowledgement is None:
            flash("PolicyAcknowledgement model is not available in models.py.", "danger")
            return redirect(url_for("orientation"))

        raw_payload = {
            "employee_id": request.form.get("employee_id", type=int),
            "policy_name": (request.form.get("policy_name") or "").strip(),
            "acknowledged": request.form.get("acknowledged") == "on",
            "acknowledged_date": parse_date(request.form.get("acknowledged_date")) or date.today(),
            "notes": (request.form.get("notes") or "").strip(),
        }

        payload = filter_payload_by_columns(PolicyAcknowledgement, raw_payload)
        db.session.add(PolicyAcknowledgement(**payload))
        return commit_with_feedback("Policy acknowledgement saved successfully.", "Unable to save policy acknowledgement", "orientation")

    @app.route("/orientation/asset-assignment/create", methods=["POST"])
    def create_asset_assignment():
        if AssetAssignment is None:
            flash("AssetAssignment model is not available in models.py.", "danger")
            return redirect(url_for("orientation"))

        raw_payload = {
            "employee_id": request.form.get("employee_id", type=int),
            "inventory_item_id": request.form.get("inventory_item_id", type=int),
            "asset_name": (request.form.get("asset_name") or "").strip(),
            "assignment_date": parse_date(request.form.get("assignment_date")) or date.today(),
            "return_due_date": parse_date(request.form.get("return_due_date")),
            "status": (request.form.get("status") or "Assigned").strip(),
        }

        payload = filter_payload_by_columns(AssetAssignment, raw_payload)
        db.session.add(AssetAssignment(**payload))
        return commit_with_feedback("Asset assignment created successfully.", "Unable to create asset assignment", "orientation")

    # =====================================================
    # SG-SST ROUTES
    # =====================================================

    @app.route("/sgsst")
    def sgsst():
        return render_or_fallback("sgsst.html", **build_sgsst_context())

    @app.route("/sgsst/risk/create", methods=["POST"])
    def create_risk_item():
        if RiskMatrixItem is None:
            flash("RiskMatrixItem model is not available in models.py.", "danger")
            return redirect(url_for("sgsst"))

        raw_payload = {
            "area": (request.form.get("area") or "").strip(),
            "hazard": (request.form.get("hazard") or "").strip(),
            "risk_level": (request.form.get("risk_level") or "Medium").strip(),
            "control_measure": (request.form.get("control_measure") or "").strip(),
            "responsible_party": (request.form.get("responsible_party") or "").strip(),
        }

        payload = filter_payload_by_columns(RiskMatrixItem, raw_payload)
        db.session.add(RiskMatrixItem(**payload))
        return commit_with_feedback("Risk matrix item created successfully.", "Unable to create risk matrix item", "sgsst")

    @app.route("/sgsst/inspection/create", methods=["POST"])
    def create_inspection_record():
        if InspectionRecord is None:
            flash("InspectionRecord model is not available in models.py.", "danger")
            return redirect(url_for("sgsst"))

        raw_payload = {
            "inspection_name": (request.form.get("inspection_name") or "").strip(),
            "area": (request.form.get("area") or "").strip(),
            "inspector": (request.form.get("inspector") or "").strip(),
            "inspection_date": parse_date(request.form.get("inspection_date")) or date.today(),
            "findings": (request.form.get("findings") or "").strip(),
            "status": (request.form.get("status") or "Open").strip(),
        }

        payload = filter_payload_by_columns(InspectionRecord, raw_payload)
        db.session.add(InspectionRecord(**payload))
        return commit_with_feedback("Inspection record created successfully.", "Unable to create inspection record", "sgsst")

    @app.route("/sgsst/incident/create", methods=["POST"])
    def create_incident_record():
        if IncidentRecord is None:
            flash("IncidentRecord model is not available in models.py.", "danger")
            return redirect(url_for("sgsst"))

        raw_payload = {
            "employee_id": request.form.get("employee_id", type=int),
            "incident_type": (request.form.get("incident_type") or "").strip(),
            "description": (request.form.get("description") or "").strip(),
            "incident_date": parse_date(request.form.get("incident_date")) or date.today(),
            "status": (request.form.get("status") or "Open").strip(),
            "corrective_action": (request.form.get("corrective_action") or "").strip(),
        }

        payload = filter_payload_by_columns(IncidentRecord, raw_payload)
        db.session.add(IncidentRecord(**payload))
        return commit_with_feedback("Incident record created successfully.", "Unable to create incident record", "sgsst")

    @app.route("/sgsst/training/create", methods=["POST"])
    def create_training_record():
        if TrainingRecord is None:
            flash("TrainingRecord model is not available in models.py.", "danger")
            return redirect(url_for("sgsst"))

        raw_payload = {
            "employee_id": request.form.get("employee_id", type=int),
            "training_name": (request.form.get("training_name") or "").strip(),
            "training_date": parse_date(request.form.get("training_date")) or date.today(),
            "trainer": (request.form.get("trainer") or "").strip(),
            "status": (request.form.get("status") or "Completed").strip(),
            "certificate": (request.form.get("certificate") or "").strip(),
        }

        payload = filter_payload_by_columns(TrainingRecord, raw_payload)
        db.session.add(TrainingRecord(**payload))
        return commit_with_feedback("Training record created successfully.", "Unable to create training record", "sgsst")

    # =====================================================
    # INVENTORY ROUTES
    # =====================================================

    @app.route("/inventory")
    def inventory():
        return render_or_fallback("inventory.html", **build_inventory_context())

    @app.route("/inventory/item/create", methods=["POST"])
    def create_inventory_item():
        if InventoryItem is None:
            flash("InventoryItem model is not available in models.py.", "danger")
            return redirect(url_for("inventory"))

        raw_payload = {
            "name": (request.form.get("name") or "").strip(),
            "sku": (request.form.get("sku") or "").strip(),
            "barcode": (request.form.get("barcode") or "").strip(),
            "category": (request.form.get("category") or "").strip(),
            "quantity": as_float(request.form.get("quantity"), 0.0),
            "unit_cost": as_float(request.form.get("unit_cost"), 0.0),
            "reorder_level": as_float(request.form.get("reorder_level"), 0.0),
            "location": (request.form.get("location") or "").strip(),
            "status": (request.form.get("status") or "Available").strip(),
        }

        payload = filter_payload_by_columns(InventoryItem, raw_payload)
        db.session.add(InventoryItem(**payload))
        return commit_with_feedback("Inventory item created successfully.", "Unable to create inventory item", "inventory")

    # =====================================================
    # FINANCE ROUTES
    # =====================================================

    @app.route("/finance")
    def finance():
        return render_or_fallback("finance.html", **build_finance_context())

    @app.route("/finance/invoice/create", methods=["POST"])
    def create_invoice():
        if Invoice is None:
            flash("Invoice model is not available in models.py.", "danger")
            return redirect(url_for("finance"))

        raw_payload = {
            "invoice_number": (request.form.get("invoice_number") or "").strip(),
            "client_name": (request.form.get("client_name") or "").strip(),
            "project_name": (request.form.get("project_name") or "").strip(),
            "amount": as_float(request.form.get("amount") or request.form.get("invoice_amount"), 0.0),
            "due_date": parse_date(request.form.get("due_date")),
            "status": (request.form.get("status") or "Pending").strip(),
            "notes": (request.form.get("notes") or "").strip(),
        }

        if not raw_payload["invoice_number"]:
            raw_payload["invoice_number"] = f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        payload = filter_payload_by_columns(Invoice, raw_payload)
        db.session.add(Invoice(**payload))

        if Finance is not None:
            try:
                ledger_payload = {
                    "entry_type": "Invoice",
                    "description": f"Invoice {raw_payload['invoice_number']}",
                    "amount": raw_payload["amount"],
                    "entry_date": date.today(),
                    "status": "Posted",
                }
                ledger_payload = filter_payload_by_columns(Finance, ledger_payload)
                if ledger_payload:
                    db.session.add(Finance(**ledger_payload))
            except Exception:
                pass

        return commit_with_feedback("Invoice created successfully.", "Unable to create invoice", "finance")

    @app.route("/finance/ledger/create", methods=["POST"])
    def create_ledger_entry():
        if Finance is None:
            flash("Finance model is not available in models.py.", "danger")
            return redirect(url_for("finance"))

        raw_payload = {
            "entry_type": (request.form.get("entry_type") or "General").strip(),
            "category": (request.form.get("category") or "").strip(),
            "description": (request.form.get("description") or "").strip(),
            "amount": as_float(request.form.get("amount"), 0.0),
            "entry_date": parse_date(request.form.get("entry_date")) or date.today(),
            "status": (request.form.get("status") or "Posted").strip(),
        }

        payload = filter_payload_by_columns(Finance, raw_payload)
        db.session.add(Finance(**payload))
        return commit_with_feedback("Ledger entry created successfully.", "Unable to create ledger entry", "finance")

    # =====================================================
    # MARKETING ROUTES
    # =====================================================

    @app.route("/marketing")
    def marketing():
        return render_or_fallback("marketing.html", **build_marketing_context())

    @app.route("/marketing/campaign/create", methods=["POST"])
    def create_marketing_campaign():
        if MarketingCampaign is None:
            flash("MarketingCampaign model is not available in models.py.", "danger")
            return redirect(url_for("marketing"))

        raw_payload = {
            "name": (request.form.get("name") or "").strip(),
            "channel": (request.form.get("channel") or "").strip(),
            "audience": (request.form.get("audience") or "").strip(),
            "budget": as_float(request.form.get("budget"), 0.0),
            "status": (request.form.get("status") or "Draft").strip(),
            "start_date": parse_date(request.form.get("start_date")),
            "end_date": parse_date(request.form.get("end_date")),
            "notes": (request.form.get("notes") or "").strip(),
        }

        payload = filter_payload_by_columns(MarketingCampaign, raw_payload)
        db.session.add(MarketingCampaign(**payload))
        return commit_with_feedback("Marketing campaign created successfully.", "Unable to create marketing campaign", "marketing")

    # =====================================================
    # CALENDAR ROUTES
    # =====================================================

    @app.route("/calendar")
    def calendar_page():
        return render_or_fallback("calendar.html", **build_calendar_context())

    @app.route("/calendar/event/create", methods=["POST"])
    def create_calendar_event():
        if CalendarEvent is None:
            flash("CalendarEvent model is not available in models.py.", "danger")
            return redirect(url_for("calendar_page"))

        raw_payload = {
            "title": (request.form.get("title") or "").strip(),
            "description": (request.form.get("description") or "").strip(),
            "location": (request.form.get("location") or "").strip(),
            "start_time": parse_datetime(request.form.get("start_time")),
            "end_time": parse_datetime(request.form.get("end_time")),
            "status": (request.form.get("status") or "Scheduled").strip(),
        }

        payload = filter_payload_by_columns(CalendarEvent, raw_payload)
        db.session.add(CalendarEvent(**payload))
        return commit_with_feedback("Calendar event created successfully.", "Unable to create calendar event", "calendar_page")

    # =====================================================
    # REPORTS / ANALYTICS
    # =====================================================

    @app.route("/reports-analytics")
    def reports_analytics():
        return render_or_fallback("reports_analytics.html", **build_reports_context())

    @app.route("/api/dashboard-stats")
    def api_dashboard_stats():
        return jsonify(build_dashboard_stats())

    # =====================================================
    # XIOMY ROUTES
    # =====================================================

    @app.route("/xiomy-page")
    def xiomy_page():
        return render_or_fallback(
            "xiomy.html",
            xiomy_status=safe_xiomy_status(xiomy_ai),
            xiomy_greeting=safe_xiomy_greeting(xiomy_ai),
            xiomy_insight=safe_xiomy_insight(xiomy_ai),
            dashboard_stats=build_dashboard_stats(),
        )

    @app.route("/xiomy")
    def xiomy():
        return jsonify({
            "assistant": "XIOMY",
            "status": "online",
            "system": safe_xiomy_status(xiomy_ai),
            "greeting": safe_xiomy_greeting(xiomy_ai),
            "insight": safe_xiomy_insight(xiomy_ai),
            "dashboard": build_dashboard_stats(),
            "timestamp": datetime.utcnow().isoformat(),
        })

    # =====================================================
    # FILE UPLOADS
    # =====================================================

    @app.route("/files/upload", methods=["POST"])
    def upload_file():
        uploaded = request.files.get("file")
        if not uploaded or not uploaded.filename:
            flash("No file selected.", "danger")
            return redirect(request.referrer or url_for("dashboard"))

        if not allowed_file(uploaded.filename):
            flash("File type not allowed.", "danger")
            return redirect(request.referrer or url_for("dashboard"))

        filename = secure_filename(uploaded.filename)
        save_path = UPLOAD_FOLDER / filename
        uploaded.save(save_path)
        flash("File uploaded successfully.", "success")
        return redirect(request.referrer or url_for("dashboard"))

    # =====================================================
    # SEARCH ROUTE
    # =====================================================

    @app.route("/search")
    def search():
        query = (request.args.get("q") or "").strip().lower()
        results = {
            "clients": [],
            "projects": [],
            "candidates": [],
            "employees": [],
            "campaigns": [],
        }

        if not query:
            return render_or_fallback("search_results.html", query=query, results=results)

        def matches(value: Any) -> bool:
            return query in str(value or "").lower()

        try:
            for client in safe_all(Client):
                if (
                    matches(getattr(client, "name", ""))
                    or matches(getattr(client, "company_name", ""))
                    or matches(getattr(client, "email", ""))
                    or matches(getattr(client, "industry", ""))
                    or matches(getattr(client, "country", ""))
                    or matches(getattr(client, "language", ""))
                    or matches(getattr(client, "tax_id_number", ""))
                ):
                    results["clients"].append(client)
        except Exception:
            pass

        try:
            for project in safe_all(Project):
                if matches(getattr(project, "name", "")) or matches(getattr(project, "project_name", "")):
                    results["projects"].append(project)
        except Exception:
            pass

        try:
            for candidate in safe_all(Candidate):
                if matches(getattr(candidate, "full_name", "")) or matches(getattr(candidate, "email", "")):
                    results["candidates"].append(candidate)
        except Exception:
            pass

        try:
            for employee in safe_all(EmployeeProfile):
                if matches(getattr(employee, "full_name", "")) or matches(getattr(employee, "email", "")):
                    results["employees"].append(employee)
        except Exception:
            pass

        try:
            for campaign in safe_all(MarketingCampaign):
                if matches(getattr(campaign, "name", "")) or matches(getattr(campaign, "channel", "")):
                    results["campaigns"].append(campaign)
        except Exception:
            pass

        return render_or_fallback("search_results.html", query=query, results=results)

    # =====================================================
    # ERROR HANDLERS
    # =====================================================

    @app.errorhandler(404)
    def not_found(error):
        return render_or_fallback("404.html", error=error), 404

    @app.errorhandler(500)
    def server_error(error):
        try:
            db.session.rollback()
        except Exception:
            pass
        return render_or_fallback("500.html", error=error), 500

    return app


# =========================================================
# APP INSTANCE
# =========================================================

app = create_app()

# =========================================================
# LOCAL RUN
# =========================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
