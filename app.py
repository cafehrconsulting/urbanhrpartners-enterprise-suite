# =========================================================
# UrbanHRPartners Enterprise Suite
# app.py
<<<<<<< HEAD
# FILE TYPE: PY
# PURPOSE:
# Full Flask application controller aligned to models.py.
# Render-ready, Gunicorn-ready, database-safe, HTML-ready,
# JSON-ready, and designed to reduce crash risk.
=======
# FULL ENTERPRISE-SAFE APPLICATION CONTROLLER
# Render-ready / HTML deploy-ready / no shrinking
# Fully synchronized with enterprise base.html + dashboard.html
>>>>>>> 6a700036149ddd83079e5ef7c8be09236a086406
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
)
from jinja2 import TemplateNotFound
from sqlalchemy import inspect, func
from werkzeug.security import check_password_hash, generate_password_hash

from models import (
    db,
    User,
    Department,
    Position,
    EmployeeProfile,
    TimeEntry,
    LeaveRequest,
    PayrollRecord,
    PerformanceReview,
    PointLog,
    SOPRequirement,
    DisciplinaryRecord,
    LaborActionRecord,
    Client,
    ClientContact,
    CommunicationLog,
    Task,
    Project,
    Proposal,
    ChartOfAccount,
    JournalEntry,
    JournalEntryLine,
    Invoice,
    InvoiceLineItem,
    Payment,
    ExpenseCategory,
    Expense,
    Budget,
    Vendor,
    InventoryCategory,
    InventoryItem,
    InventoryMovement,
    AssetAssignment,
    JobPosting,
    Candidate,
    CandidateApplication,
    Interview,
    ResumeProfile,
    OrientationSession,
    OrientationChecklist,
    PolicyAcknowledgement,
    SafetyPolicy,
    LegalRequirement,
    RiskMatrix,
    Inspection,
    Incident,
    IncidentInvestigation,
    SafetyTraining,
    PPEIssue,
    MedicalSurveillance,
    EmergencyDrill,
    Contractor,
    ContractorEvaluation,
    SafetyAudit,
    ImprovementPlan,
    MarketingCampaign,
    MarketingLead,
    LeadActivity,
    CalendarEvent,
    NotificationLog,
    ReportSnapshot,
    KPISetting,
    seed_basic_departments,
    seed_basic_positions,
)

# =========================================================
# BASE PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
<<<<<<< HEAD
DEFAULT_SQLITE_PATH = BASE_DIR / "urbanhrpartners.db"
=======
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
    "json",
}
>>>>>>> 6a700036149ddd83079e5ef7c8be09236a086406

# =========================================================
# HELPERS
# =========================================================

<<<<<<< HEAD
=======
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
        return (
            f"{period}. XIOMY Executive AI is ready to assist "
            f"UrbanHRPartners Enterprise operations."
        )

    def insight(self):
        return (
            "Cross-module intelligence is active. Monitor CRM pipeline, HR performance, "
            "recruiting velocity, SG-SST compliance, finance forecasting, inventory status, "
            "marketing activity, and enterprise growth indicators from one executive environment."
        )


def build_xiomy_instance(db_instance):
    if ImportedXiomyAI is None:
        return SafeXiomyAI(db_instance)

    try:
        return ImportedXiomyAI(db_instance)
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
        db as imported_models_db,
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

    models_db = imported_models_db
    db = imported_models_db

except Exception:
    try:
        from models import db as imported_models_db  # type: ignore

        models_db = imported_models_db
        db = imported_models_db
    except Exception:
        models_db = None

# =========================================================
# CORE UTILITIES
# =========================================================


>>>>>>> 6a700036149ddd83079e5ef7c8be09236a086406
def normalize_database_url(raw_url: str | None) -> str:
    if not raw_url:
        return f"sqlite:///{DEFAULT_SQLITE_PATH}"
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql://", 1)
    return raw_url

<<<<<<< HEAD
def parse_date(value: str | None) -> date | None:
=======

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
        elif hasattr(model, "id"):
            query = query.order_by(model.id.desc())
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
>>>>>>> 6a700036149ddd83079e5ef7c8be09236a086406
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None

