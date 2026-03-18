# =========================================================
# UrbanHRPartners Enterprise Suite
# app.py
# FULL FLASK CONTROLLER ALIGNED TO ENTERPRISE models.py
# =========================================================

import os
from datetime import datetime, date
from pathlib import Path

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import func

from models import (
    db,
    User,
    Role,
    Permission,
    UserRole,
    RolePermission,
    AuditLog,
    SystemSetting,
    Notification,
    Department,
    JobTitle,
    WorkLocation,
    CostCenter,
    Client,
    Contact,
    Lead,
    Opportunity,
    Project,
    CommunicationLog,
    ClientDocument,
    Task,
    Employee,
    Attendance,
    LeaveRequest,
    PerformanceReview,
    EmployeeDocument,
    TrainingRecord,
    DisciplinaryRecord,
    LaborCase,
    JobOpening,
    Candidate,
    Resume,
    ResumeOptimizationRecord,
    Interview,
    CandidateEvaluation,
    CandidateStageHistory,
    OfferLetter,
    OrientationChecklist,
    PolicyAcknowledgement,
    SafetyPolicy,
    LegalRequirement,
    Hazard,
    AnnualWorkPlan,
    SGSSTTraining,
    SGSSTTrainingAttendance,
    MedicalSurveillance,
    Incident,
    Investigation,
    Inspection,
    CorrectiveAction,
    PPEAssignment,
    EmergencyPlan,
    EmergencyDrill,
    Contractor,
    ContractorComplianceDocument,
    SafetyAudit,
    ManagementReview,
    MinimumStandardAssessment,
    Committee,
    CommitteeMember,
    Account,
    FinancialPeriod,
    JournalEntry,
    JournalLine,
    Vendor,
    Invoice,
    InvoiceLine,
    Bill,
    BillLine,
    Payment,
    BankAccount,
    BankTransaction,
    Reconciliation,
    Budget,
    Forecast,
    RecurringTransaction,
    PurchaseOrder,
    PurchaseOrderLine,
    GoodsReceipt,
    GoodsReceiptLine,
    PayrollRecord,
    PayrollItem,
    EmployeeTaxRecord,
    TaxRate,
    InventoryCategory,
    WarehouseLocation,
    InventoryItem,
    StockMovement,
    AssetAssignment,
    MaintenanceLog,
    Campaign,
    ContentAsset,
    LeadConversion,
    KPIRecord,
    AnalyticsSnapshot,
    ReportRequest,
    ExportLog,
)


# =========================================================
# PATHS / CONFIG HELPERS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
UPLOADS_DIR = BASE_DIR / "uploads"
EXPORTS_DIR = BASE_DIR / "exports"


def normalize_database_url(raw_url: str | None) -> str:
    if not raw_url:
        return f"sqlite:///{INSTANCE_DIR / 'urbanhrpartners.db'}"
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql://", 1)
    return raw_url


def ensure_directories() -> None:
    directories = [
        INSTANCE_DIR,
        UPLOADS_DIR,
        UPLOADS_DIR / "resumes",
        UPLOADS_DIR / "client_docs",
        UPLOADS_DIR / "sgsst_docs",
        UPLOADS_DIR / "invoices",
        UPLOADS_DIR / "employee_docs",
        EXPORTS_DIR,
        EXPORTS_DIR / "reports",
        EXPORTS_DIR / "csv",
        EXPORTS_DIR / "pdf",
        EXPORTS_DIR / "xlsx",
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


# =========================================================
# SMALL UTILS
# =========================================================


def as_str(value: str | None, default: str = "") -> str:
    return (value or default).strip()


def as_float(value: str | None, default: float = 0.0) -> float:
    try:
        return float((value or "").strip())
    except (TypeError, ValueError, AttributeError):
        return default


def as_int(value: str | None, default: int = 0) -> int:
    try:
        return int((value or "").strip())
    except (TypeError, ValueError, AttributeError):
        return default


def as_bool(value: str | None) -> bool:
    return str(value).lower() in {"1", "true", "yes", "on"}


def as_date(value: str | None):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def as_datetime(value: str | None):
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def render_with_fallback(template_name: str, **context):
    templates = set(app.jinja_env.list_templates())
    if template_name in templates:
        return render_template(template_name, **context)
    fallback_name = "template_missing.html"
    if fallback_name in templates:
        context["missing_template"] = template_name
        return render_template(fallback_name, **context), 200
    return f"Template '{template_name}' is missing.", 200


def safe_commit(message: str):
    try:
        db.session.commit()
        flash(message, "success")
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        flash(f"Database error: {exc}", "danger")


def seed_defaults() -> None:
    admin_email = os.getenv("ADMIN_EMAIL", "admin@urbanhrconsulting.cloud")
    admin_password = os.getenv("ADMIN_PASSWORD", "ChangeMe123!")

    if not Role.query.filter_by(name="Admin").first():
        db.session.add(Role(name="Admin", description="Full access administrator"))
    if not Role.query.filter_by(name="HR").first():
        db.session.add(Role(name="HR", description="HR and people operations"))
    if not Role.query.filter_by(name="Finance").first():
        db.session.add(Role(name="Finance", description="Finance and accounting access"))
    db.session.commit()

    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin = User(
            email=admin_email,
            password_hash=admin_password,
            full_name="System Administrator",
            notes="Initial seeded admin user.",
        )
        db.session.add(admin)
        db.session.commit()

    admin_role = Role.query.filter_by(name="Admin").first()
    if admin_role and not UserRole.query.filter_by(user_id=admin.id, role_id=admin_role.id).first():
        db.session.add(UserRole(user_id=admin.id, role_id=admin_role.id))
        db.session.commit()


# =========================================================
# APP FACTORY
# =========================================================


def create_app() -> Flask:
    flask_app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
        instance_path=str(INSTANCE_DIR),
        instance_relative_config=True,
    )

    ensure_directories()

    flask_app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "urbanhrpartners-secret-key")
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = normalize_database_url(os.getenv("DATABASE_URL"))
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    flask_app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
    flask_app.config["UPLOAD_FOLDER"] = str(UPLOADS_DIR)

    db.init_app(flask_app)

    with flask_app.app_context():
        db.create_all()
        seed_defaults()

    return flask_app


app = create_app()


# =========================================================
# DASHBOARD / CORE PAGES
# =========================================================


@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    dashboard_stats = {
        "clients_count": Client.query.count(),
        "leads_count": Lead.query.count(),
        "projects_count": Project.query.count(),
        "employees_count": Employee.query.count(),
        "job_openings_count": JobOpening.query.count(),
        "candidates_count": Candidate.query.count(),
        "hazards_count": Hazard.query.count(),
        "incidents_count": Incident.query.count(),
        "inventory_items_count": InventoryItem.query.count(),
        "campaigns_count": Campaign.query.count(),
        "invoices_count": Invoice.query.count(),
        "bills_count": Bill.query.count(),
    }

    finance_stats = {
        "invoice_total": db.session.query(func.coalesce(func.sum(Invoice.total_amount), 0)).scalar() or 0,
        "invoice_balance_due": db.session.query(func.coalesce(func.sum(Invoice.balance_due), 0)).scalar() or 0,
        "bill_total": db.session.query(func.coalesce(func.sum(Bill.total_amount), 0)).scalar() or 0,
        "payments_total": db.session.query(func.coalesce(func.sum(Payment.amount), 0)).scalar() or 0,
    }

    recent_clients = Client.query.order_by(Client.created_at.desc()).limit(5).all()
    recent_employees = Employee.query.order_by(Employee.created_at.desc()).limit(5).all()
    recent_candidates = Candidate.query.order_by(Candidate.created_at.desc()).limit(5).all()
    recent_incidents = Incident.query.order_by(Incident.created_at.desc()).limit(5).all()

    return render_with_fallback(
        "dashboard.html",
        dashboard_stats=dashboard_stats,
        finance_stats=finance_stats,
        recent_clients=recent_clients,
        recent_employees=recent_employees,
        recent_candidates=recent_candidates,
        recent_incidents=recent_incidents,
        current_year=date.today().year,
    )


@app.route("/login")
def login():
    return render_with_fallback("login.html")


@app.route("/settings")
def settings():
    settings_list = SystemSetting.query.order_by(SystemSetting.setting_key.asc()).all()
    return render_with_fallback("settings.html", settings_list=settings_list)


@app.route("/calendar")
def calendar_page():
    tasks = Task.query.order_by(Task.due_date.asc().nulls_last()).limit(50).all()
    interviews = Interview.query.order_by(Interview.scheduled_at.asc()).limit(50).all()
    drills = EmergencyDrill.query.order_by(EmergencyDrill.drill_date.asc().nulls_last()).limit(50).all()
    return render_with_fallback("calendar.html", tasks=tasks, interviews=interviews, drills=drills)