def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
<<<<<<< HEAD
    candidates = [
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in candidates:
=======
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
>>>>>>> 6a700036149ddd83079e5ef7c8be09236a086406
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None

def parse_float(value, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(Decimal(str(value).replace(",", "")))
    except (InvalidOperation, ValueError, TypeError):
        return default

def parse_int(value, default: int = 0) -> int:
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def bool_from_form(value) -> bool:
    return str(value).lower() in {"true", "1", "yes", "on", "checked"}

def current_user() -> User | None:
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)

def login_required():
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                flash("Please log in first.", "warning")
                return redirect(url_for("login"))
            return fn(*args, **kwargs)
        return wrapped
    return decorator

<<<<<<< HEAD
def ensure_directory_structure():
    (BASE_DIR / "templates").mkdir(exist_ok=True)
    (BASE_DIR / "static").mkdir(exist_ok=True)
    (BASE_DIR / "static" / "css").mkdir(exist_ok=True)
    (BASE_DIR / "static" / "js").mkdir(exist_ok=True)
    (BASE_DIR / "static" / "img").mkdir(exist_ok=True)
=======
def render_or_fallback(template_name: str, **context):
    if template_exists(template_name):
        try:
            return render_template(template_name, **context)
        except TemplateNotFound:
            pass
        except Exception as exc:
            fallback_template = "template_missing.html"
            if template_exists(fallback_template):
                return render_template(
                    fallback_template,
                    template_name=template_name,
                    error_message=str(exc),
                    **context,
                )
            return f"Template render failure for {template_name}: {exc}", 500

    fallback_template = "template_missing.html"
    if template_exists(fallback_template):
        return render_template(
            fallback_template,
            missing_template=template_name,
            **context,
        )
    return f"Missing template: {template_name}", 500
>>>>>>> 6a700036149ddd83079e5ef7c8be09236a086406

def safe_render(template_name: str, **context):
    try:
        return render_template(template_name, **context)
    except TemplateNotFound:
        page_title = context.get("page_title", template_name)
        message = (
            f"<h1>{page_title}</h1>"
            f"<p>Template <strong>{template_name}</strong> is not present yet.</p>"
            f"<p>The route is active and the backend is working.</p>"
        )
        return (
            "<!doctype html>"
            "<html><head><title>UrbanHRPartners</title></head>"
            f"<body style='font-family:Arial;padding:30px'>{message}</body></html>"
        )

# =========================================================
# DATABASE BOOTSTRAP
# =========================================================

def bootstrap_reference_data():
    with db.session.begin():
        if not Department.query.first():
            seed_basic_departments()
        if not Position.query.first():
            seed_basic_positions()
        if not ExpenseCategory.query.first():
            for name in ["Travel", "Meals", "Software", "Payroll", "Marketing", "Training", "Office Supplies", "Professional Services", "Utilities", "Rent"]:
                db.session.add(ExpenseCategory(name=name, status="Active"))
        if not InventoryCategory.query.first():
            for name in ["Technology", "Office Equipment", "Furniture", "PPE", "Training Materials", "Supplies", "Assets"]:
                db.session.add(InventoryCategory(name=name, status="Active"))
        if not ChartOfAccount.query.first():
            chart = [
                ("1000", "Cash", "Asset"),
                ("1100", "Accounts Receivable", "Asset"),
                ("1200", "Inventory", "Asset"),
                ("1500", "Fixed Assets", "Asset"),
                ("2000", "Accounts Payable", "Liability"),
                ("2100", "Taxes Payable", "Liability"),
                ("3000", "Owner Equity", "Equity"),
                ("4000", "Consulting Revenue", "Revenue"),
                ("4100", "Software Revenue", "Revenue"),
                ("5000", "Payroll Expense", "Expense"),
                ("5100", "Marketing Expense", "Expense"),
                ("5200", "Office Expense", "Expense"),
                ("5300", "Travel Expense", "Expense"),
            ]
            for code, name, acc_type in chart:
                db.session.add(ChartOfAccount(account_code=code, account_name=name, account_type=acc_type, status="Active"))

def bootstrap_admin():
    admin_email = os.getenv("ADMIN_EMAIL", "admin@urbanhrconsulting.cloud").strip().lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "Admin123!").strip()
    admin_name = os.getenv("ADMIN_NAME", "UrbanHRPartners Administrator").strip()

    existing = User.query.filter(func.lower(User.email) == admin_email).first()
    if existing:
        return existing

<<<<<<< HEAD
    admin = User(
        full_name=admin_name,
        email=admin_email,
        password_hash=generate_password_hash(admin_password),
        role="Admin",
        language="English",
        timezone="America/New_York",
        status="Active",
        is_active=True,
=======
def safe_xiomy_insight(xiomy_ai):
    try:
        if hasattr(xiomy_ai, "insight") and callable(getattr(xiomy_ai, "insight")):
            return xiomy_ai.insight()
    except Exception:
        pass

    return (
        "Executive enterprise monitoring is active. Review CRM performance, workforce data, "
        "recruiting progress, SG-SST compliance, financial health, inventory condition, "
        "marketing growth, and strategic indicators from the dashboard."
>>>>>>> 6a700036149ddd83079e5ef7c8be09236a086406
    )
    db.session.add(admin)
    db.session.commit()
    return admin

<<<<<<< HEAD
def ensure_sqlite_tables(app: Flask):
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        if not existing_tables:
            db.create_all()
        bootstrap_reference_data()
        bootstrap_admin()
=======

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
# GENERIC SERIALIZATION HELPERS
# =========================================================

def get_attr(obj: Any, *names: str, default: Any = None) -> Any:
    for name in names:
        try:
            if hasattr(obj, name):
                value = getattr(obj, name)
                if value is not None:
                    return value
        except Exception:
            continue
    return default


def money(value: Any) -> float:
    return round(as_float(value, 0.0), 2)


def isoish(value: Any) -> str:
    try:
        if isinstance(value, (datetime, date)):
            return value.isoformat()
    except Exception:
        pass
    return str(value or "")


# =========================================================
# DASHBOARD BUILDERS
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
    total_events = safe_count(CalendarEvent)

    open_tasks = 0
    total_revenue = 0.0
    outstanding_total = 0.0
    low_stock_items = 0
    payroll_cycle = "Pending"
    risk_score = "N/A"

    try:
        if Task is not None:
            tasks = Task.query.all()
            open_tasks = len(
                [
                    t for t in tasks
                    if str(getattr(t, "status", "")).lower() not in {"completed", "closed", "done"}
                ]
            )
    except Exception:
        open_tasks = 0

    try:
        if Invoice is not None:
            invoices = Invoice.query.all()
            total_revenue = sum(as_float(getattr(i, "amount", 0.0), 0.0) for i in invoices)
            outstanding_total = sum(
                as_float(getattr(i, "amount", 0.0), 0.0)
                for i in invoices
                if str(getattr(i, "status", "")).lower() not in {"paid", "closed", "collected"}
            )
    except Exception:
        total_revenue = 0.0
        outstanding_total = 0.0

    try:
        if InventoryItem is not None:
            items = InventoryItem.query.all()
            low_stock_items = len(
                [
                    item for item in items
                    if as_float(getattr(item, "quantity", 0), 0)
                    <= as_float(getattr(item, "reorder_level", 0), 0)
                ]
            )
    except Exception:
        low_stock_items = 0

    try:
        if total_incidents == 0:
            risk_score = "Low"
        elif total_incidents < 5:
            risk_score = "Moderate"
        else:
            risk_score = "High"
    except Exception:
        risk_score = "N/A"

    return {
        "total_clients": total_clients,
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "open_tasks": open_tasks,
        "inventory_items": inventory_items,
        "low_stock_items": low_stock_items,
        "total_invoices": total_invoices,
        "total_revenue": round(total_revenue, 2),
        "outstanding_total": round(outstanding_total, 2),
        "total_candidates": total_candidates,
        "total_employees": total_employees,
        "total_campaigns": total_campaigns,
        "total_incidents": total_incidents,
        "total_events": total_events,
        "payroll_cycle": payroll_cycle,
        "risk_score": risk_score,
    }


def build_dashboard_metrics(dashboard_stats: dict) -> dict:
    return {
        "revenue": dashboard_stats.get("total_revenue", 0),
        "active_clients": dashboard_stats.get("total_clients", 0),
        "employees": dashboard_stats.get("total_employees", 0),
        "jobs": dashboard_stats.get("total_candidates", 0),
        "incidents": dashboard_stats.get("total_incidents", 0),
        "inventory_alerts": dashboard_stats.get("low_stock_items", 0),
        "consultant_load": dashboard_stats.get("total_clients", 0),
        "open_tasks": dashboard_stats.get("open_tasks", 0),
        "meetings": dashboard_stats.get("total_events", 0),
        "payroll_cycle": dashboard_stats.get("payroll_cycle", "Pending"),
        "receivables": dashboard_stats.get("outstanding_total", 0),
        "risk_score": dashboard_stats.get("risk_score", "N/A"),
    }


def build_dashboard_ai_insights(dashboard_stats: dict, xiomy_ai) -> list[dict]:
    insights = [
        {
            "title": "XIOMY Status",
            "message": safe_xiomy_greeting(xiomy_ai),
        },
        {
            "title": "Executive Insight",
            "message": safe_xiomy_insight(xiomy_ai),
        },
    ]

    revenue = dashboard_stats.get("total_revenue", 0)
    open_tasks = dashboard_stats.get("open_tasks", 0)
    incidents = dashboard_stats.get("total_incidents", 0)
    candidates = dashboard_stats.get("total_candidates", 0)

    insights.append(
        {
            "title": "Revenue Overview",
            "message": (
                f"Current posted invoice value is ${revenue}. "
                f"Use Finance and CRM together to monitor collection timing and margins."
            ),
        }
    )

    insights.append(
        {
            "title": "Execution Load",
            "message": (
                f"There are {open_tasks} open tasks and {candidates} candidates in the ATS flow. "
                f"Review consultant capacity, hiring demand, and onboarding readiness."
            ),
        }
    )

    insights.append(
        {
            "title": "Compliance Watch",
            "message": (
                f"SG-SST currently reflects {incidents} incident records. "
                f"Track inspections, corrective actions, and training cadence to reduce risk."
            ),
        }
    )

    return insights


def build_dashboard_alerts(dashboard_stats: dict) -> list[dict]:
    alerts = []

    if dashboard_stats.get("outstanding_total", 0) > 0:
        alerts.append(
            {
                "title": "Outstanding Invoices",
                "priority": "Finance",
                "message": (
                    f"${dashboard_stats.get('outstanding_total', 0)} remains outstanding. "
                    "Review Finance for receivables follow-up."
                ),
            }
        )

    if dashboard_stats.get("low_stock_items", 0) > 0:
        alerts.append(
            {
                "title": "Inventory Reorder Needed",
                "priority": "Inventory",
                "message": (
                    f"{dashboard_stats.get('low_stock_items', 0)} inventory items are at or below reorder level."
                ),
            }
        )

    if dashboard_stats.get("total_incidents", 0) > 0:
        alerts.append(
            {
                "title": "Safety / Incident Review",
                "priority": "SG-SST",
                "message": (
                    f"{dashboard_stats.get('total_incidents', 0)} incident records require visibility "
                    "across safety and workforce leadership."
                ),
            }
        )

    if dashboard_stats.get("open_tasks", 0) > 0:
        alerts.append(
            {
                "title": "Open Task Queue",
                "priority": "Operations",
                "message": (
                    f"{dashboard_stats.get('open_tasks', 0)} open tasks remain active across modules."
                ),
            }
        )

    if not alerts:
        alerts.append(
            {
                "title": "No Critical Alerts",
                "priority": "System",
                "message": "No immediate alert conditions were detected in the current enterprise snapshot.",
            }
        )

    return alerts


def build_dashboard_recent_activity(limit: int = 7) -> list[dict]:
    activity = []

    try:
        for log in safe_all(CommunicationLog, limit=3, order_attr="id"):
            activity.append(
                {
                    "title": get_attr(log, "subject", "channel", default="CRM communication logged"),
                    "message": get_attr(log, "summary", "message", default="New client communication was recorded."),
                    "time": isoish(get_attr(log, "log_date", "created_at", default="Recently")),
                }
            )
    except Exception:
        pass

    try:
        for invoice in safe_all(Invoice, limit=2, order_attr="id"):
            activity.append(
                {
                    "title": f"Invoice {get_attr(invoice, 'invoice_number', default='created')}",
                    "message": (
                        f"Amount ${money(get_attr(invoice, 'amount', default=0))} "
                        f"with status {get_attr(invoice, 'status', default='Pending')}."
                    ),
                    "time": isoish(get_attr(invoice, "created_at", "due_date", default="Recently")),
                }
            )
    except Exception:
        pass

    try:
        for incident in safe_all(IncidentRecord, limit=2, order_attr="id"):
            activity.append(
                {
                    "title": get_attr(incident, "incident_type", default="Incident record updated"),
                    "message": get_attr(
                        incident,
                        "description",
                        "corrective_action",
                        default="Safety activity requires review.",
                    ),
                    "time": isoish(get_attr(incident, "incident_date", "created_at", default="Recently")),
                }
            )
    except Exception:
        pass

    if not activity:
        activity = [
            {
                "title": "System initialized",
                "message": "Dashboard is ready to receive live CRM, HRIS, ATS, SG-SST, Finance, and Inventory activity.",
                "time": "Now",
            }
        ]

    return activity[:limit]


def build_client_pipeline() -> list[dict]:
    rows = []
    projects = safe_all(Project, order_attr="id")

    if not projects:
        return []

    stage_map: dict[str, dict[str, float | int | str]] = {}

    for project in projects:
        stage = str(
            get_attr(project, "status", default="Pipeline")
        ).strip() or "Pipeline"
        amount = as_float(
            get_attr(project, "budget", "estimated_value", default=0.0),
            0.0,
        )
        key = stage
        if key not in stage_map:
            stage_map[key] = {"stage": stage, "count": 0, "value": 0.0, "status": "Tracking"}
        stage_map[key]["count"] = int(stage_map[key]["count"]) + 1
        stage_map[key]["value"] = float(stage_map[key]["value"]) + amount

    for _, row in stage_map.items():
        rows.append(
            {
                "stage": row["stage"],
                "count": int(row["count"]),
                "value": round(float(row["value"]), 2),
                "status": row["status"],
            }
        )

    return rows[:8]


def build_ats_pipeline() -> list[dict]:
    rows = []
    candidates = safe_all(Candidate, order_attr="id")

    if not candidates:
        return []

    stage_map: dict[str, dict[str, Any]] = {}

    for candidate in candidates:
        stage = str(get_attr(candidate, "stage", default="Applied")).strip() or "Applied"
        priority = "Normal"
        if stage.lower() in {"offer", "offered", "interview", "orientation"}:
            priority = "High"
        readiness = "In Progress"
        if stage.lower() in {"orientation", "hired", "onboarding"}:
            readiness = "Ready"

        if stage not in stage_map:
            stage_map[stage] = {
                "stage": stage,
                "count": 0,
                "priority": priority,
                "readiness": readiness,
            }

        stage_map[stage]["count"] += 1

    for _, row in stage_map.items():
        rows.append(row)

    return rows[:8]


def build_finance_rows(limit: int = 8) -> list[dict]:
    rows = []

    try:
        for entry in safe_all(Finance, limit=limit, order_attr="id"):
            rows.append(
                {
                    "date": isoish(get_attr(entry, "entry_date", "created_at", default="-")),
                    "description": get_attr(entry, "description", default="Ledger entry"),
                    "category": get_attr(entry, "category", default="General"),
                    "amount": money(get_attr(entry, "amount", default=0)),
                    "entry_type": get_attr(entry, "entry_type", default="Transaction"),
                }
            )
    except Exception:
        pass

    if not rows:
        try:
            for invoice in safe_all(Invoice, limit=limit, order_attr="id"):
                rows.append(
                    {
                        "date": isoish(get_attr(invoice, "created_at", "due_date", default="-")),
                        "description": f"Invoice {get_attr(invoice, 'invoice_number', default='')}".strip(),
                        "category": "Revenue",
                        "amount": money(get_attr(invoice, "amount", default=0)),
                        "entry_type": get_attr(invoice, "status", default="Invoice"),
                    }
                )
        except Exception:
            pass

    return rows[:limit]


def build_inventory_rows(limit: int = 6) -> list[dict]:
    rows = []

    for item in safe_all(InventoryItem, limit=limit, order_attr="id"):
        rows.append(
            {
                "name": get_attr(item, "name", default="Inventory Item"),
                "quantity": as_float(get_attr(item, "quantity", default=0), 0),
                "summary": (
                    f"SKU: {get_attr(item, 'sku', default='N/A')} | "
                    f"Location: {get_attr(item, 'location', default='Unassigned')} | "
                    f"Status: {get_attr(item, 'status', default='Available')}"
                ),
            }
        )

    return rows


def build_hris_rows(limit: int = 6) -> list[dict]:
    rows = []

    for employee in safe_all(EmployeeProfile, limit=limit, order_attr="id"):
        full_name = get_attr(
            employee,
            "full_name",
            default=f"{get_attr(employee, 'first_name', default='')} {get_attr(employee, 'last_name', default='')}".strip(),
        )
        rows.append(
            {
                "name": full_name or "Employee Record",
                "status": get_attr(employee, "status", default="Active"),
                "summary": (
                    f"Position: {get_attr(employee, 'position', default='Not set')} | "
                    f"Department: {get_attr(employee, 'department', default='Not set')} | "
                    f"Email: {get_attr(employee, 'email', default='N/A')}"
                ),
            }
        )

    return rows


def build_sgsst_rows(limit: int = 6) -> list[dict]:
    rows = []

    for incident in safe_all(IncidentRecord, limit=limit, order_attr="id"):
        rows.append(
            {
                "title": get_attr(incident, "incident_type", default="Incident"),
                "status": get_attr(incident, "status", default="Open"),
                "summary": get_attr(
                    incident,
                    "description",
                    "corrective_action",
                    default="Incident monitoring record available.",
                ),
            }
        )

    if not rows:
        for inspection in safe_all(InspectionRecord, limit=limit, order_attr="id"):
            rows.append(
                {
                    "title": get_attr(inspection, "inspection_name", default="Inspection"),
                    "status": get_attr(inspection, "status", default="Open"),
                    "summary": get_attr(
                        inspection,
                        "findings",
                        default="Inspection record available for follow-up.",
                    ),
                }
            )

    return rows


def build_dashboard_tasks(limit: int = 6) -> list[dict]:
    rows = []

    for task in safe_all(Task, limit=limit, order_attr="id"):
        rows.append(
            {
                "title": get_attr(task, "title", default="Task"),
                "priority": get_attr(task, "priority", default="Normal"),
                "description": get_attr(task, "description", "notes", default="Operational task item."),
            }
        )

    return rows


def build_dashboard_payload(xiomy_ai):
    dashboard_stats = build_dashboard_stats()
    payload = {
        "dashboard_stats": dashboard_stats,
        "metrics": build_dashboard_metrics(dashboard_stats),
        "dashboard": dashboard_stats,
        "ai_insights": build_dashboard_ai_insights(dashboard_stats, xiomy_ai),
        "alerts": build_dashboard_alerts(dashboard_stats),
        "recent_activity": build_dashboard_recent_activity(),
        "client_pipeline": build_client_pipeline(),
        "ats_pipeline": build_ats_pipeline(),
        "tasks": build_dashboard_tasks(),
        "finance_rows": build_finance_rows(),
        "inventory_rows": build_inventory_rows(),
        "hris_rows": build_hris_rows(),
        "sgsst_rows": build_sgsst_rows(),
        "xiomy_greeting": safe_xiomy_greeting(xiomy_ai),
        "xiomy_insight": safe_xiomy_insight(xiomy_ai),
        "xiomy_status": safe_xiomy_status(xiomy_ai),
        "recent_clients": safe_all(Client, limit=5, order_attr="id"),
        "recent_projects": safe_all(Project, limit=5, order_attr="id"),
        "recent_candidates": safe_all(Candidate, limit=5, order_attr="id"),
        "recent_invoices": safe_all(Invoice, limit=5, order_attr="id"),
        "recent_incidents": safe_all(IncidentRecord, limit=5, order_attr="id"),
    }
    return payload


# =========================================================
# MODULE CONTEXT BUILDERS
# =========================================================

def build_crm_context():
    clients = safe_all(Client, order_attr="id")
    communication_logs = safe_all(CommunicationLog, limit=50, order_attr="id")
    projects = safe_all(Project, limit=50, order_attr="id")
    tasks = safe_all(Task, limit=50, order_attr="id")

    pipeline_value = 0.0
    try:
        for project in projects:
            pipeline_value += as_float(
                getattr(project, "budget", getattr(project, "estimated_value", 0.0)),
                0.0,
            )
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
    }