@app.route("/search")
def search_results():
    q = as_str(request.args.get("q"))
    clients = Client.query.filter(Client.name.ilike(f"%{q}%")).limit(20).all() if q else []
    employees = Employee.query.filter(Employee.full_name.ilike(f"%{q}%")).limit(20).all() if q else []
    candidates = Candidate.query.filter(Candidate.full_name.ilike(f"%{q}%")).limit(20).all() if q else []
    projects = Project.query.filter(Project.name.ilike(f"%{q}%")).limit(20).all() if q else []
    return render_with_fallback(
        "search_results.html",
        q=q,
        clients=clients,
        employees=employees,
        candidates=candidates,
        projects=projects,
    )


# =========================================================
# CRM ROUTES
# =========================================================


@app.route("/crm")
def crm():
    clients = Client.query.order_by(Client.created_at.desc()).all()
    contacts = Contact.query.order_by(Contact.created_at.desc()).limit(50).all()
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    opportunities = Opportunity.query.order_by(Opportunity.created_at.desc()).all()
    projects = Project.query.order_by(Project.created_at.desc()).all()
    communications = CommunicationLog.query.order_by(CommunicationLog.created_at.desc()).limit(50).all()
    tasks = Task.query.filter_by(module="CRM").order_by(Task.created_at.desc()).limit(50).all()

    crm_stats = {
        "clients_count": Client.query.count(),
        "leads_count": Lead.query.count(),
        "opportunities_count": Opportunity.query.count(),
        "projects_count": Project.query.count(),
        "communications_count": CommunicationLog.query.count(),
    }

    return render_with_fallback(
        "crm.html",
        clients=clients,
        contacts=contacts,
        leads=leads,
        opportunities=opportunities,
        projects=projects,
        communications=communications,
        tasks=tasks,
        crm_stats=crm_stats,
    )