def build_hris_context():
    employees = safe_all(EmployeeProfile, order_attr="id")
    point_logs = safe_all(PointLog, limit=50, order_attr="id")
    sop_requirements = safe_all(SOPRequirement, limit=50, order_attr="id")
    disciplinary_records = safe_all(DisciplinaryRecord, limit=50, order_attr="id")

    active_employees = 0
    try:
        active_employees = len(
            [
                e for e in employees
                if str(getattr(e, "status", "Active")).lower() in {"active", "current", "working"}
            ]
        )
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
        "interview_stage": len(
            [c for c in candidates if str(getattr(c, "stage", "")).lower() in {"interview", "interviewing"}]
        ),
        "offers": len(
            [c for c in candidates if str(getattr(c, "stage", "")).lower() in {"offer", "offered"}]
        ),
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
        "active_campaigns": len(
            [c for c in campaigns if str(getattr(c, "status", "")).lower() in {"active", "running", "live"}]
        ),
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


def build_tasks_context():
    tasks = safe_all(Task, limit=200, order_attr="id")
    task_stats = {
        "total_tasks": len(tasks),
        "open_tasks": len(
            [
                t for t in tasks
                if str(getattr(t, "status", "")).lower() not in {"completed", "closed", "done"}
            ]
        ),
    }
    return {
        "tasks": tasks,
        "task_stats": task_stats,
    }