@app.route("/crm/create-client", methods=["POST"])
def create_client():
    client = Client(
        client_code=as_str(request.form.get("client_code")),
        name=as_str(request.form.get("name")),
        legal_name=as_str(request.form.get("legal_name")),
        industry=as_str(request.form.get("industry")),
        subindustry=as_str(request.form.get("subindustry")),
        country=as_str(request.form.get("country")),
        state=as_str(request.form.get("state")),
        city=as_str(request.form.get("city")),
        address=as_str(request.form.get("address")),
        website=as_str(request.form.get("website")),
        language=as_str(request.form.get("language")),
        tax_id_type=as_str(request.form.get("tax_id_type")),
        tax_id_number=as_str(request.form.get("tax_id_number")),
        phone=as_str(request.form.get("phone")),
        email=as_str(request.form.get("email")),
        status=as_str(request.form.get("status"), "Active"),
        lead_source=as_str(request.form.get("lead_source")),
        account_owner=as_str(request.form.get("account_owner")),
        health_score=as_float(request.form.get("health_score")),
        annual_revenue_estimate=as_float(request.form.get("annual_revenue_estimate")),
        employee_count_estimate=as_int(request.form.get("employee_count_estimate"), None),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(client)
    safe_commit("Client created successfully.")
    return redirect(url_for("crm"))


@app.route("/crm/create-contact", methods=["POST"])
def create_contact():
    contact = Contact(
        client_id=as_int(request.form.get("client_id")),
        first_name=as_str(request.form.get("first_name")),
        last_name=as_str(request.form.get("last_name")),
        title=as_str(request.form.get("title")),
        department=as_str(request.form.get("department")),
        email=as_str(request.form.get("email")),
        phone=as_str(request.form.get("phone")),
        mobile=as_str(request.form.get("mobile")),
        preferred_language=as_str(request.form.get("preferred_language")),
        is_primary=as_bool(request.form.get("is_primary")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(contact)
    safe_commit("Contact created successfully.")
    return redirect(url_for("crm"))


@app.route("/crm/create-lead", methods=["POST"])
def create_lead():
    lead = Lead(
        client_id=as_int(request.form.get("client_id"), None),
        lead_name=as_str(request.form.get("lead_name")),
        source=as_str(request.form.get("source")),
        campaign_name=as_str(request.form.get("campaign_name")),
        status=as_str(request.form.get("status"), "New"),
        industry=as_str(request.form.get("industry")),
        country=as_str(request.form.get("country")),
        estimated_value=as_float(request.form.get("estimated_value")),
        probability=as_float(request.form.get("probability")),
        assigned_to=as_str(request.form.get("assigned_to")),
        next_follow_up=as_date(request.form.get("next_follow_up")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(lead)
    safe_commit("Lead created successfully.")
    return redirect(url_for("crm"))


@app.route("/crm/create-opportunity", methods=["POST"])
def create_opportunity():
    opportunity = Opportunity(
        client_id=as_int(request.form.get("client_id")),
        title=as_str(request.form.get("title")),
        stage=as_str(request.form.get("stage"), "Prospecting"),
        value=as_float(request.form.get("value")),
        probability=as_float(request.form.get("probability")),
        expected_close_date=as_date(request.form.get("expected_close_date")),
        service_line=as_str(request.form.get("service_line")),
        assigned_to=as_str(request.form.get("assigned_to")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(opportunity)
    safe_commit("Opportunity created successfully.")
    return redirect(url_for("crm"))


@app.route("/crm/create-project", methods=["POST"])
def create_project():
    project = Project(
        client_id=as_int(request.form.get("client_id")),
        project_code=as_str(request.form.get("project_code")),
        name=as_str(request.form.get("name")),
        description=as_str(request.form.get("description")),
        status=as_str(request.form.get("status"), "Planned"),
        priority=as_str(request.form.get("priority"), "Medium"),
        start_date=as_date(request.form.get("start_date")),
        end_date=as_date(request.form.get("end_date")),
        budget=as_float(request.form.get("budget")),
        actual_cost=as_float(request.form.get("actual_cost")),
        revenue=as_float(request.form.get("revenue")),
        project_manager=as_str(request.form.get("project_manager")),
        cost_center_id=as_int(request.form.get("cost_center_id"), None),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(project)
    safe_commit("Project created successfully.")
    return redirect(url_for("crm"))


@app.route("/crm/create-communication-log", methods=["POST"])
def create_communication_log():
    communication = CommunicationLog(
        client_id=as_int(request.form.get("client_id")),
        contact_id=as_int(request.form.get("contact_id"), None),
        project_id=as_int(request.form.get("project_id"), None),
        communication_type=as_str(request.form.get("communication_type")),
        direction=as_str(request.form.get("direction"), "Outbound"),
        subject=as_str(request.form.get("subject")),
        summary=as_str(request.form.get("summary")),
        action_items=as_str(request.form.get("action_items")),
        follow_up_date=as_date(request.form.get("follow_up_date")),
        created_by=as_str(request.form.get("created_by")),
        attachment_path=as_str(request.form.get("attachment_path")),
    )
    db.session.add(communication)
    safe_commit("Communication log created successfully.")
    return redirect(url_for("crm"))


@app.route("/crm/create-task", methods=["POST"])
def create_task():
    task = Task(
        client_id=as_int(request.form.get("client_id"), None),
        employee_id=as_int(request.form.get("employee_id"), None),
        project_id=as_int(request.form.get("project_id"), None),
        title=as_str(request.form.get("title")),
        description=as_str(request.form.get("description")),
        status=as_str(request.form.get("status"), "Open"),
        priority=as_str(request.form.get("priority"), "Medium"),
        due_date=as_date(request.form.get("due_date")),
        completed_date=as_date(request.form.get("completed_date")),
        assigned_to=as_str(request.form.get("assigned_to")),
        module=as_str(request.form.get("module"), "CRM"),
    )
    db.session.add(task)
    safe_commit("Task created successfully.")
    return redirect(url_for("crm"))


# =========================================================
# HRIS ROUTES
# =========================================================


@app.route("/hris")
def hris():
    employees = Employee.query.order_by(Employee.created_at.desc()).all()
    departments = Department.query.order_by(Department.name.asc()).all()
    job_titles = JobTitle.query.order_by(JobTitle.title.asc()).all()
    leave_requests = LeaveRequest.query.order_by(LeaveRequest.created_at.desc()).limit(50).all()
    disciplinary_records = DisciplinaryRecord.query.order_by(DisciplinaryRecord.created_at.desc()).limit(50).all()
    labor_cases = LaborCase.query.order_by(LaborCase.created_at.desc()).limit(50).all()
    training_records = TrainingRecord.query.order_by(TrainingRecord.created_at.desc()).limit(50).all()
    payroll_records = PayrollRecord.query.order_by(PayrollRecord.created_at.desc()).limit(50).all()

    hris_stats = {
        "employees_count": Employee.query.count(),
        "departments_count": Department.query.count(),
        "leave_requests_count": LeaveRequest.query.count(),
        "disciplinary_cases_count": DisciplinaryRecord.query.count(),
        "labor_cases_count": LaborCase.query.count(),
    }

    return render_with_fallback(
        "hris.html",
        employees=employees,
        departments=departments,
        job_titles=job_titles,
        leave_requests=leave_requests,
        disciplinary_records=disciplinary_records,
        labor_cases=labor_cases,
        training_records=training_records,
        payroll_records=payroll_records,
        hris_stats=hris_stats,
    )


@app.route("/hris/add-department", methods=["POST"])
def add_department():
    department = Department(
        name=as_str(request.form.get("name")),
        code=as_str(request.form.get("code")),
        description=as_str(request.form.get("description")),
    )
    db.session.add(department)
    safe_commit("Department created successfully.")
    return redirect(url_for("hris"))


@app.route("/hris/add-job-title", methods=["POST"])
def add_job_title():
    job_title = JobTitle(
        title=as_str(request.form.get("title")),
        description=as_str(request.form.get("description")),
        salary_grade=as_str(request.form.get("salary_grade")),
    )
    db.session.add(job_title)
    safe_commit("Job title created successfully.")
    return redirect(url_for("hris"))


@app.route("/hris/add-employee", methods=["POST"])
def add_employee():
    first_name = as_str(request.form.get("first_name"))
    middle_name = as_str(request.form.get("middle_name"))
    last_name = as_str(request.form.get("last_name"))
    full_name = " ".join(part for part in [first_name, middle_name, last_name] if part).strip()

    employee = Employee(
        employee_code=as_str(request.form.get("employee_code")),
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        full_name=full_name,
        email=as_str(request.form.get("email")),
        phone=as_str(request.form.get("phone")),
        alternate_phone=as_str(request.form.get("alternate_phone")),
        address=as_str(request.form.get("address")),
        city=as_str(request.form.get("city")),
        state=as_str(request.form.get("state")),
        country=as_str(request.form.get("country")),
        national_id=as_str(request.form.get("national_id")),
        birth_date=as_date(request.form.get("birth_date")),
        gender=as_str(request.form.get("gender")),
        marital_status=as_str(request.form.get("marital_status")),
        emergency_contact_name=as_str(request.form.get("emergency_contact_name")),
        emergency_contact_phone=as_str(request.form.get("emergency_contact_phone")),
        department_id=as_int(request.form.get("department_id"), None),
        job_title_id=as_int(request.form.get("job_title_id"), None),
        manager_id=as_int(request.form.get("manager_id"), None),
        work_location_id=as_int(request.form.get("work_location_id"), None),
        employment_type=as_str(request.form.get("employment_type")),
        contract_type=as_str(request.form.get("contract_type")),
        hire_date=as_date(request.form.get("hire_date")),
        termination_date=as_date(request.form.get("termination_date")),
        employment_status=as_str(request.form.get("employment_status"), "Active"),
        salary=as_float(request.form.get("salary")),
        currency=as_str(request.form.get("currency"), "USD"),
        pay_frequency=as_str(request.form.get("pay_frequency")),
        benefits_summary=as_str(request.form.get("benefits_summary")),
        profile_photo_path=as_str(request.form.get("profile_photo_path")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(employee)
    safe_commit("Employee created successfully.")
    return redirect(url_for("hris"))


@app.route("/hris/add-attendance", methods=["POST"])
def add_attendance():
    attendance = Attendance(
        employee_id=as_int(request.form.get("employee_id")),
        attendance_date=as_date(request.form.get("attendance_date")),
        check_in=as_datetime(request.form.get("check_in")),
        check_out=as_datetime(request.form.get("check_out")),
        hours_worked=as_float(request.form.get("hours_worked")),
        status=as_str(request.form.get("status"), "Present"),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(attendance)
    safe_commit("Attendance record created successfully.")
    return redirect(url_for("hris"))


@app.route("/hris/add-leave-request", methods=["POST"])
def add_leave_request():
    leave_request = LeaveRequest(
        employee_id=as_int(request.form.get("employee_id")),
        leave_type=as_str(request.form.get("leave_type")),
        start_date=as_date(request.form.get("start_date")),
        end_date=as_date(request.form.get("end_date")),
        days_requested=as_float(request.form.get("days_requested")),
        status=as_str(request.form.get("status"), "Pending"),
        request_reason=as_str(request.form.get("request_reason")),
        approver_name=as_str(request.form.get("approver_name")),
        approval_notes=as_str(request.form.get("approval_notes")),
    )
    db.session.add(leave_request)
    safe_commit("Leave request created successfully.")
    return redirect(url_for("hris"))


@app.route("/hris/add-training-record", methods=["POST"])
def add_training_record():
    training_record = TrainingRecord(
        employee_id=as_int(request.form.get("employee_id")),
        training_name=as_str(request.form.get("training_name")),
        category=as_str(request.form.get("category")),
        provider=as_str(request.form.get("provider")),
        training_date=as_date(request.form.get("training_date")),
        expiration_date=as_date(request.form.get("expiration_date")),
        certificate_path=as_str(request.form.get("certificate_path")),
        status=as_str(request.form.get("status"), "Completed"),
        score=as_float(request.form.get("score")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(training_record)
    safe_commit("Training record created successfully.")
    return redirect(url_for("hris"))


@app.route("/hris/add-disciplinary-record", methods=["POST"])
def add_disciplinary_record():
    disciplinary_record = DisciplinaryRecord(
        employee_id=as_int(request.form.get("employee_id")),
        case_number=as_str(request.form.get("case_number")),
        country_framework=as_str(request.form.get("country_framework")),
        labor_framework=as_str(request.form.get("labor_framework")),
        incident_date=as_date(request.form.get("incident_date")),
        report_date=as_date(request.form.get("report_date")),
        incident_type=as_str(request.form.get("incident_type")),
        violation_category=as_str(request.form.get("violation_category")),
        severity_level=as_str(request.form.get("severity_level")),
        policy_violation=as_str(request.form.get("policy_violation")),
        description=as_str(request.form.get("description")),
        evidence_summary=as_str(request.form.get("evidence_summary")),
        witness_summary=as_str(request.form.get("witness_summary")),
        investigator_name=as_str(request.form.get("investigator_name")),
        action_type=as_str(request.form.get("action_type")),
        action_taken=as_str(request.form.get("action_taken")),
        suspension_days=as_int(request.form.get("suspension_days")),
        due_process_completed=as_bool(request.form.get("due_process_completed")),
        employee_response_received=as_bool(request.form.get("employee_response_received")),
        union_representation_requested=as_bool(request.form.get("union_representation_requested")),
        decision_official=as_str(request.form.get("decision_official")),
        outcome=as_str(request.form.get("outcome")),
        appeal_flag=as_bool(request.form.get("appeal_flag")),
        appeal_status=as_str(request.form.get("appeal_status")),
        status=as_str(request.form.get("status"), "Open"),
        notice_file_path=as_str(request.form.get("notice_file_path")),
        decision_file_path=as_str(request.form.get("decision_file_path")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(disciplinary_record)
    safe_commit("Disciplinary record created successfully.")
    return redirect(url_for("hris"))


@app.route("/hris/add-labor-case", methods=["POST"])
def add_labor_case():
    labor_case = LaborCase(
        employee_id=as_int(request.form.get("employee_id")),
        case_number=as_str(request.form.get("case_number")),
        framework=as_str(request.form.get("framework")),
        case_type=as_str(request.form.get("case_type")),
        subject=as_str(request.form.get("subject")),
        description=as_str(request.form.get("description")),
        filed_date=as_date(request.form.get("filed_date")),
        hearing_date=as_date(request.form.get("hearing_date")),
        response_deadline=as_date(request.form.get("response_deadline")),
        union_name=as_str(request.form.get("union_name")),
        representative_name=as_str(request.form.get("representative_name")),
        employer_representative=as_str(request.form.get("employer_representative")),
        status=as_str(request.form.get("status"), "Open"),
        resolution=as_str(request.form.get("resolution")),
        resolution_date=as_date(request.form.get("resolution_date")),
        legal_risk_level=as_str(request.form.get("legal_risk_level")),
        file_path=as_str(request.form.get("file_path")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(labor_case)
    safe_commit("Labor case created successfully.")
    return redirect(url_for("hris"))


# =========================================================
# ATS ROUTES
# =========================================================


@app.route("/ats")
def ats():
    job_openings = JobOpening.query.order_by(JobOpening.created_at.desc()).all()
    candidates = Candidate.query.order_by(Candidate.created_at.desc()).all()
    resumes = Resume.query.order_by(Resume.created_at.desc()).limit(50).all()
    interviews = Interview.query.order_by(Interview.created_at.desc()).limit(50).all()
    offers = OfferLetter.query.order_by(OfferLetter.created_at.desc()).limit(50).all()
    resume_services = ResumeOptimizationRecord.query.order_by(ResumeOptimizationRecord.created_at.desc()).limit(50).all()

    ats_stats = {
        "job_openings_count": JobOpening.query.count(),
        "candidates_count": Candidate.query.count(),
        "resumes_count": Resume.query.count(),
        "interviews_count": Interview.query.count(),
        "offers_count": OfferLetter.query.count(),
    }

    return render_with_fallback(
        "ats.html",
        job_openings=job_openings,
        candidates=candidates,
        resumes=resumes,
        interviews=interviews,
        offers=offers,
        resume_services=resume_services,
        ats_stats=ats_stats,
    )


@app.route("/ats/add-job-opening", methods=["POST"])
def add_job_opening():
    job_opening = JobOpening(
        requisition_number=as_str(request.form.get("requisition_number")),
        title=as_str(request.form.get("title")),
        department_id=as_int(request.form.get("department_id"), None),
        hiring_manager=as_str(request.form.get("hiring_manager")),
        location=as_str(request.form.get("location")),
        employment_type=as_str(request.form.get("employment_type")),
        salary_min=as_float(request.form.get("salary_min")),
        salary_max=as_float(request.form.get("salary_max")),
        currency=as_str(request.form.get("currency"), "USD"),
        openings_count=as_int(request.form.get("openings_count"), 1),
        description=as_str(request.form.get("description")),
        requirements=as_str(request.form.get("requirements")),
        status=as_str(request.form.get("status"), "Open"),
        posting_date=as_date(request.form.get("posting_date")),
        closing_date=as_date(request.form.get("closing_date")),
        source_channel=as_str(request.form.get("source_channel")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(job_opening)
    safe_commit("Job opening created successfully.")
    return redirect(url_for("ats"))


@app.route("/ats/add-candidate", methods=["POST"])
def add_candidate():
    first_name = as_str(request.form.get("first_name"))
    middle_name = as_str(request.form.get("middle_name"))
    last_name = as_str(request.form.get("last_name"))
    full_name = " ".join(part for part in [first_name, middle_name, last_name] if part).strip()

    candidate = Candidate(
        job_opening_id=as_int(request.form.get("job_opening_id"), None),
        candidate_code=as_str(request.form.get("candidate_code")),
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        full_name=full_name,
        email=as_str(request.form.get("email")),
        phone=as_str(request.form.get("phone")),
        city=as_str(request.form.get("city")),
        state=as_str(request.form.get("state")),
        country=as_str(request.form.get("country")),
        linkedin_url=as_str(request.form.get("linkedin_url")),
        portfolio_url=as_str(request.form.get("portfolio_url")),
        source=as_str(request.form.get("source")),
        stage=as_str(request.form.get("stage"), "Applied"),
        status=as_str(request.form.get("status"), "Active"),
        years_experience=as_float(request.form.get("years_experience")),
        desired_salary=as_float(request.form.get("desired_salary")),
        available_start_date=as_date(request.form.get("available_start_date")),
        recruiter_name=as_str(request.form.get("recruiter_name")),
        federal_resume_mode=as_bool(request.form.get("federal_resume_mode")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(candidate)
    safe_commit("Candidate created successfully.")
    return redirect(url_for("ats"))


@app.route("/ats/add-resume", methods=["POST"])
def add_resume():
    resume = Resume(
        candidate_id=as_int(request.form.get("candidate_id")),
        file_name=as_str(request.form.get("file_name")),
        file_path=as_str(request.form.get("file_path")),
        parsed_text=as_str(request.form.get("parsed_text")),
        skills=as_str(request.form.get("skills")),
        experience_summary=as_str(request.form.get("experience_summary")),
        education_summary=as_str(request.form.get("education_summary")),
        ats_score=as_float(request.form.get("ats_score")),
        keyword_match_score=as_float(request.form.get("keyword_match_score")),
        version_label=as_str(request.form.get("version_label")),
        is_primary=as_bool(request.form.get("is_primary")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(resume)
    safe_commit("Resume record created successfully.")
    return redirect(url_for("ats"))


@app.route("/ats/add-interview", methods=["POST"])
def add_interview():
    interview = Interview(
        candidate_id=as_int(request.form.get("candidate_id")),
        job_opening_id=as_int(request.form.get("job_opening_id")),
        interview_type=as_str(request.form.get("interview_type")),
        interview_round=as_str(request.form.get("interview_round")),
        scheduled_at=as_datetime(request.form.get("scheduled_at")),
        interviewer_name=as_str(request.form.get("interviewer_name")),
        location_or_link=as_str(request.form.get("location_or_link")),
        status=as_str(request.form.get("status"), "Scheduled"),
        feedback=as_str(request.form.get("feedback")),
        score=as_float(request.form.get("score")),
    )
    db.session.add(interview)
    safe_commit("Interview created successfully.")
    return redirect(url_for("ats"))


@app.route("/ats/add-offer-letter", methods=["POST"])
def add_offer_letter():
    offer_letter = OfferLetter(
        candidate_id=as_int(request.form.get("candidate_id")),
        job_opening_id=as_int(request.form.get("job_opening_id")),
        offer_date=as_date(request.form.get("offer_date")),
        proposed_start_date=as_date(request.form.get("proposed_start_date")),
        salary_offer=as_float(request.form.get("salary_offer")),
        currency=as_str(request.form.get("currency"), "USD"),
        employment_type=as_str(request.form.get("employment_type")),
        status=as_str(request.form.get("status"), "Draft"),
        letter_path=as_str(request.form.get("letter_path")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(offer_letter)
    safe_commit("Offer letter created successfully.")
    return redirect(url_for("ats"))


@app.route("/ats/add-resume-optimization", methods=["POST"])
def add_resume_optimization():
    optimization = ResumeOptimizationRecord(
        candidate_id=as_int(request.form.get("candidate_id")),
        target_role=as_str(request.form.get("target_role")),
        target_industry=as_str(request.form.get("target_industry")),
        job_description_text=as_str(request.form.get("job_description_text")),
        original_resume_path=as_str(request.form.get("original_resume_path")),
        optimized_resume_path=as_str(request.form.get("optimized_resume_path")),
        optimization_type=as_str(request.form.get("optimization_type")),
        ats_score_before=as_float(request.form.get("ats_score_before")),
        ats_score_after=as_float(request.form.get("ats_score_after")),
        match_score=as_float(request.form.get("match_score")),
        recommendations=as_str(request.form.get("recommendations")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(optimization)
    safe_commit("Resume optimization record created successfully.")
    return redirect(url_for("ats"))


# =========================================================
# ORIENTATION ROUTES
# =========================================================


@app.route("/orientation")
def orientation():
    orientation_checklists = OrientationChecklist.query.order_by(OrientationChecklist.created_at.desc()).all()
    policy_acknowledgements = PolicyAcknowledgement.query.order_by(PolicyAcknowledgement.created_at.desc()).all()
    employees = Employee.query.order_by(Employee.full_name.asc()).all()
    return render_with_fallback(
        "orientation.html",
        orientation_checklists=orientation_checklists,
        policy_acknowledgements=policy_acknowledgements,
        employees=employees,
    )


@app.route("/orientation/add-checklist-item", methods=["POST"])
def add_checklist_item():
    checklist_item = OrientationChecklist(
        employee_id=as_int(request.form.get("employee_id")),
        checklist_name=as_str(request.form.get("checklist_name")),
        item_name=as_str(request.form.get("item_name")),
        module=as_str(request.form.get("module")),
        responsible_person=as_str(request.form.get("responsible_person")),
        due_date=as_date(request.form.get("due_date")),
        completed=as_bool(request.form.get("completed")),
        completed_date=as_date(request.form.get("completed_date")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(checklist_item)
    safe_commit("Orientation checklist item created successfully.")
    return redirect(url_for("orientation"))


@app.route("/orientation/add-policy-acknowledgement", methods=["POST"])
def add_policy_acknowledgement():
    acknowledgement = PolicyAcknowledgement(
        employee_id=as_int(request.form.get("employee_id")),
        policy_name=as_str(request.form.get("policy_name")),
        policy_version=as_str(request.form.get("policy_version")),
        acknowledged=as_bool(request.form.get("acknowledged")),
        acknowledged_date=as_date(request.form.get("acknowledged_date")),
        file_path=as_str(request.form.get("file_path")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(acknowledgement)
    safe_commit("Policy acknowledgement created successfully.")
    return redirect(url_for("orientation"))


# =========================================================
# SG-SST ROUTES
# =========================================================


@app.route("/sgsst")
def sgsst():
    safety_policies = SafetyPolicy.query.order_by(SafetyPolicy.created_at.desc()).all()
    legal_requirements = LegalRequirement.query.order_by(LegalRequirement.created_at.desc()).all()
    hazards = Hazard.query.order_by(Hazard.created_at.desc()).all()
    annual_work_plans = AnnualWorkPlan.query.order_by(AnnualWorkPlan.created_at.desc()).all()
    incidents = Incident.query.order_by(Incident.created_at.desc()).all()
    inspections = Inspection.query.order_by(Inspection.created_at.desc()).all()
    corrective_actions = CorrectiveAction.query.order_by(CorrectiveAction.created_at.desc()).all()
    ppe_assignments = PPEAssignment.query.order_by(PPEAssignment.created_at.desc()).all()
    medical_surveillance_records = MedicalSurveillance.query.order_by(MedicalSurveillance.created_at.desc()).all()
    safety_audits = SafetyAudit.query.order_by(SafetyAudit.created_at.desc()).all()
    minimum_standard_assessments = MinimumStandardAssessment.query.order_by(MinimumStandardAssessment.created_at.desc()).all()

    sgsst_stats = {
        "hazards_count": Hazard.query.count(),
        "incidents_count": Incident.query.count(),
        "inspections_count": Inspection.query.count(),
        "corrective_actions_count": CorrectiveAction.query.count(),
        "audits_count": SafetyAudit.query.count(),
    }

    return render_with_fallback(
        "sgsst.html",
        safety_policies=safety_policies,
        legal_requirements=legal_requirements,
        hazards=hazards,
        annual_work_plans=annual_work_plans,
        incidents=incidents,
        inspections=inspections,
        corrective_actions=corrective_actions,
        ppe_assignments=ppe_assignments,
        medical_surveillance_records=medical_surveillance_records,
        safety_audits=safety_audits,
        minimum_standard_assessments=minimum_standard_assessments,
        sgsst_stats=sgsst_stats,
    )


@app.route("/sgsst/add-safety-policy", methods=["POST"])
def add_safety_policy():
    record = SafetyPolicy(
        title=as_str(request.form.get("title")),
        version=as_str(request.form.get("version")),
        effective_date=as_date(request.form.get("effective_date")),
        review_date=as_date(request.form.get("review_date")),
        approved_by=as_str(request.form.get("approved_by")),
        file_path=as_str(request.form.get("file_path")),
        description=as_str(request.form.get("description")),
    )
    db.session.add(record)
    safe_commit("Safety policy created successfully.")
    return redirect(url_for("sgsst"))


@app.route("/sgsst/add-legal-requirement", methods=["POST"])
def add_legal_requirement():
    record = LegalRequirement(
        jurisdiction=as_str(request.form.get("jurisdiction"), "Colombia"),
        law_name=as_str(request.form.get("law_name")),
        article_or_section=as_str(request.form.get("article_or_section")),
        requirement_description=as_str(request.form.get("requirement_description")),
        compliance_status=as_str(request.form.get("compliance_status"), "Pending"),
        responsible_person=as_str(request.form.get("responsible_person")),
        review_date=as_date(request.form.get("review_date")),
        evidence_path=as_str(request.form.get("evidence_path")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(record)
    safe_commit("Legal requirement created successfully.")
    return redirect(url_for("sgsst"))


@app.route("/sgsst/add-hazard", methods=["POST"])
def add_hazard():
    probability = as_int(request.form.get("probability"), 1)
    consequence = as_int(request.form.get("consequence"), 1)
    hazard = Hazard(
        hazard_code=as_str(request.form.get("hazard_code")),
        area=as_str(request.form.get("area")),
        process=as_str(request.form.get("process")),
        activity=as_str(request.form.get("activity")),
        hazard_type=as_str(request.form.get("hazard_type")),
        description=as_str(request.form.get("description")),
        exposed_population=as_str(request.form.get("exposed_population")),
        existing_controls=as_str(request.form.get("existing_controls")),
        probability=probability,
        consequence=consequence,
        risk_score=probability * consequence,
        risk_level=as_str(request.form.get("risk_level")),
        control_measures=as_str(request.form.get("control_measures")),
        responsible_person=as_str(request.form.get("responsible_person")),
        next_review_date=as_date(request.form.get("next_review_date")),
        status=as_str(request.form.get("status"), "Open"),
    )
    db.session.add(hazard)
    safe_commit("Hazard created successfully.")
    return redirect(url_for("sgsst"))


@app.route("/sgsst/add-annual-work-plan", methods=["POST"])
def add_annual_work_plan():
    record = AnnualWorkPlan(
        year=as_int(request.form.get("year"), date.today().year),
        activity=as_str(request.form.get("activity")),
        objective=as_str(request.form.get("objective")),
        responsible_person=as_str(request.form.get("responsible_person")),
        due_date=as_date(request.form.get("due_date")),
        progress_percent=as_float(request.form.get("progress_percent")),
        status=as_str(request.form.get("status"), "Pending"),
        indicator_name=as_str(request.form.get("indicator_name")),
        evidence_path=as_str(request.form.get("evidence_path")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(record)
    safe_commit("Annual work plan item created successfully.")
    return redirect(url_for("sgsst"))


@app.route("/sgsst/add-incident", methods=["POST"])
def add_incident():
    incident = Incident(
        incident_code=as_str(request.form.get("incident_code")),
        employee_id=as_int(request.form.get("employee_id"), None),
        hazard_id=as_int(request.form.get("hazard_id"), None),
        project_id=as_int(request.form.get("project_id"), None),
        incident_date=as_date(request.form.get("incident_date")),
        incident_time=as_str(request.form.get("incident_time")),
        location=as_str(request.form.get("location")),
        incident_type=as_str(request.form.get("incident_type")),
        severity=as_str(request.form.get("severity")),
        description=as_str(request.form.get("description")),
        immediate_actions=as_str(request.form.get("immediate_actions")),
        lost_time=as_bool(request.form.get("lost_time")),
        reported_by=as_str(request.form.get("reported_by")),
        status=as_str(request.form.get("status"), "Open"),
        evidence_path=as_str(request.form.get("evidence_path")),
    )
    db.session.add(incident)
    safe_commit("Incident created successfully.")
    return redirect(url_for("sgsst"))


@app.route("/sgsst/add-investigation", methods=["POST"])
def add_investigation():
    investigation = Investigation(
        incident_id=as_int(request.form.get("incident_id")),
        investigator_name=as_str(request.form.get("investigator_name")),
        methodology=as_str(request.form.get("methodology")),
        root_cause=as_str(request.form.get("root_cause")),
        contributing_factors=as_str(request.form.get("contributing_factors")),
        recommendations=as_str(request.form.get("recommendations")),
        conclusion=as_str(request.form.get("conclusion")),
        closure_date=as_date(request.form.get("closure_date")),
        status=as_str(request.form.get("status"), "Open"),
        file_path=as_str(request.form.get("file_path")),
    )
    db.session.add(investigation)
    safe_commit("Investigation created successfully.")
    return redirect(url_for("sgsst"))


@app.route("/sgsst/add-inspection", methods=["POST"])
def add_inspection():
    inspection = Inspection(
        hazard_id=as_int(request.form.get("hazard_id"), None),
        inspection_type=as_str(request.form.get("inspection_type")),
        location=as_str(request.form.get("location")),
        inspection_date=as_date(request.form.get("inspection_date")),
        inspector_name=as_str(request.form.get("inspector_name")),
        checklist_used=as_str(request.form.get("checklist_used")),
        findings=as_str(request.form.get("findings")),
        risk_level=as_str(request.form.get("risk_level")),
        corrective_actions_required=as_bool(request.form.get("corrective_actions_required")),
        status=as_str(request.form.get("status"), "Completed"),
        evidence_path=as_str(request.form.get("evidence_path")),
    )
    db.session.add(inspection)
    safe_commit("Inspection created successfully.")
    return redirect(url_for("sgsst"))


@app.route("/sgsst/add-corrective-action", methods=["POST"])
def add_corrective_action():
    record = CorrectiveAction(
        incident_id=as_int(request.form.get("incident_id"), None),
        source_type=as_str(request.form.get("source_type")),
        source_id=as_int(request.form.get("source_id"), None),
        action_type=as_str(request.form.get("action_type")),
        description=as_str(request.form.get("description")),
        responsible_person=as_str(request.form.get("responsible_person")),
        due_date=as_date(request.form.get("due_date")),
        completion_date=as_date(request.form.get("completion_date")),
        effectiveness_review=as_str(request.form.get("effectiveness_review")),
        status=as_str(request.form.get("status"), "Open"),
        evidence_path=as_str(request.form.get("evidence_path")),
    )
    db.session.add(record)
    safe_commit("Corrective action created successfully.")
    return redirect(url_for("sgsst"))


@app.route("/sgsst/add-medical-surveillance", methods=["POST"])
def add_medical_surveillance():
    record = MedicalSurveillance(
        employee_id=as_int(request.form.get("employee_id")),
        exam_type=as_str(request.form.get("exam_type")),
        exam_date=as_date(request.form.get("exam_date")),
        provider=as_str(request.form.get("provider")),
        restrictions=as_str(request.form.get("restrictions")),
        fitness_status=as_str(request.form.get("fitness_status")),
        next_exam_date=as_date(request.form.get("next_exam_date")),
        confidential_notes=as_str(request.form.get("confidential_notes")),
        file_path=as_str(request.form.get("file_path")),
    )
    db.session.add(record)
    safe_commit("Medical surveillance record created successfully.")
    return redirect(url_for("sgsst"))


@app.route("/sgsst/add-ppe-assignment", methods=["POST"])
def add_ppe_assignment():
    record = PPEAssignment(
        employee_id=as_int(request.form.get("employee_id")),
        inventory_item_id=as_int(request.form.get("inventory_item_id")),
        assignment_date=as_date(request.form.get("assignment_date")),
        return_date=as_date(request.form.get("return_date")),
        condition_on_delivery=as_str(request.form.get("condition_on_delivery")),
        signed_receipt=as_bool(request.form.get("signed_receipt")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(record)
    safe_commit("PPE assignment created successfully.")
    return redirect(url_for("sgsst"))


@app.route("/sgsst/add-safety-audit", methods=["POST"])
def add_safety_audit():
    audit = SafetyAudit(
        audit_name=as_str(request.form.get("audit_name")),
        audit_type=as_str(request.form.get("audit_type")),
        audit_date=as_date(request.form.get("audit_date")),
        auditor_name=as_str(request.form.get("auditor_name")),
        scope=as_str(request.form.get("scope")),
        findings=as_str(request.form.get("findings")),
        score=as_float(request.form.get("score")),
        status=as_str(request.form.get("status"), "Open"),
        report_path=as_str(request.form.get("report_path")),
    )
    db.session.add(audit)
    safe_commit("Safety audit created successfully.")
    return redirect(url_for("sgsst"))


# =========================================================
# FINANCE ROUTES
# =========================================================


@app.route("/finance")
def finance():
    accounts = Account.query.order_by(Account.account_code.asc()).all()
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    bills = Bill.query.order_by(Bill.created_at.desc()).all()
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    vendors = Vendor.query.order_by(Vendor.name.asc()).all()
    bank_accounts = BankAccount.query.order_by(BankAccount.created_at.desc()).all()
    budgets = Budget.query.order_by(Budget.created_at.desc()).all()
    forecasts = Forecast.query.order_by(Forecast.created_at.desc()).all()
    purchase_orders = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).all()
    payroll_records = PayrollRecord.query.order_by(PayrollRecord.created_at.desc()).all()
    tax_rates = TaxRate.query.order_by(TaxRate.created_at.desc()).all()

    finance_stats = {
        "accounts_count": Account.query.count(),
        "invoices_count": Invoice.query.count(),
        "bills_count": Bill.query.count(),
        "payments_count": Payment.query.count(),
        "invoice_total": db.session.query(func.coalesce(func.sum(Invoice.total_amount), 0)).scalar() or 0,
        "bill_total": db.session.query(func.coalesce(func.sum(Bill.total_amount), 0)).scalar() or 0,
        "payment_total": db.session.query(func.coalesce(func.sum(Payment.amount), 0)).scalar() or 0,
    }

    return render_with_fallback(
        "finance.html",
        accounts=accounts,
        invoices=invoices,
        bills=bills,
        payments=payments,
        vendors=vendors,
        bank_accounts=bank_accounts,
        budgets=budgets,
        forecasts=forecasts,
        purchase_orders=purchase_orders,
        payroll_records=payroll_records,
        tax_rates=tax_rates,
        finance_stats=finance_stats,
    )


@app.route("/finance/add-account", methods=["POST"])
def add_account():
    account = Account(
        account_code=as_str(request.form.get("account_code")),
        account_name=as_str(request.form.get("account_name")),
        account_type=as_str(request.form.get("account_type")),
        parent_account_id=as_int(request.form.get("parent_account_id"), None),
        description=as_str(request.form.get("description")),
    )
    db.session.add(account)
    safe_commit("Account created successfully.")
    return redirect(url_for("finance"))


@app.route("/finance/add-vendor", methods=["POST"])
def add_vendor():
    vendor = Vendor(
        vendor_code=as_str(request.form.get("vendor_code")),
        name=as_str(request.form.get("name")),
        tax_id=as_str(request.form.get("tax_id")),
        contact_person=as_str(request.form.get("contact_person")),
        email=as_str(request.form.get("email")),
        phone=as_str(request.form.get("phone")),
        address=as_str(request.form.get("address")),
        city=as_str(request.form.get("city")),
        country=as_str(request.form.get("country")),
        payment_terms=as_str(request.form.get("payment_terms")),
        status=as_str(request.form.get("status"), "Active"),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(vendor)
    safe_commit("Vendor created successfully.")
    return redirect(url_for("finance"))


@app.route("/finance/create-invoice", methods=["POST"])
def create_invoice():
    invoice = Invoice(
        invoice_number=as_str(request.form.get("invoice_number")),
        client_id=as_int(request.form.get("client_id")),
        project_id=as_int(request.form.get("project_id"), None),
        invoice_date=as_date(request.form.get("invoice_date")),
        due_date=as_date(request.form.get("due_date")),
        subtotal=as_float(request.form.get("subtotal")),
        tax_amount=as_float(request.form.get("tax_amount")),
        discount_amount=as_float(request.form.get("discount_amount")),
        total_amount=as_float(request.form.get("total_amount")),
        amount_paid=as_float(request.form.get("amount_paid")),
        balance_due=as_float(request.form.get("balance_due")),
        currency=as_str(request.form.get("currency"), "USD"),
        status=as_str(request.form.get("status"), "Draft"),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(invoice)
    safe_commit("Invoice created successfully.")
    return redirect(url_for("finance"))


@app.route("/finance/add-invoice-line", methods=["POST"])
def add_invoice_line():
    line = InvoiceLine(
        invoice_id=as_int(request.form.get("invoice_id")),
        description=as_str(request.form.get("description")),
        quantity=as_float(request.form.get("quantity"), 1),
        unit_price=as_float(request.form.get("unit_price")),
        line_total=as_float(request.form.get("line_total")),
        revenue_account_id=as_int(request.form.get("revenue_account_id"), None),
    )
    db.session.add(line)
    safe_commit("Invoice line created successfully.")
    return redirect(url_for("finance"))


@app.route("/finance/create-bill", methods=["POST"])
def create_bill():
    bill = Bill(
        bill_number=as_str(request.form.get("bill_number")),
        vendor_id=as_int(request.form.get("vendor_id")),
        purchase_order_id=as_int(request.form.get("purchase_order_id"), None),
        bill_date=as_date(request.form.get("bill_date")),
        due_date=as_date(request.form.get("due_date")),
        subtotal=as_float(request.form.get("subtotal")),
        tax_amount=as_float(request.form.get("tax_amount")),
        total_amount=as_float(request.form.get("total_amount")),
        amount_paid=as_float(request.form.get("amount_paid")),
        balance_due=as_float(request.form.get("balance_due")),
        status=as_str(request.form.get("status"), "Open"),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(bill)
    safe_commit("Bill created successfully.")
    return redirect(url_for("finance"))


@app.route("/finance/add-bill-line", methods=["POST"])
def add_bill_line():
    line = BillLine(
        bill_id=as_int(request.form.get("bill_id")),
        description=as_str(request.form.get("description")),
        quantity=as_float(request.form.get("quantity"), 1),
        unit_cost=as_float(request.form.get("unit_cost")),
        line_total=as_float(request.form.get("line_total")),
        expense_account_id=as_int(request.form.get("expense_account_id"), None),
        inventory_item_id=as_int(request.form.get("inventory_item_id"), None),
    )
    db.session.add(line)
    safe_commit("Bill line created successfully.")
    return redirect(url_for("finance"))


@app.route("/finance/create-payment", methods=["POST"])
def create_payment():
    payment = Payment(
        payment_number=as_str(request.form.get("payment_number")),
        invoice_id=as_int(request.form.get("invoice_id"), None),
        bill_id=as_int(request.form.get("bill_id"), None),
        payment_date=as_date(request.form.get("payment_date")),
        amount=as_float(request.form.get("amount")),
        payment_method=as_str(request.form.get("payment_method")),
        bank_account_id=as_int(request.form.get("bank_account_id"), None),
        reference=as_str(request.form.get("reference")),
        direction=as_str(request.form.get("direction")),
        status=as_str(request.form.get("status"), "Posted"),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(payment)
    safe_commit("Payment created successfully.")
    return redirect(url_for("finance"))


@app.route("/finance/add-bank-account", methods=["POST"])
def add_bank_account():
    bank_account = BankAccount(
        account_name=as_str(request.form.get("account_name")),
        bank_name=as_str(request.form.get("bank_name")),
        account_number=as_str(request.form.get("account_number")),
        currency=as_str(request.form.get("currency"), "USD"),
        opening_balance=as_float(request.form.get("opening_balance")),
        current_balance=as_float(request.form.get("current_balance")),
        status=as_str(request.form.get("status"), "Active"),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(bank_account)
    safe_commit("Bank account created successfully.")
    return redirect(url_for("finance"))


@app.route("/finance/add-budget", methods=["POST"])
def add_budget():
    budget = Budget(
        budget_name=as_str(request.form.get("budget_name")),
        fiscal_year=as_int(request.form.get("fiscal_year"), date.today().year),
        cost_center_id=as_int(request.form.get("cost_center_id"), None),
        department_id=as_int(request.form.get("department_id"), None),
        account_id=as_int(request.form.get("account_id"), None),
        amount=as_float(request.form.get("amount")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(budget)
    safe_commit("Budget created successfully.")
    return redirect(url_for("finance"))


@app.route("/finance/add-forecast", methods=["POST"])
def add_forecast():
    forecast = Forecast(
        forecast_name=as_str(request.form.get("forecast_name")),
        forecast_period=as_str(request.form.get("forecast_period")),
        module=as_str(request.form.get("module")),
        projected_revenue=as_float(request.form.get("projected_revenue")),
        projected_expense=as_float(request.form.get("projected_expense")),
        projected_profit=as_float(request.form.get("projected_profit")),
        assumptions=as_str(request.form.get("assumptions")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(forecast)
    safe_commit("Forecast created successfully.")
    return redirect(url_for("finance"))


@app.route("/finance/create-purchase-order", methods=["POST"])
def create_purchase_order():
    record = PurchaseOrder(
        po_number=as_str(request.form.get("po_number")),
        vendor_id=as_int(request.form.get("vendor_id")),
        order_date=as_date(request.form.get("order_date")),
        expected_date=as_date(request.form.get("expected_date")),
        subtotal=as_float(request.form.get("subtotal")),
        tax_amount=as_float(request.form.get("tax_amount")),
        total_amount=as_float(request.form.get("total_amount")),
        status=as_str(request.form.get("status"), "Draft"),
        approved_by=as_str(request.form.get("approved_by")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(record)
    safe_commit("Purchase order created successfully.")
    return redirect(url_for("finance"))


@app.route("/finance/add-purchase-order-line", methods=["POST"])
def add_purchase_order_line():
    line = PurchaseOrderLine(
        purchase_order_id=as_int(request.form.get("purchase_order_id")),
        inventory_item_id=as_int(request.form.get("inventory_item_id"), None),
        description=as_str(request.form.get("description")),
        quantity=as_float(request.form.get("quantity")),
        unit_cost=as_float(request.form.get("unit_cost")),
        line_total=as_float(request.form.get("line_total")),
    )
    db.session.add(line)
    safe_commit("Purchase order line created successfully.")
    return redirect(url_for("finance"))


@app.route("/finance/create-goods-receipt", methods=["POST"])
def create_goods_receipt():
    receipt = GoodsReceipt(
        receipt_number=as_str(request.form.get("receipt_number")),
        purchase_order_id=as_int(request.form.get("purchase_order_id")),
        receipt_date=as_date(request.form.get("receipt_date")),
        received_by=as_str(request.form.get("received_by")),
        status=as_str(request.form.get("status"), "Received"),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(receipt)
    safe_commit("Goods receipt created successfully.")
    return redirect(url_for("finance"))


@app.route("/finance/add-goods-receipt-line", methods=["POST"])
def add_goods_receipt_line():
    line = GoodsReceiptLine(
        goods_receipt_id=as_int(request.form.get("goods_receipt_id")),
        inventory_item_id=as_int(request.form.get("inventory_item_id")),
        quantity_received=as_float(request.form.get("quantity_received")),
        condition_notes=as_str(request.form.get("condition_notes")),
    )
    db.session.add(line)
    safe_commit("Goods receipt line created successfully.")
    return redirect(url_for("finance"))


@app.route("/finance/create-payroll-record", methods=["POST"])
def create_payroll_record():
    record = PayrollRecord(
        employee_id=as_int(request.form.get("employee_id")),
        pay_period_start=as_date(request.form.get("pay_period_start")),
        pay_period_end=as_date(request.form.get("pay_period_end")),
        gross_pay=as_float(request.form.get("gross_pay")),
        overtime_pay=as_float(request.form.get("overtime_pay")),
        bonus_pay=as_float(request.form.get("bonus_pay")),
        deductions_total=as_float(request.form.get("deductions_total")),
        taxes_total=as_float(request.form.get("taxes_total")),
        employer_cost_total=as_float(request.form.get("employer_cost_total")),
        net_pay=as_float(request.form.get("net_pay")),
        status=as_str(request.form.get("status"), "Draft"),
        journal_entry_id=as_int(request.form.get("journal_entry_id"), None),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(record)
    safe_commit("Payroll record created successfully.")
    return redirect(url_for("finance"))


@app.route("/finance/add-payroll-item", methods=["POST"])
def add_payroll_item():
    item = PayrollItem(
        payroll_record_id=as_int(request.form.get("payroll_record_id")),
        item_type=as_str(request.form.get("item_type")),
        item_name=as_str(request.form.get("item_name")),
        amount=as_float(request.form.get("amount")),
        account_id=as_int(request.form.get("account_id"), None),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(item)
    safe_commit("Payroll item created successfully.")
    return redirect(url_for("finance"))


@app.route("/finance/add-tax-rate", methods=["POST"])
def add_tax_rate():
    tax_rate = TaxRate(
        tax_name=as_str(request.form.get("tax_name")),
        jurisdiction=as_str(request.form.get("jurisdiction")),
        rate_percent=as_float(request.form.get("rate_percent")),
        tax_category=as_str(request.form.get("tax_category")),
        effective_date=as_date(request.form.get("effective_date")),
        expiration_date=as_date(request.form.get("expiration_date")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(tax_rate)
    safe_commit("Tax rate created successfully.")
    return redirect(url_for("finance"))


# =========================================================
# INVENTORY ROUTES
# =========================================================


@app.route("/inventory")
def inventory():
    categories = InventoryCategory.query.order_by(InventoryCategory.name.asc()).all()
    warehouse_locations = WarehouseLocation.query.order_by(WarehouseLocation.name.asc()).all()
    inventory_items = InventoryItem.query.order_by(InventoryItem.created_at.desc()).all()
    stock_movements = StockMovement.query.order_by(StockMovement.created_at.desc()).limit(100).all()
    asset_assignments = AssetAssignment.query.order_by(AssetAssignment.created_at.desc()).all()
    maintenance_logs = MaintenanceLog.query.order_by(MaintenanceLog.created_at.desc()).all()

    inventory_stats = {
        "categories_count": InventoryCategory.query.count(),
        "items_count": InventoryItem.query.count(),
        "stock_movements_count": StockMovement.query.count(),
        "asset_assignments_count": AssetAssignment.query.count(),
    }

    return render_with_fallback(
        "inventory.html",
        categories=categories,
        warehouse_locations=warehouse_locations,
        inventory_items=inventory_items,
        stock_movements=stock_movements,
        asset_assignments=asset_assignments,
        maintenance_logs=maintenance_logs,
        inventory_stats=inventory_stats,
    )


@app.route("/inventory/add-category", methods=["POST"])
def add_inventory_category():
    category = InventoryCategory(
        name=as_str(request.form.get("name")),
        description=as_str(request.form.get("description")),
    )
    db.session.add(category)
    safe_commit("Inventory category created successfully.")
    return redirect(url_for("inventory"))


@app.route("/inventory/add-warehouse-location", methods=["POST"])
def add_warehouse_location():
    location = WarehouseLocation(
        name=as_str(request.form.get("name")),
        code=as_str(request.form.get("code")),
        address=as_str(request.form.get("address")),
        city=as_str(request.form.get("city")),
        country=as_str(request.form.get("country")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(location)
    safe_commit("Warehouse location created successfully.")
    return redirect(url_for("inventory"))


@app.route("/inventory/add-item", methods=["POST"])
def add_inventory_item():
    item = InventoryItem(
        item_code=as_str(request.form.get("item_code")),
        name=as_str(request.form.get("name")),
        description=as_str(request.form.get("description")),
        category_id=as_int(request.form.get("category_id"), None),
        warehouse_location_id=as_int(request.form.get("warehouse_location_id"), None),
        vendor_id=as_int(request.form.get("vendor_id"), None),
        sku=as_str(request.form.get("sku")),
        serial_number=as_str(request.form.get("serial_number")),
        barcode=as_str(request.form.get("barcode")),
        qr_code=as_str(request.form.get("qr_code")),
        unit_of_measure=as_str(request.form.get("unit_of_measure"), "Unit"),
        quantity_on_hand=as_float(request.form.get("quantity_on_hand")),
        minimum_stock=as_float(request.form.get("minimum_stock")),
        maximum_stock=as_float(request.form.get("maximum_stock")),
        reorder_point=as_float(request.form.get("reorder_point")),
        unit_cost=as_float(request.form.get("unit_cost")),
        average_cost=as_float(request.form.get("average_cost")),
        sale_price=as_float(request.form.get("sale_price")),
        item_type=as_str(request.form.get("item_type"), "Inventory"),
        status=as_str(request.form.get("status"), "Active"),
        image_path=as_str(request.form.get("image_path")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(item)
    safe_commit("Inventory item created successfully.")
    return redirect(url_for("inventory"))


@app.route("/inventory/add-stock-movement", methods=["POST"])
def add_stock_movement():
    movement = StockMovement(
        inventory_item_id=as_int(request.form.get("inventory_item_id")),
        movement_type=as_str(request.form.get("movement_type")),
        quantity=as_float(request.form.get("quantity")),
        movement_date=as_date(request.form.get("movement_date")) or date.today(),
        from_location_id=as_int(request.form.get("from_location_id"), None),
        to_location_id=as_int(request.form.get("to_location_id"), None),
        reference_type=as_str(request.form.get("reference_type")),
        reference_id=as_int(request.form.get("reference_id"), None),
        scanned_code=as_str(request.form.get("scanned_code")),
        performed_by=as_str(request.form.get("performed_by")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(movement)
    safe_commit("Stock movement created successfully.")
    return redirect(url_for("inventory"))


@app.route("/inventory/assign-asset", methods=["POST"])
def assign_asset():
    assignment = AssetAssignment(
        employee_id=as_int(request.form.get("employee_id")),
        inventory_item_id=as_int(request.form.get("inventory_item_id")),
        assigned_date=as_date(request.form.get("assigned_date")),
        expected_return_date=as_date(request.form.get("expected_return_date")),
        actual_return_date=as_date(request.form.get("actual_return_date")),
        assignment_status=as_str(request.form.get("assignment_status"), "Assigned"),
        condition_on_issue=as_str(request.form.get("condition_on_issue")),
        condition_on_return=as_str(request.form.get("condition_on_return")),
        signed_receipt=as_bool(request.form.get("signed_receipt")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(assignment)
    safe_commit("Asset assignment created successfully.")
    return redirect(url_for("inventory"))


@app.route("/inventory/add-maintenance-log", methods=["POST"])
def add_maintenance_log():
    log = MaintenanceLog(
        inventory_item_id=as_int(request.form.get("inventory_item_id")),
        maintenance_type=as_str(request.form.get("maintenance_type")),
        maintenance_date=as_date(request.form.get("maintenance_date")),
        provider=as_str(request.form.get("provider")),
        cost=as_float(request.form.get("cost")),
        findings=as_str(request.form.get("findings")),
        next_due_date=as_date(request.form.get("next_due_date")),
        status=as_str(request.form.get("status"), "Completed"),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(log)
    safe_commit("Maintenance log created successfully.")
    return redirect(url_for("inventory"))


@app.route("/inventory/scan")
def inventory_scan():
    inventory_items = InventoryItem.query.order_by(InventoryItem.name.asc()).all()
    return render_with_fallback("inventory_scan.html", inventory_items=inventory_items)


# =========================================================
# MARKETING ROUTES
# =========================================================


@app.route("/marketing")
def marketing():
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
    content_assets = ContentAsset.query.order_by(ContentAsset.created_at.desc()).all()
    lead_conversions = LeadConversion.query.order_by(LeadConversion.created_at.desc()).all()

    marketing_stats = {
        "campaigns_count": Campaign.query.count(),
        "content_assets_count": ContentAsset.query.count(),
        "lead_conversions_count": LeadConversion.query.count(),
        "campaign_budget_total": db.session.query(func.coalesce(func.sum(Campaign.budget), 0)).scalar() or 0,
        "campaign_revenue_total": db.session.query(func.coalesce(func.sum(Campaign.revenue_generated), 0)).scalar() or 0,
    }

    return render_with_fallback(
        "marketing.html",
        campaigns=campaigns,
        content_assets=content_assets,
        lead_conversions=lead_conversions,
        marketing_stats=marketing_stats,
    )


@app.route("/marketing/create-campaign", methods=["POST"])
def create_campaign():
    campaign = Campaign(
        campaign_code=as_str(request.form.get("campaign_code")),
        name=as_str(request.form.get("name")),
        channel=as_str(request.form.get("channel")),
        objective=as_str(request.form.get("objective")),
        target_audience=as_str(request.form.get("target_audience")),
        start_date=as_date(request.form.get("start_date")),
        end_date=as_date(request.form.get("end_date")),
        budget=as_float(request.form.get("budget")),
        actual_spend=as_float(request.form.get("actual_spend")),
        impressions=as_int(request.form.get("impressions")),
        clicks=as_int(request.form.get("clicks")),
        leads_generated=as_int(request.form.get("leads_generated")),
        conversions=as_int(request.form.get("conversions")),
        revenue_generated=as_float(request.form.get("revenue_generated")),
        roi=as_float(request.form.get("roi")),
        status=as_str(request.form.get("status"), "Draft"),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(campaign)
    safe_commit("Campaign created successfully.")
    return redirect(url_for("marketing"))


@app.route("/marketing/add-content-asset", methods=["POST"])
def add_content_asset():
    asset = ContentAsset(
        campaign_id=as_int(request.form.get("campaign_id"), None),
        asset_name=as_str(request.form.get("asset_name")),
        asset_type=as_str(request.form.get("asset_type")),
        platform=as_str(request.form.get("platform")),
        file_path=as_str(request.form.get("file_path")),
        publish_date=as_date(request.form.get("publish_date")),
        status=as_str(request.form.get("status"), "Draft"),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(asset)
    safe_commit("Content asset created successfully.")
    return redirect(url_for("marketing"))


@app.route("/marketing/add-lead-conversion", methods=["POST"])
def add_lead_conversion():
    conversion = LeadConversion(
        lead_id=as_int(request.form.get("lead_id")),
        campaign_id=as_int(request.form.get("campaign_id"), None),
        conversion_status=as_str(request.form.get("conversion_status"), "Open"),
        conversion_date=as_date(request.form.get("conversion_date")),
        revenue_amount=as_float(request.form.get("revenue_amount")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(conversion)
    safe_commit("Lead conversion created successfully.")
    return redirect(url_for("marketing"))


# =========================================================
# REPORTS / ANALYTICS / XIOMY ROUTES
# =========================================================


@app.route("/reports-analytics")
def reports_analytics():
    kpi_records = KPIRecord.query.order_by(KPIRecord.created_at.desc()).all()
    analytics_snapshots = AnalyticsSnapshot.query.order_by(AnalyticsSnapshot.created_at.desc()).all()
    report_requests = ReportRequest.query.order_by(ReportRequest.created_at.desc()).all()
    export_logs = ExportLog.query.order_by(ExportLog.created_at.desc()).all()
    return render_with_fallback(
        "reports_analytics.html",
        kpi_records=kpi_records,
        analytics_snapshots=analytics_snapshots,
        report_requests=report_requests,
        export_logs=export_logs,
    )


@app.route("/reports-analytics/add-kpi-record", methods=["POST"])
def add_kpi_record():
    kpi = KPIRecord(
        module=as_str(request.form.get("module")),
        kpi_name=as_str(request.form.get("kpi_name")),
        kpi_value=as_float(request.form.get("kpi_value")),
        kpi_date=as_date(request.form.get("kpi_date")) or date.today(),
        unit=as_str(request.form.get("unit")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(kpi)
    safe_commit("KPI record created successfully.")
    return redirect(url_for("reports_analytics"))


@app.route("/reports-analytics/add-analytics-snapshot", methods=["POST"])
def add_analytics_snapshot():
    snapshot = AnalyticsSnapshot(
        module=as_str(request.form.get("module")),
        snapshot_name=as_str(request.form.get("snapshot_name")),
        period_label=as_str(request.form.get("period_label")),
        json_data=as_str(request.form.get("json_data")),
        summary=as_str(request.form.get("summary")),
    )
    db.session.add(snapshot)
    safe_commit("Analytics snapshot created successfully.")
    return redirect(url_for("reports_analytics"))


@app.route("/reports-analytics/add-report-request", methods=["POST"])
def add_report_request():
    report_request = ReportRequest(
        module=as_str(request.form.get("module")),
        report_name=as_str(request.form.get("report_name")),
        filters_json=as_str(request.form.get("filters_json")),
        requested_by=as_str(request.form.get("requested_by")),
        status=as_str(request.form.get("status"), "Pending"),
        generated_file_path=as_str(request.form.get("generated_file_path")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(report_request)
    safe_commit("Report request created successfully.")
    return redirect(url_for("reports_analytics"))


@app.route("/reports-analytics/add-export-log", methods=["POST"])
def add_export_log():
    export_log = ExportLog(
        module=as_str(request.form.get("module")),
        export_type=as_str(request.form.get("export_type")),
        record_count=as_int(request.form.get("record_count")),
        generated_by=as_str(request.form.get("generated_by")),
        file_path=as_str(request.form.get("file_path")),
        notes=as_str(request.form.get("notes")),
    )
    db.session.add(export_log)
    safe_commit("Export log created successfully.")
    return redirect(url_for("reports_analytics"))


@app.route("/xiomy-page")
def xiomy_page():
    dashboard_stats = {
        "clients": Client.query.count(),
        "employees": Employee.query.count(),
        "candidates": Candidate.query.count(),
        "incidents": Incident.query.count(),
        "inventory_items": InventoryItem.query.count(),
        "invoices": Invoice.query.count(),
        "campaigns": Campaign.query.count(),
    }
    return render_with_fallback("xiomy.html", dashboard_stats=dashboard_stats)


# =========================================================
# ERROR HANDLERS
# =========================================================


@app.errorhandler(404)
def not_found(error):  # noqa: ARG001
    return render_with_fallback("404.html"), 404


@app.errorhandler(500)
def internal_error(error):  # noqa: ARG001
    db.session.rollback()
    return render_with_fallback("500.html"), 500


# =========================================================
# LOCAL RUN
# =========================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