def build_reports_context():
    dashboard_stats = build_dashboard_stats()
    return {
        "dashboard_stats": dashboard_stats,
        "generated_at": datetime.utcnow(),
    }

>>>>>>> 6a700036149ddd83079e5ef7c8be09236a086406

# =========================================================
# APP FACTORY
# =========================================================

def create_app():
<<<<<<< HEAD
    ensure_directory_structure()
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "urbanhrpartners-secret-key-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = normalize_database_url(os.getenv("DATABASE_URL"))
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JSON_SORT_KEYS"] = False

    db.init_app(app)

    with app.app_context():
        ensure_sqlite_tables(app)

    @app.context_processor
    def inject_global_context():
        user = current_user()
        unread_notifications = 0
        if user:
            unread_notifications = NotificationLog.query.filter_by(user_id=user.id, is_read=False).count()
        return {"current_user": user, "today_date": date.today(), "now_datetime": datetime.now(), "unread_notifications": unread_notifications, "system_name": "UrbanHRPartners Enterprise Suite"}

    # All routes as previously defined...
    # (dashboard, crm, hris, ats, orientation, sgsst, inventory, finance, marketing, reports, calendar, notifications, API endpoints)

    # ERROR HANDLERS
    @app.errorhandler(404)
=======
    flask_app = Flask(
        __name__,
        template_folder=str(TEMPLATES_FOLDER),
        static_folder=str(STATIC_FOLDER),
    )

    flask_app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "urbanhrpartners-enterprise-secret")
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = normalize_database_url(os.getenv("DATABASE_URL"))
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    flask_app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
    flask_app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

    db.init_app(flask_app)

    xiomy_ai = build_xiomy_instance(db)

    @flask_app.context_processor
    def inject_globals():
        return {
            "current_year": datetime.utcnow().year,
            "today": date.today(),
            "dashboard_quick_stats": build_dashboard_stats(),
            "app_name": "UrbanHRPartners Enterprise Suite",
            "company_name": "UrbanHRPartners",
            "system_name": "UrbanHRPartners Enterprise Suite",
        }

    @flask_app.before_request
    def ensure_directories():
        UPLOAD_FOLDER.mkdir(exist_ok=True)
        CLIENT_PROGRAMS_FOLDER.mkdir(exist_ok=True)

    # =====================================================
    # STARTUP DATABASE SAFETY
    # =====================================================

    with flask_app.app_context():
        try:
            db.create_all()
        except Exception:
            pass

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

    @flask_app.route("/")
    def index():
        return redirect(url_for("dashboard"))

    @flask_app.route("/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "application": "UrbanHRPartners Enterprise Suite",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    @flask_app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(flask_app.config["UPLOAD_FOLDER"], filename)

    # =====================================================
    # DASHBOARD
    # =====================================================

    @flask_app.route("/dashboard")
    def dashboard():
        return render_or_fallback(
            "dashboard.html",
            **build_dashboard_payload(xiomy_ai),
        )

    # =====================================================
    # CRM ROUTES
    # =====================================================

    @flask_app.route("/crm", endpoint="crm_dashboard")
    def crm_dashboard():
        return render_or_fallback("crm.html", **build_crm_context())

    @flask_app.route("/crm/client/create", methods=["POST"])
    def create_client():
        if Client is None:
            flash("Client model is not available in models.py.", "danger")
            return redirect(url_for("crm_dashboard"))

        raw_payload = {
            "name": (request.form.get("name") or "").strip(),
            "company_name": (request.form.get("company_name") or "").strip(),
            "contact_person": (request.form.get("contact_person") or "").strip(),
            "email": (request.form.get("email") or "").strip(),
            "phone": (request.form.get("phone") or "").strip(),
            "industry": (request.form.get("industry") or "").strip(),
            "status": (request.form.get("status") or "Prospect").strip(),
            "address": (request.form.get("address") or "").strip(),
            "country": (request.form.get("country") or "").strip(),
            "language": (request.form.get("language") or "").strip(),
            "region": (request.form.get("region") or "").strip(),
            "tax_id_type": (request.form.get("tax_id_type") or "").strip(),
            "tax_id_number": (request.form.get("tax_id_number") or "").strip(),
            "risk_level": (request.form.get("risk_level") or "").strip(),
            "needs": (request.form.get("needs") or "").strip(),
            "notes": (request.form.get("notes") or "").strip(),
        }

        if not raw_payload["name"] and not raw_payload["company_name"]:
            flash("Client name or company name is required.", "danger")
            return redirect(url_for("crm_dashboard"))

        payload = filter_payload_by_columns(Client, raw_payload)
        client_columns = model_columns(Client)

        if "name" in client_columns and not payload.get("name"):
            payload["name"] = raw_payload["company_name"] or "Unnamed Client"

        if "country" in client_columns and not payload.get("country"):
            payload["country"] = "Colombia"

        if "language" in client_columns and not payload.get("language"):
            payload["language"] = "Spanish"

        db.session.add(Client(**payload))
        return commit_with_feedback(
            "Client created successfully.",
            "Unable to create client",
            "crm_dashboard",
        )

    @flask_app.route("/crm/communication-log/create", methods=["POST"])
    def create_communication_log():
        if CommunicationLog is None:
            flash("CommunicationLog model is not available in models.py.", "danger")
            return redirect(url_for("crm_dashboard"))

        client_id = request.form.get("client_id", type=int)
        if not client_id:
            flash("Client is required before saving a communication log.", "danger")
            return redirect(url_for("crm_dashboard"))

        if Client is not None:
            client = Client.query.get(client_id)
            if not client:
                flash("Selected client was not found.", "danger")
                return redirect(url_for("crm_dashboard"))

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
        return commit_with_feedback(
            "Communication log created successfully.",
            "Unable to save communication log",
            "crm_dashboard",
        )

    @flask_app.route("/crm/project/create", methods=["POST"])
    def create_project():
        if Project is None:
            flash("Project model is not available in models.py.", "danger")
            return redirect(url_for("crm_dashboard"))

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
        return commit_with_feedback(
            "Project created successfully.",
            "Unable to create project",
            "crm_dashboard",
        )

    @flask_app.route("/crm/task/create", methods=["POST"])
    def create_task():
        if Task is None:
            flash("Task model is not available in models.py.", "danger")
            return redirect(url_for("crm_dashboard"))

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
            return redirect(url_for("crm_dashboard"))

        payload = filter_payload_by_columns(Task, raw_payload)
        db.session.add(Task(**payload))
        return commit_with_feedback(
            "Task created successfully.",
            "Unable to create task",
            "crm_dashboard",
        )

    # =====================================================
    # HRIS ROUTES
    # =====================================================

    @flask_app.route("/hris", endpoint="hris_dashboard")
    def hris_dashboard():
        return render_or_fallback("hris.html", **build_hris_context())

    @flask_app.route("/hris/employee/create", methods=["POST"])
    def create_employee_profile():
        if EmployeeProfile is None:
            flash("EmployeeProfile model is not available in models.py.", "danger")
            return redirect(url_for("hris_dashboard"))

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
        return commit_with_feedback(
            "Employee profile created successfully.",
            "Unable to create employee profile",
            "hris_dashboard",
        )

    @flask_app.route("/hris/point-log/create", methods=["POST"])
    def create_point_log():
        if PointLog is None:
            flash("PointLog model is not available in models.py.", "danger")
            return redirect(url_for("hris_dashboard"))

        raw_payload = {
            "employee_id": request.form.get("employee_id", type=int),
            "points": as_int(request.form.get("points"), 0),
            "reason": (request.form.get("reason") or "").strip(),
            "category": (request.form.get("category") or "Performance").strip(),
            "log_date": parse_date(request.form.get("log_date")) or date.today(),
        }

        payload = filter_payload_by_columns(PointLog, raw_payload)
        db.session.add(PointLog(**payload))
        return commit_with_feedback(
            "Point log created successfully.",
            "Unable to create point log",
            "hris_dashboard",
        )

    @flask_app.route("/hris/disciplinary-record/create", methods=["POST"])
    def create_disciplinary_record():
        if DisciplinaryRecord is None:
            flash("DisciplinaryRecord model is not available in models.py.", "danger")
            return redirect(url_for("hris_dashboard"))

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
        return commit_with_feedback(
            "Disciplinary record created successfully.",
            "Unable to create disciplinary record",
            "hris_dashboard",
        )

    @flask_app.route("/hris/sop-requirement/create", methods=["POST"])
    def create_sop_requirement():
        if SOPRequirement is None:
            flash("SOPRequirement model is not available in models.py.", "danger")
            return redirect(url_for("hris_dashboard"))

        raw_payload = {
            "job_title": (request.form.get("job_title") or "").strip(),
            "title": (request.form.get("title") or "").strip(),
            "requirement": (request.form.get("requirement") or "").strip(),
            "description": (request.form.get("description") or "").strip(),
            "required": request.form.get("required") == "on",
        }

        payload = filter_payload_by_columns(SOPRequirement, raw_payload)
        db.session.add(SOPRequirement(**payload))
        return commit_with_feedback(
            "SOP requirement created successfully.",
            "Unable to create SOP requirement",
            "hris_dashboard",
        )

    # =====================================================
    # ATS ROUTES
    # =====================================================

    @flask_app.route("/ats", endpoint="ats_dashboard")
    def ats_dashboard():
        return render_or_fallback("ats.html", **build_ats_context())

    @flask_app.route("/ats/candidate/create", methods=["POST"])
    def create_candidate():
        if Candidate is None:
            flash("Candidate model is not available in models.py.", "danger")
            return redirect(url_for("ats_dashboard"))

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
        return commit_with_feedback(
            "Candidate created successfully.",
            "Unable to create candidate",
            "ats_dashboard",
        )

    @flask_app.route("/ats/candidate/<int:candidate_id>/promote", methods=["POST"])
    def promote_candidate_to_orientation(candidate_id: int):
        if Candidate is None:
            flash("Candidate model is not available in models.py.", "danger")
            return redirect(url_for("ats_dashboard"))

        candidate = Candidate.query.get_or_404(candidate_id)

        try:
            if hasattr(candidate, "stage"):
                candidate.stage = "Orientation"
            if hasattr(candidate, "status"):
                candidate.status = "Onboarding"

            if OrientationChecklist is not None:
                checklist_payload = {
                    "candidate_id": candidate_id,
                    "employee_name": getattr(candidate, "full_name", None)
                    or getattr(candidate, "first_name", ""),
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

        return redirect(url_for("ats_dashboard"))

    # =====================================================
    # ORIENTATION ROUTES
    # =====================================================

    @flask_app.route("/orientation", endpoint="orientation_dashboard")
    def orientation_dashboard():
        return render_or_fallback("orientation.html", **build_orientation_context())

    @flask_app.route("/orientation/checklist/create", methods=["POST"])
    def create_orientation_checklist():
        if OrientationChecklist is None:
            flash("OrientationChecklist model is not available in models.py.", "danger")
            return redirect(url_for("orientation_dashboard"))

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
        return commit_with_feedback(
            "Orientation checklist item created successfully.",
            "Unable to create orientation checklist item",
            "orientation_dashboard",
        )

    @flask_app.route("/orientation/policy-acknowledgement/create", methods=["POST"])
    def create_policy_acknowledgement():
        if PolicyAcknowledgement is None:
            flash("PolicyAcknowledgement model is not available in models.py.", "danger")
            return redirect(url_for("orientation_dashboard"))

        raw_payload = {
            "employee_id": request.form.get("employee_id", type=int),
            "policy_name": (request.form.get("policy_name") or "").strip(),
            "acknowledged": request.form.get("acknowledged") == "on",
            "acknowledged_date": parse_date(request.form.get("acknowledged_date")) or date.today(),
            "notes": (request.form.get("notes") or "").strip(),
        }

        payload = filter_payload_by_columns(PolicyAcknowledgement, raw_payload)
        db.session.add(PolicyAcknowledgement(**payload))
        return commit_with_feedback(
            "Policy acknowledgement saved successfully.",
            "Unable to save policy acknowledgement",
            "orientation_dashboard",
        )

    @flask_app.route("/orientation/asset-assignment/create", methods=["POST"])
    def create_asset_assignment():
        if AssetAssignment is None:
            flash("AssetAssignment model is not available in models.py.", "danger")
            return redirect(url_for("orientation_dashboard"))

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
        return commit_with_feedback(
            "Asset assignment created successfully.",
            "Unable to create asset assignment",
            "orientation_dashboard",
        )

    # =====================================================
    # SG-SST ROUTES
    # =====================================================

    @flask_app.route("/sgsst", endpoint="sgsst_dashboard")
    def sgsst_dashboard():
        return render_or_fallback("sgsst.html", **build_sgsst_context())

    @flask_app.route("/sgsst/risk/create", methods=["POST"])
    def create_risk_item():
        if RiskMatrixItem is None:
            flash("RiskMatrixItem model is not available in models.py.", "danger")
            return redirect(url_for("sgsst_dashboard"))

        raw_payload = {
            "area": (request.form.get("area") or "").strip(),
            "hazard": (request.form.get("hazard") or "").strip(),
            "risk_level": (request.form.get("risk_level") or "Medium").strip(),
            "control_measure": (request.form.get("control_measure") or "").strip(),
            "responsible_party": (request.form.get("responsible_party") or "").strip(),
        }

        payload = filter_payload_by_columns(RiskMatrixItem, raw_payload)
        db.session.add(RiskMatrixItem(**payload))
        return commit_with_feedback(
            "Risk matrix item created successfully.",
            "Unable to create risk matrix item",
            "sgsst_dashboard",
        )

    @flask_app.route("/sgsst/inspection/create", methods=["POST"])
    def create_inspection_record():
        if InspectionRecord is None:
            flash("InspectionRecord model is not available in models.py.", "danger")
            return redirect(url_for("sgsst_dashboard"))

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
        return commit_with_feedback(
            "Inspection record created successfully.",
            "Unable to create inspection record",
            "sgsst_dashboard",
        )

    @flask_app.route("/sgsst/incident/create", methods=["POST"])
    def create_incident_record():
        if IncidentRecord is None:
            flash("IncidentRecord model is not available in models.py.", "danger")
            return redirect(url_for("sgsst_dashboard"))

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
        return commit_with_feedback(
            "Incident record created successfully.",
            "Unable to create incident record",
            "sgsst_dashboard",
        )

    @flask_app.route("/sgsst/training/create", methods=["POST"])
    def create_training_record():
        if TrainingRecord is None:
            flash("TrainingRecord model is not available in models.py.", "danger")
            return redirect(url_for("sgsst_dashboard"))

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
        return commit_with_feedback(
            "Training record created successfully.",
            "Unable to create training record",
            "sgsst_dashboard",
        )

    # =====================================================
    # INVENTORY ROUTES
    # =====================================================

    @flask_app.route("/inventory", endpoint="inventory_dashboard")
    def inventory_dashboard():
        return render_or_fallback("inventory.html", **build_inventory_context())

    @flask_app.route("/inventory/item/create", methods=["POST"])
    def create_inventory_item():
        if InventoryItem is None:
            flash("InventoryItem model is not available in models.py.", "danger")
            return redirect(url_for("inventory_dashboard"))

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
        return commit_with_feedback(
            "Inventory item created successfully.",
            "Unable to create inventory item",
            "inventory_dashboard",
        )

    # =====================================================
    # FINANCE ROUTES
    # =====================================================

    @flask_app.route("/finance", endpoint="finance_dashboard")
    def finance_dashboard():
        return render_or_fallback("finance.html", **build_finance_context())

    @flask_app.route("/finance/invoice/create", methods=["POST"])
    def create_invoice():
        if Invoice is None:
            flash("Invoice model is not available in models.py.", "danger")
            return redirect(url_for("finance_dashboard"))

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

        return commit_with_feedback(
            "Invoice created successfully.",
            "Unable to create invoice",
            "finance_dashboard",
        )

    @flask_app.route("/finance/ledger/create", methods=["POST"])
    def create_ledger_entry():
        if Finance is None:
            flash("Finance model is not available in models.py.", "danger")
            return redirect(url_for("finance_dashboard"))

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
        return commit_with_feedback(
            "Ledger entry created successfully.",
            "Unable to create ledger entry",
            "finance_dashboard",
        )

    # =====================================================
    # MARKETING ROUTES
    # =====================================================

    @flask_app.route("/marketing", endpoint="marketing_dashboard")
    def marketing_dashboard():
        return render_or_fallback("marketing.html", **build_marketing_context())

    @flask_app.route("/marketing/campaign/create", methods=["POST"])
    def create_marketing_campaign():
        if MarketingCampaign is None:
            flash("MarketingCampaign model is not available in models.py.", "danger")
            return redirect(url_for("marketing_dashboard"))

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
        return commit_with_feedback(
            "Marketing campaign created successfully.",
            "Unable to create marketing campaign",
            "marketing_dashboard",
        )

    # =====================================================
    # CALENDAR ROUTES
    # =====================================================

    @flask_app.route("/calendar", endpoint="calendar_dashboard")
    def calendar_dashboard():
        return render_or_fallback("calendar.html", **build_calendar_context())

    @flask_app.route("/calendar/event/create", methods=["POST"])
    def create_calendar_event():
        if CalendarEvent is None:
            flash("CalendarEvent model is not available in models.py.", "danger")
            return redirect(url_for("calendar_dashboard"))

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
        return commit_with_feedback(
            "Calendar event created successfully.",
            "Unable to create calendar event",
            "calendar_dashboard",
        )

    # =====================================================
    # TASK ROUTES
    # =====================================================

    @flask_app.route("/tasks", endpoint="tasks_dashboard")
    def tasks_dashboard():
        return render_or_fallback("tasks.html", **build_tasks_context())

    # =====================================================
    # REPORTS / ANALYTICS
    # =====================================================

    @flask_app.route("/reports-analytics", endpoint="reports_dashboard")
    def reports_dashboard():
        return render_or_fallback("reports_analytics.html", **build_reports_context())

    @flask_app.route("/api/dashboard-stats")
    def api_dashboard_stats():
        return jsonify(build_dashboard_stats())

    @flask_app.route("/api/dashboard")
    def api_dashboard():
        return jsonify(build_dashboard_payload(xiomy_ai))

    # =====================================================
    # XIOMY ROUTES
    # =====================================================

    @flask_app.route("/xiomy-page")
    def xiomy_page():
        return render_or_fallback(
            "xiomy.html",
            xiomy_status=safe_xiomy_status(xiomy_ai),
            xiomy_greeting=safe_xiomy_greeting(xiomy_ai),
            xiomy_insight=safe_xiomy_insight(xiomy_ai),
            dashboard_stats=build_dashboard_stats(),
        )

    @flask_app.route("/xiomy")
    def xiomy():
        return jsonify(
            {
                "assistant": "XIOMY",
                "status": "online",
                "system": safe_xiomy_status(xiomy_ai),
                "greeting": safe_xiomy_greeting(xiomy_ai),
                "insight": safe_xiomy_insight(xiomy_ai),
                "dashboard": build_dashboard_stats(),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    # =====================================================
    # FILE UPLOADS
    # =====================================================

    @flask_app.route("/files/upload", methods=["POST"])
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

    @flask_app.route("/search")
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
    # LEGACY ALIAS ROUTES
    # These help older templates or code continue working.
    # =====================================================

    @flask_app.route("/crm-legacy")
    def crm():
        return redirect(url_for("crm_dashboard"))

    @flask_app.route("/hris-legacy")
    def hris():
        return redirect(url_for("hris_dashboard"))

    @flask_app.route("/ats-legacy")
    def ats():
        return redirect(url_for("ats_dashboard"))

    @flask_app.route("/orientation-legacy")
    def orientation():
        return redirect(url_for("orientation_dashboard"))

    @flask_app.route("/sgsst-legacy")
    def sgsst():
        return redirect(url_for("sgsst_dashboard"))

    @flask_app.route("/finance-legacy")
    def finance():
        return redirect(url_for("finance_dashboard"))

    @flask_app.route("/inventory-legacy")
    def inventory():
        return redirect(url_for("inventory_dashboard"))

    @flask_app.route("/marketing-legacy")
    def marketing():
        return redirect(url_for("marketing_dashboard"))

    @flask_app.route("/calendar-legacy")
    def calendar_page():
        return redirect(url_for("calendar_dashboard"))

    @flask_app.route("/reports-legacy")
    def reports_analytics():
        return redirect(url_for("reports_dashboard"))

    # =====================================================
    # ERROR HANDLERS
    # =====================================================

    @flask_app.errorhandler(404)
>>>>>>> 6a700036149ddd83079e5ef7c8be09236a086406
    def not_found(error):
        return safe_render("404.html", page_title="Page Not Found", error=error), 404

<<<<<<< HEAD
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return (
            "<h1>500 - Internal Server Error</h1>"
            "<p>Something broke in the backend.</p>"
            "<p>Check logs.</p>",
            500,
        )
=======
    @flask_app.errorhandler(500)
    def server_error(error):
        try:
            db.session.rollback()
        except Exception:
            pass
        return render_or_fallback("500.html", error=error), 500
>>>>>>> 6a700036149ddd83079e5ef7c8be09236a086406

    return flask_app

# =========================================================
# GUNICORN / RENDER ENTRYPOINT
# =========================================================

app = create_app()

if __name__ == "__main__":
<<<<<<< HEAD
    port = int(os.getenv("PORT", "5000"))
    debug = bool_from_form(os.getenv("FLASK_DEBUG", "false"))
    app.run(host="0.0.0.0", port=port, debug=debug)
=======
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
>>>>>>> 6a700036149ddd83079e5ef7c8be09236a086406
