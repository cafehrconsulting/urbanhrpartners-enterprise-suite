# =========================================================
# UrbanHRPartners Enterprise Suite
# models.py
# FILE TYPE: PY
# PURPOSE: Full integrated SQLAlchemy models for CRM, HRIS,
# ATS, Orientation, SG-SST, Finance, Inventory, Marketing,
# Tasks, Notifications, and Analytics support.
# =========================================================

from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# =========================================================
# SHARED MIXINS
# =========================================================

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class StatusMixin:
    status = db.Column(db.String(100), default="Active", nullable=False, index=True)


class SoftDeleteMixin:
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)


# =========================================================
# USER / AUTH / SYSTEM
# =========================================================

class User(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(100), default="Admin", nullable=False, index=True)
    phone = db.Column(db.String(50))
    department_name = db.Column(db.String(150))
    language = db.Column(db.String(50), default="English")
    timezone = db.Column(db.String(100), default="America/New_York")
    avatar_url = db.Column(db.String(500))
    last_login_at = db.Column(db.DateTime)

    employee_profile_id = db.Column(
        db.Integer,
        db.ForeignKey("employee_profiles.id"),
        nullable=True,
        index=True,
    )

    employee_profile = db.relationship(
        "EmployeeProfile",
        foreign_keys=[employee_profile_id],
        backref=db.backref("system_users", lazy=True),
    )

    assigned_tasks = db.relationship(
        "Task",
        foreign_keys="Task.assigned_to_user_id",
        backref=db.backref("assigned_user", lazy=True),
        lazy=True,
    )

    created_tasks = db.relationship(
        "Task",
        foreign_keys="Task.created_by_user_id",
        backref=db.backref("creator_user", lazy=True),
        lazy=True,
    )

    notifications = db.relationship(
        "NotificationLog",
        backref=db.backref("user", lazy=True),
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User {self.email}>"


# =========================================================
# ORGANIZATION / HRIS CORE
# =========================================================

class Department(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    code = db.Column(db.String(50), unique=True, index=True)
    description = db.Column(db.Text)
    manager_employee_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"), index=True)

    employees = db.relationship(
        "EmployeeProfile",
        backref=db.backref("department", lazy=True),
        lazy=True,
        foreign_keys="EmployeeProfile.department_id",
    )

    def __repr__(self):
        return f"<Department {self.name}>"


class Position(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "positions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, unique=True, index=True)
    job_code = db.Column(db.String(50), unique=False, index=True)
    description = db.Column(db.Text)
    salary_band_min = db.Column(db.Float, default=0.0)
    salary_band_max = db.Column(db.Float, default=0.0)
    employment_type = db.Column(db.String(50), default="Full-Time")
    exempt_status = db.Column(db.String(50), default="Non-Exempt")
    risk_level = db.Column(db.String(50), default="Medium")
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), index=True)

    department = db.relationship(
        "Department",
        backref=db.backref("positions", lazy=True),
        foreign_keys=[department_id],
    )

    employees = db.relationship(
        "EmployeeProfile",
        backref=db.backref("position", lazy=True),
        lazy=True,
        foreign_keys="EmployeeProfile.position_id",
    )

    sop_requirements = db.relationship(
        "SOPRequirement",
        backref=db.backref("position", lazy=True),
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Position {self.title}>"


class EmployeeProfile(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "employee_profiles"

    id = db.Column(db.Integer, primary_key=True)

    employee_number = db.Column(db.String(50), unique=True, index=True)
    first_name = db.Column(db.String(120), nullable=False, index=True)
    last_name = db.Column(db.String(120), nullable=False, index=True)
    full_name = db.Column(db.String(250), nullable=False, index=True)
    email = db.Column(db.String(200), unique=True, index=True)
    personal_email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    emergency_contact_name = db.Column(db.String(150))
    emergency_contact_phone = db.Column(db.String(50))

    national_id = db.Column(db.String(100), index=True)
    tax_id = db.Column(db.String(100), index=True)
    date_of_birth = db.Column(db.Date)
    hire_date = db.Column(db.Date, index=True)
    termination_date = db.Column(db.Date)

    employment_type = db.Column(db.String(50), default="Full-Time")
    work_location = db.Column(db.String(150))
    country = db.Column(db.String(100), default="Colombia")
    city = db.Column(db.String(100))
    address = db.Column(db.String(255))

    salary = db.Column(db.Float, default=0.0)
    salary_frequency = db.Column(db.String(50), default="Monthly")
    supervisor_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"), index=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), index=True)
    position_id = db.Column(db.Integer, db.ForeignKey("positions.id"), index=True)

    profile_photo_url = db.Column(db.String(500))
    notes = db.Column(db.Text)

    supervisor = db.relationship(
        "EmployeeProfile",
        remote_side=[id],
        backref=db.backref("direct_reports", lazy=True),
        foreign_keys=[supervisor_id],
    )

    point_logs = db.relationship("PointLog", backref=db.backref("employee", lazy=True), lazy=True, cascade="all, delete-orphan")
    disciplinary_records = db.relationship("DisciplinaryRecord", backref=db.backref("employee", lazy=True), lazy=True, cascade="all, delete-orphan")
    labor_action_records = db.relationship("LaborActionRecord", backref=db.backref("employee", lazy=True), lazy=True, cascade="all, delete-orphan")
    performance_reviews = db.relationship("PerformanceReview", backref=db.backref("employee", lazy=True), lazy=True, cascade="all, delete-orphan")
    time_entries = db.relationship("TimeEntry", backref=db.backref("employee", lazy=True), lazy=True, cascade="all, delete-orphan")
    leave_requests = db.relationship("LeaveRequest", backref=db.backref("employee", lazy=True), lazy=True, cascade="all, delete-orphan")
    payroll_records = db.relationship("PayrollRecord", backref=db.backref("employee", lazy=True), lazy=True, cascade="all, delete-orphan")
    policy_acknowledgements = db.relationship("PolicyAcknowledgement", backref=db.backref("employee", lazy=True), lazy=True, cascade="all, delete-orphan")
    asset_assignments = db.relationship("AssetAssignment", backref=db.backref("employee", lazy=True), lazy=True, cascade="all, delete-orphan")
    orientation_checklists = db.relationship("OrientationChecklist", backref=db.backref("employee", lazy=True), lazy=True, cascade="all, delete-orphan")
    medical_surveillance_records = db.relationship("MedicalSurveillance", backref=db.backref("employee", lazy=True), lazy=True, cascade="all, delete-orphan")
    ppe_issues = db.relationship("PPEIssue", backref=db.backref("employee", lazy=True), lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<EmployeeProfile {self.full_name}>"


class TimeEntry(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "time_entries"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"), nullable=False, index=True)
    work_date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    clock_in = db.Column(db.DateTime)
    clock_out = db.Column(db.DateTime)
    total_hours = db.Column(db.Float, default=0.0)
    overtime_hours = db.Column(db.Float, default=0.0)
    break_minutes = db.Column(db.Integer, default=0)
    source = db.Column(db.String(50), default="Manual")
    notes = db.Column(db.Text)


class LeaveRequest(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "leave_requests"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"), nullable=False, index=True)
    leave_type = db.Column(db.String(100), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False)
    total_days = db.Column(db.Float, default=0.0)
    reason = db.Column(db.Text)
    approved_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    approval_notes = db.Column(db.Text)

    approved_by = db.relationship(
        "User",
        foreign_keys=[approved_by_user_id],
        backref=db.backref("approved_leave_requests", lazy=True),
    )


class PayrollRecord(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "payroll_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"), nullable=False, index=True)
    pay_period_start = db.Column(db.Date, nullable=False, index=True)
    pay_period_end = db.Column(db.Date, nullable=False)
    base_salary = db.Column(db.Float, default=0.0)
    overtime_pay = db.Column(db.Float, default=0.0)
    bonuses = db.Column(db.Float, default=0.0)
    deductions = db.Column(db.Float, default=0.0)
    taxes = db.Column(db.Float, default=0.0)
    benefits_cost = db.Column(db.Float, default=0.0)
    net_pay = db.Column(db.Float, default=0.0)
    payment_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50), default="Bank Transfer")
    notes = db.Column(db.Text)


class PerformanceReview(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "performance_reviews"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"), nullable=False, index=True)
    reviewer_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    review_period_start = db.Column(db.Date)
    review_period_end = db.Column(db.Date)
    overall_score = db.Column(db.Float, default=0.0)
    strengths = db.Column(db.Text)
    improvement_areas = db.Column(db.Text)
    goals = db.Column(db.Text)
    comments = db.Column(db.Text)
    next_review_date = db.Column(db.Date)

    reviewer = db.relationship(
        "User",
        foreign_keys=[reviewer_user_id],
        backref=db.backref("performance_reviews_authored", lazy=True),
    )


class PointLog(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "point_logs"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"), nullable=False, index=True)
    points = db.Column(db.Integer, nullable=False, default=0)
    point_type = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))
    recorded_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)

    recorded_by = db.relationship(
        "User",
        foreign_keys=[recorded_by_user_id],
        backref=db.backref("point_logs_recorded", lazy=True),
    )


class SOPRequirement(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "sop_requirements"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    code = db.Column(db.String(100), index=True)
    description = db.Column(db.Text)
    position_id = db.Column(db.Integer, db.ForeignKey("positions.id"), index=True)
    version = db.Column(db.String(50), default="1.0")
    effective_date = db.Column(db.Date)
    mandatory = db.Column(db.Boolean, default=True)
    document_url = db.Column(db.String(500))


class DisciplinaryRecord(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "disciplinary_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"), nullable=False, index=True)
    issued_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    record_type = db.Column(db.String(100), nullable=False, index=True)
    violation_type = db.Column(db.String(150))
    incident_date = db.Column(db.Date)
    action_date = db.Column(db.Date, default=date.today)
    summary = db.Column(db.Text, nullable=False)
    corrective_action = db.Column(db.Text)
    employee_response = db.Column(db.Text)
    follow_up_date = db.Column(db.Date)
    legal_reference = db.Column(db.String(255))

    issued_by = db.relationship(
        "User",
        foreign_keys=[issued_by_user_id],
        backref=db.backref("disciplinary_records_issued", lazy=True),
    )


class LaborActionRecord(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "labor_action_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"), nullable=False, index=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    action_type = db.Column(db.String(150), nullable=False, index=True)
    jurisdiction = db.Column(db.String(100), default="Colombia")
    legal_framework = db.Column(db.String(255))
    case_number = db.Column(db.String(100), index=True)
    filing_date = db.Column(db.Date)
    resolution_date = db.Column(db.Date)
    summary = db.Column(db.Text, nullable=False)
    outcome = db.Column(db.Text)
    next_steps = db.Column(db.Text)

    created_by = db.relationship(
        "User",
        foreign_keys=[created_by_user_id],
        backref=db.backref("labor_actions_created", lazy=True),
    )


# =========================================================
# CRM
# =========================================================

class Client(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    client_code = db.Column(db.String(50), unique=True, index=True)
    legal_name = db.Column(db.String(255), nullable=False, index=True)
    trade_name = db.Column(db.String(255), index=True)
    client_type = db.Column(db.String(100), default="Business", index=True)
    industry = db.Column(db.String(200), index=True)
    company_size = db.Column(db.String(100))
    website = db.Column(db.String(255))
    email = db.Column(db.String(200), index=True)
    phone = db.Column(db.String(50))
    whatsapp = db.Column(db.String(50))
    country = db.Column(db.String(120), index=True)
    state = db.Column(db.String(120))
    city = db.Column(db.String(120), index=True)
    address = db.Column(db.String(255))
    postal_code = db.Column(db.String(30))
    language = db.Column(db.String(100))
    tax_id_type = db.Column(db.String(50))
    tax_id_number = db.Column(db.String(100), index=True)
    annual_revenue = db.Column(db.Float, default=0.0)
    employee_count = db.Column(db.Integer, default=0)
    source = db.Column(db.String(100), index=True)
    lead_score = db.Column(db.Float, default=0.0)
    owner_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    notes = db.Column(db.Text)

    owner_user = db.relationship(
        "User",
        foreign_keys=[owner_user_id],
        backref=db.backref("owned_clients", lazy=True),
    )

    contacts = db.relationship("ClientContact", backref=db.backref("client", lazy=True), lazy=True, cascade="all, delete-orphan")
    communications = db.relationship("CommunicationLog", backref=db.backref("client", lazy=True), lazy=True, cascade="all, delete-orphan")
    projects = db.relationship("Project", backref=db.backref("client", lazy=True), lazy=True, cascade="all, delete-orphan")
    proposals = db.relationship("Proposal", backref=db.backref("client", lazy=True), lazy=True, cascade="all, delete-orphan")
    invoices = db.relationship("Invoice", backref=db.backref("client", lazy=True), lazy=True, cascade="all, delete-orphan")
    marketing_leads = db.relationship("MarketingLead", backref=db.backref("client", lazy=True), lazy=True)
    tasks = db.relationship("Task", backref=db.backref("client", lazy=True), lazy=True)

    def __repr__(self):
        return f"<Client {self.legal_name}>"


class ClientContact(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "client_contacts"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False, index=True)
    full_name = db.Column(db.String(200), nullable=False, index=True)
    job_title = db.Column(db.String(150))
    email = db.Column(db.String(200), index=True)
    phone = db.Column(db.String(50))
    whatsapp = db.Column(db.String(50))
    preferred_contact_method = db.Column(db.String(50), default="Email")
    decision_maker = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)


class CommunicationLog(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "communication_logs"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False, index=True)
    contact_id = db.Column(db.Integer, db.ForeignKey("client_contacts.id"), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    channel = db.Column(db.String(50), nullable=False, index=True)
    subject = db.Column(db.String(255))
    message_summary = db.Column(db.Text, nullable=False)
    raw_content = db.Column(db.Text)
    action_items = db.Column(db.Text)
    next_follow_up_date = db.Column(db.Date, index=True)
    duration_minutes = db.Column(db.Integer, default=0)

    contact = db.relationship("ClientContact", backref=db.backref("communications", lazy=True), foreign_keys=[contact_id])
    user = db.relationship("User", backref=db.backref("communication_logs", lazy=True), foreign_keys=[user_id])


class Task(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), index=True)
    priority = db.Column(db.String(50), default="Medium", index=True)
    due_date = db.Column(db.Date, index=True)
    due_datetime = db.Column(db.DateTime)

    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), index=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"), index=True)

    completion_percentage = db.Column(db.Float, default=0.0)
    completed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)

    employee = db.relationship("EmployeeProfile", backref=db.backref("tasks", lazy=True), foreign_keys=[employee_id])


class Project(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    project_code = db.Column(db.String(50), unique=True, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    service_line = db.Column(db.String(150), index=True)
    start_date = db.Column(db.Date, index=True)
    end_date = db.Column(db.Date)
    estimated_budget = db.Column(db.Float, default=0.0)
    actual_cost = db.Column(db.Float, default=0.0)
    projected_revenue = db.Column(db.Float, default=0.0)
    actual_revenue = db.Column(db.Float, default=0.0)
    margin_percentage = db.Column(db.Float, default=0.0)
    project_manager_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    notes = db.Column(db.Text)

    project_manager = db.relationship("User", backref=db.backref("managed_projects", lazy=True), foreign_keys=[project_manager_user_id])
    tasks = db.relationship("Task", backref=db.backref("project", lazy=True), lazy=True)
    inventory_movements = db.relationship("InventoryMovement", backref=db.backref("project", lazy=True), lazy=True)
    expenses = db.relationship("Expense", backref=db.backref("project", lazy=True), lazy=True)


class Proposal(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "proposals"

    id = db.Column(db.Integer, primary_key=True)
    proposal_number = db.Column(db.String(50), unique=True, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    service_description = db.Column(db.Text)
    proposed_value = db.Column(db.Float, default=0.0)
    issue_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    accepted_date = db.Column(db.Date)
    version = db.Column(db.String(50), default="1.0")
    document_url = db.Column(db.String(500))
    notes = db.Column(db.Text)


# =========================================================
# FINANCE
# =========================================================

class ChartOfAccount(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "chart_of_accounts"

    id = db.Column(db.Integer, primary_key=True)
    account_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    account_name = db.Column(db.String(200), nullable=False, index=True)
    account_type = db.Column(db.String(100), nullable=False, index=True)
    parent_account_id = db.Column(db.Integer, db.ForeignKey("chart_of_accounts.id"), index=True)
    description = db.Column(db.Text)

    parent_account = db.relationship(
        "ChartOfAccount",
        remote_side=[id],
        backref=db.backref("child_accounts", lazy=True),
        foreign_keys=[parent_account_id],
    )


class JournalEntry(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "journal_entries"

    id = db.Column(db.Integer, primary_key=True)
    entry_number = db.Column(db.String(50), unique=True, index=True)
    entry_date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    memo = db.Column(db.Text)
    reference_type = db.Column(db.String(100), index=True)
    reference_id = db.Column(db.Integer, index=True)
    posted_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)

    posted_by = db.relationship("User", backref=db.backref("journal_entries_posted", lazy=True), foreign_keys=[posted_by_user_id])
    lines = db.relationship("JournalEntryLine", backref=db.backref("journal_entry", lazy=True), lazy=True, cascade="all, delete-orphan")


class JournalEntryLine(db.Model, TimestampMixin):
    __tablename__ = "journal_entry_lines"

    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey("journal_entries.id"), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey("chart_of_accounts.id"), nullable=False, index=True)
    description = db.Column(db.String(255))
    debit = db.Column(db.Float, default=0.0)
    credit = db.Column(db.Float, default=0.0)

    account = db.relationship("ChartOfAccount", backref=db.backref("journal_lines", lazy=True), foreign_keys=[account_id])


class Invoice(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), index=True)
    issue_date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    due_date = db.Column(db.Date, index=True)
    subtotal = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    balance_due = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default="COP")
    notes = db.Column(db.Text)

    project = db.relationship("Project", backref=db.backref("invoices", lazy=True), foreign_keys=[project_id])
    payments = db.relationship("Payment", backref=db.backref("invoice", lazy=True), lazy=True, cascade="all, delete-orphan")
    items = db.relationship("InvoiceLineItem", backref=db.backref("invoice", lazy=True), lazy=True, cascade="all, delete-orphan")


class InvoiceLineItem(db.Model, TimestampMixin):
    __tablename__ = "invoice_line_items"

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=False, index=True)
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float, default=1.0)
    unit_price = db.Column(db.Float, default=0.0)
    line_total = db.Column(db.Float, default=0.0)


class Payment(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=False, index=True)
    payment_date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    payment_method = db.Column(db.String(50), default="Bank Transfer")
    reference_number = db.Column(db.String(100), index=True)
    received_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    notes = db.Column(db.Text)

    received_by = db.relationship("User", backref=db.backref("payments_received", lazy=True), foreign_keys=[received_by_user_id])


class ExpenseCategory(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "expense_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)


class Expense(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    expense_number = db.Column(db.String(50), unique=True, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("expense_categories.id"), index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), index=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), index=True)
    expense_date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Float, default=0.0, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(50), default="Unpaid", index=True)
    payment_method = db.Column(db.String(50))
    receipt_url = db.Column(db.String(500))
    entered_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)

    category = db.relationship("ExpenseCategory", backref=db.backref("expenses", lazy=True), foreign_keys=[category_id])
    vendor = db.relationship("Vendor", backref=db.backref("expenses", lazy=True), foreign_keys=[vendor_id])
    entered_by = db.relationship("User", backref=db.backref("expenses_entered", lazy=True), foreign_keys=[entered_by_user_id])


class Budget(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    fiscal_year = db.Column(db.String(20), nullable=False, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), index=True)
    planned_amount = db.Column(db.Float, default=0.0)
    actual_amount = db.Column(db.Float, default=0.0)
    variance_amount = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)

    department = db.relationship("Department", backref=db.backref("budgets", lazy=True), foreign_keys=[department_id])
    project = db.relationship("Project", backref=db.backref("budgets", lazy=True), foreign_keys=[project_id])


# =========================================================
# VENDORS / INVENTORY / ASSETS
# =========================================================

class Vendor(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "vendors"

    id = db.Column(db.Integer, primary_key=True)
    vendor_code = db.Column(db.String(50), unique=True, index=True)
    legal_name = db.Column(db.String(255), nullable=False, index=True)
    contact_name = db.Column(db.String(200))
    email = db.Column(db.String(200), index=True)
    phone = db.Column(db.String(50))
    website = db.Column(db.String(255))
    country = db.Column(db.String(120))
    city = db.Column(db.String(120))
    address = db.Column(db.String(255))
    tax_id = db.Column(db.String(100), index=True)
    notes = db.Column(db.Text)


class InventoryCategory(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "inventory_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)


class InventoryItem(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "inventory_items"

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(100), unique=True, index=True)
    barcode = db.Column(db.String(150), unique=True, index=True)
    qr_code = db.Column(db.String(150), unique=True, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey("inventory_categories.id"), index=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), index=True)
    unit_of_measure = db.Column(db.String(50), default="Unit")
    cost_price = db.Column(db.Float, default=0.0)
    sale_price = db.Column(db.Float, default=0.0)
    quantity_on_hand = db.Column(db.Float, default=0.0)
    reorder_level = db.Column(db.Float, default=0.0)
    location = db.Column(db.String(150), index=True)
    serial_number = db.Column(db.String(150), index=True)
    is_asset = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)

    category = db.relationship("InventoryCategory", backref=db.backref("items", lazy=True), foreign_keys=[category_id])
    vendor = db.relationship("Vendor", backref=db.backref("inventory_items", lazy=True), foreign_keys=[vendor_id])
    movements = db.relationship("InventoryMovement", backref=db.backref("item", lazy=True), lazy=True, cascade="all, delete-orphan")
    assignments = db.relationship("AssetAssignment", backref=db.backref("item", lazy=True), lazy=True, cascade="all, delete-orphan")
    ppe_issues = db.relationship("PPEIssue", backref=db.backref("inventory_item", lazy=True), lazy=True, cascade="all, delete-orphan")


class InventoryMovement(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "inventory_movements"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), index=True)
    movement_type = db.Column(db.String(50), nullable=False, index=True)
    quantity = db.Column(db.Float, default=0.0, nullable=False)
    movement_date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    reference_type = db.Column(db.String(100), index=True)
    reference_id = db.Column(db.Integer, index=True)
    notes = db.Column(db.Text)
    recorded_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)

    recorded_by = db.relationship("User", backref=db.backref("inventory_movements_recorded", lazy=True), foreign_keys=[recorded_by_user_id])


class AssetAssignment(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "asset_assignments"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"), nullable=False, index=True)
    item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"), nullable=False, index=True)
    assigned_date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    expected_return_date = db.Column(db.Date)
    actual_return_date = db.Column(db.Date)
    condition_on_issue = db.Column(db.String(100))
    condition_on_return = db.Column(db.String(100))
    notes = db.Column(db.Text)


# =========================================================
# ATS
# =========================================================

class JobPosting(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "job_postings"

    id = db.Column(db.Integer, primary_key=True)
    requisition_code = db.Column(db.String(50), unique=True, index=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), index=True)
    position_id = db.Column(db.Integer, db.ForeignKey("positions.id"), index=True)
    hiring_manager_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    employment_type = db.Column(db.String(50), default="Full-Time")
    location = db.Column(db.String(150))
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    compensation_min = db.Column(db.Float, default=0.0)
    compensation_max = db.Column(db.Float, default=0.0)
    opening_date = db.Column(db.Date, index=True)
    closing_date = db.Column(db.Date)
    vacancies = db.Column(db.Integer, default=1)

    department = db.relationship("Department", backref=db.backref("job_postings", lazy=True), foreign_keys=[department_id])
    position = db.relationship("Position", backref=db.backref("job_postings", lazy=True), foreign_keys=[position_id])
    hiring_manager = db.relationship("User", backref=db.backref("job_postings_managed", lazy=True), foreign_keys=[hiring_manager_user_id])
    candidates = db.relationship("CandidateApplication", backref=db.backref("job_posting", lazy=True), lazy=True, cascade="all, delete-orphan")


class Candidate(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "candidates"

    id = db.Column(db.Integer, primary_key=True)
    candidate_code = db.Column(db.String(50), unique=True, index=True)
    first_name = db.Column(db.String(120), nullable=False, index=True)
    last_name = db.Column(db.String(120), nullable=False, index=True)
    full_name = db.Column(db.String(250), nullable=False, index=True)
    email = db.Column(db.String(200), nullable=False, index=True)
    phone = db.Column(db.String(50))
    city = db.Column(db.String(120), index=True)
    country = db.Column(db.String(120), index=True)
    linkedin_url = db.Column(db.String(500))
    portfolio_url = db.Column(db.String(500))
    source = db.Column(db.String(100), index=True)
    years_of_experience = db.Column(db.Float, default=0.0)
    current_employer = db.Column(db.String(200))
    desired_salary = db.Column(db.Float, default=0.0)
    resume_file_url = db.Column(db.String(500))
    parsed_resume_text = db.Column(db.Text)
    ats_score = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)

    applications = db.relationship("CandidateApplication", backref=db.backref("candidate", lazy=True), lazy=True, cascade="all, delete-orphan")
    interviews = db.relationship("Interview", backref=db.backref("candidate", lazy=True), lazy=True, cascade="all, delete-orphan")
    resume_profiles = db.relationship("ResumeProfile", backref=db.backref("candidate", lazy=True), lazy=True, cascade="all, delete-orphan")


class CandidateApplication(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "candidate_applications"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False, index=True)
    job_posting_id = db.Column(db.Integer, db.ForeignKey("job_postings.id"), nullable=False, index=True)
    stage = db.Column(db.String(100), default="Applied", index=True)
    application_date = db.Column(db.Date, default=date.today, index=True)
    screening_score = db.Column(db.Float, default=0.0)
    recruiter_notes = db.Column(db.Text)
    disposition_reason = db.Column(db.String(255))
    hired_employee_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"), index=True)

    hired_employee = db.relationship("EmployeeProfile", backref=db.backref("source_applications", lazy=True), foreign_keys=[hired_employee_id])


class Interview(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "interviews"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False, index=True)
    application_id = db.Column(db.Integer, db.ForeignKey("candidate_applications.id"), index=True)
    interview_type = db.Column(db.String(100), default="Phone Screen", index=True)
    scheduled_at = db.Column(db.DateTime, index=True)
    interviewer_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    location = db.Column(db.String(255))
    score = db.Column(db.Float, default=0.0)
    feedback = db.Column(db.Text)

    application = db.relationship("CandidateApplication", backref=db.backref("interviews", lazy=True), foreign_keys=[application_id])
    interviewer = db.relationship("User", backref=db.backref("interviews_conducted", lazy=True), foreign_keys=[interviewer_user_id])


class ResumeProfile(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "resume_profiles"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False, index=True)
    target_role = db.Column(db.String(150), index=True)
    professional_summary = db.Column(db.Text)
    skills = db.Column(db.Text)
    experience_text = db.Column(db.Text)
    education_text = db.Column(db.Text)
    certifications_text = db.Column(db.Text)
    ats_optimized = db.Column(db.Boolean, default=False)
    language = db.Column(db.String(50), default="English")
    version_name = db.Column(db.String(100), default="Default", index=True)


# =========================================================
# ORIENTATION / ONBOARDING
# =========================================================

class OrientationSession(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "orientation_sessions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    session_date = db.Column(db.Date, index=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    facilitator_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    location = db.Column(db.String(255))
    description = db.Column(db.Text)

    facilitator = db.relationship("User", backref=db.backref("orientation_sessions", lazy=True), foreign_keys=[facilitator_user_id])


class OrientationChecklist(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "orientation_checklists"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"), nullable=False, index=True)
    application_id = db.Column(db.Integer, db.ForeignKey("candidate_applications.id"), index=True)
    orientation_session_id = db.Column(db.Integer, db.ForeignKey("orientation_sessions.id"), index=True)
    task_name = db.Column(db.String(255), nullable=False, index=True)
    task_category = db.Column(db.String(100), index=True)
    completed = db.Column(db.Boolean, default=False, index=True)
    completed_date = db.Column(db.Date)
    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    notes = db.Column(db.Text)

    application = db.relationship("CandidateApplication", backref=db.backref("orientation_checklists", lazy=True), foreign_keys=[application_id])
    orientation_session = db.relationship("OrientationSession", backref=db.backref("checklists", lazy=True), foreign_keys=[orientation_session_id])
    assigned_to = db.relationship("User", backref=db.backref("orientation_checklists_assigned", lazy=True), foreign_keys=[assigned_to_user_id])


class PolicyAcknowledgement(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "policy_acknowledgements"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"), nullable=False, index=True)
    policy_name = db.Column(db.String(255), nullable=False, index=True)
    policy_version = db.Column(db.String(50), default="1.0")
    acknowledgement_date = db.Column(db.Date, default=date.today, index=True)
    document_url = db.Column(db.String(500))
    digital_signature_name = db.Column(db.String(200))
    acknowledgement_text = db.Column(db.Text)


# =========================================================
# SG-SST / SAFETY
# =========================================================

class SafetyPolicy(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "safety_policies"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    code = db.Column(db.String(100), index=True)
    version = db.Column(db.String(50), default="1.0")
    effective_date = db.Column(db.Date, index=True)
    owner_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    content = db.Column(db.Text)
    document_url = db.Column(db.String(500))

    owner = db.relationship("User", backref=db.backref("safety_policies_owned", lazy=True), foreign_keys=[owner_user_id])


class LegalRequirement(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "legal_requirements"

    id = db.Column(db.Integer, primary_key=True)
    jurisdiction = db.Column(db.String(100), nullable=False, default="Colombia", index=True)
    law_name = db.Column(db.String(255), nullable=False, index=True)
    article_reference = db.Column(db.String(255))
    subject_area = db.Column(db.String(150), index=True)
    requirement_text = db.Column(db.Text, nullable=False)
    compliance_frequency = db.Column(db.String(100))
    responsible_area = db.Column(db.String(150))
    evidence_required = db.Column(db.Text)
    source_url = db.Column(db.String(500))


class RiskMatrix(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "risk_matrix"

    id = db.Column(db.Integer, primary_key=True)
    process_name = db.Column(db.String(200), nullable=False, index=True)
    activity = db.Column(db.String(255), nullable=False, index=True)
    hazard = db.Column(db.String(255), nullable=False, index=True)
    hazard_classification = db.Column(db.String(150), index=True)
    possible_effects = db.Column(db.Text)
    existing_controls = db.Column(db.Text)
    probability = db.Column(db.Integer, default=1)
    consequence = db.Column(db.Integer, default=1)
    risk_level = db.Column(db.String(100), index=True)
    intervention_measures = db.Column(db.Text)
    responsible_person = db.Column(db.String(150))
    review_date = db.Column(db.Date, index=True)


class Inspection(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "inspections"

    id = db.Column(db.Integer, primary_key=True)
    inspection_type = db.Column(db.String(150), nullable=False, index=True)
    area = db.Column(db.String(150), index=True)
    inspection_date = db.Column(db.Date, default=date.today, index=True)
    inspector_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    findings = db.Column(db.Text)
    non_conformities = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    follow_up_date = db.Column(db.Date)

    inspector = db.relationship("User", backref=db.backref("inspections_conducted", lazy=True), foreign_keys=[inspector_user_id])


class Incident(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "incidents"

    id = db.Column(db.Integer, primary_key=True)
    incident_number = db.Column(db.String(50), unique=True, index=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"), index=True)
    incident_date = db.Column(db.Date, nullable=False, index=True)
    incident_time = db.Column(db.String(20))
    location = db.Column(db.String(255), index=True)
    incident_type = db.Column(db.String(150), index=True)
    severity = db.Column(db.String(100), index=True)
    description = db.Column(db.Text, nullable=False)
    immediate_action = db.Column(db.Text)
    lost_time = db.Column(db.Boolean, default=False)
    reported_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)

    employee = db.relationship("EmployeeProfile", backref=db.backref("incidents", lazy=True), foreign_keys=[employee_id])
    reported_by = db.relationship("User", backref=db.backref("incidents_reported", lazy=True), foreign_keys=[reported_by_user_id])
    investigations = db.relationship("IncidentInvestigation", backref=db.backref("incident", lazy=True), lazy=True, cascade="all, delete-orphan")


class IncidentInvestigation(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "incident_investigations"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=False, index=True)
    investigator_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    root_cause = db.Column(db.Text)
    contributing_factors = db.Column(db.Text)
    corrective_actions = db.Column(db.Text)
    preventive_actions = db.Column(db.Text)
    closure_date = db.Column(db.Date)

    investigator = db.relationship("User", backref=db.backref("incident_investigations", lazy=True), foreign_keys=[investigator_user_id])


class SafetyTraining(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "safety_trainings"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    topic = db.Column(db.String(200), index=True)
    training_date = db.Column(db.Date, index=True)
    trainer_name = db.Column(db.String(150))
    duration_hours = db.Column(db.Float, default=0.0)
    audience = db.Column(db.String(150))
    evidence_url = db.Column(db.String(500))
    notes = db.Column(db.Text)


class PPEIssue(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "ppe_issues"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"), nullable=False, index=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"), nullable=False, index=True)
    issue_date = db.Column(db.Date, default=date.today, index=True)
    replacement_due_date = db.Column(db.Date)
    quantity = db.Column(db.Float, default=1.0)
    condition = db.Column(db.String(100))
    notes = db.Column(db.Text)


class MedicalSurveillance(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "medical_surveillance"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"), nullable=False, index=True)
    exam_type = db.Column(db.String(150), nullable=False, index=True)
    exam_date = db.Column(db.Date, index=True)
    provider_name = db.Column(db.String(200))
    fitness_result = db.Column(db.String(100), index=True)
    restrictions = db.Column(db.Text)
    next_exam_date = db.Column(db.Date)
    notes = db.Column(db.Text)


class EmergencyDrill(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "emergency_drills"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    drill_date = db.Column(db.Date, index=True)
    scenario = db.Column(db.String(255))
    location = db.Column(db.String(255))
    participants_count = db.Column(db.Integer, default=0)
    observations = db.Column(db.Text)
    improvement_actions = db.Column(db.Text)


class Contractor(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "contractors"

    id = db.Column(db.Integer, primary_key=True)
    legal_name = db.Column(db.String(255), nullable=False, index=True)
    contact_name = db.Column(db.String(200))
    email = db.Column(db.String(200), index=True)
    phone = db.Column(db.String(50))
    service_type = db.Column(db.String(150), index=True)
    tax_id = db.Column(db.String(100), index=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    safety_documents_status = db.Column(db.String(100), default="Pending", index=True)
    notes = db.Column(db.Text)

    evaluations = db.relationship("ContractorEvaluation", backref=db.backref("contractor", lazy=True), lazy=True, cascade="all, delete-orphan")


class ContractorEvaluation(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "contractor_evaluations"

    id = db.Column(db.Integer, primary_key=True)
    contractor_id = db.Column(db.Integer, db.ForeignKey("contractors.id"), nullable=False, index=True)
    evaluation_date = db.Column(db.Date, default=date.today, index=True)
    evaluator_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    score = db.Column(db.Float, default=0.0)
    findings = db.Column(db.Text)
    recommendations = db.Column(db.Text)

    evaluator = db.relationship("User", backref=db.backref("contractor_evaluations", lazy=True), foreign_keys=[evaluator_user_id])


class SafetyAudit(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "safety_audits"

    id = db.Column(db.Integer, primary_key=True)
    audit_name = db.Column(db.String(255), nullable=False, index=True)
    audit_date = db.Column(db.Date, index=True)
    auditor_name = db.Column(db.String(150))
    scope = db.Column(db.Text)
    findings = db.Column(db.Text)
    non_conformities = db.Column(db.Text)
    opportunities_for_improvement = db.Column(db.Text)
    overall_result = db.Column(db.String(100), index=True)


class ImprovementPlan(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "improvement_plans"

    id = db.Column(db.Integer, primary_key=True)
    source_type = db.Column(db.String(100), index=True)
    source_id = db.Column(db.Integer, index=True)
    action_item = db.Column(db.Text, nullable=False)
    responsible_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    target_date = db.Column(db.Date, index=True)
    completion_date = db.Column(db.Date)
    progress_percentage = db.Column(db.Float, default=0.0)
    evidence_url = db.Column(db.String(500))
    notes = db.Column(db.Text)

    responsible_user = db.relationship("User", backref=db.backref("improvement_plans", lazy=True), foreign_keys=[responsible_user_id])


# =========================================================
# MARKETING / LEADS
# =========================================================

class MarketingCampaign(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "marketing_campaigns"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    channel = db.Column(db.String(100), index=True)
    objective = db.Column(db.String(255))
    start_date = db.Column(db.Date, index=True)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Float, default=0.0)
    spend = db.Column(db.Float, default=0.0)
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)

    leads = db.relationship("MarketingLead", backref=db.backref("campaign", lazy=True), lazy=True, cascade="all, delete-orphan")


class MarketingLead(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "marketing_leads"

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("marketing_campaigns.id"), index=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), index=True)
    lead_name = db.Column(db.String(200), nullable=False, index=True)
    company_name = db.Column(db.String(255))
    email = db.Column(db.String(200), index=True)
    phone = db.Column(db.String(50))
    source = db.Column(db.String(100), index=True)
    lead_stage = db.Column(db.String(100), default="New", index=True)
    score = db.Column(db.Float, default=0.0)
    estimated_value = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)

    activities = db.relationship("LeadActivity", backref=db.backref("lead", lazy=True), lazy=True, cascade="all, delete-orphan")


class LeadActivity(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "lead_activities"

    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey("marketing_leads.id"), nullable=False, index=True)
    activity_type = db.Column(db.String(100), index=True)
    activity_date = db.Column(db.Date, default=date.today, index=True)
    summary = db.Column(db.Text)
    outcome = db.Column(db.String(150), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)

    user = db.relationship("User", backref=db.backref("lead_activities", lazy=True), foreign_keys=[user_id])


# =========================================================
# CALENDAR / NOTIFICATIONS / REPORTS
# =========================================================

class CalendarEvent(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "calendar_events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    start_datetime = db.Column(db.DateTime, nullable=False, index=True)
    end_datetime = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255))
    event_type = db.Column(db.String(100), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), index=True)

    user = db.relationship("User", backref=db.backref("calendar_events", lazy=True), foreign_keys=[user_id])
    client = db.relationship("Client", backref=db.backref("calendar_events", lazy=True), foreign_keys=[client_id])
    project = db.relationship("Project", backref=db.backref("calendar_events", lazy=True), foreign_keys=[project_id])


class NotificationLog(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "notification_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    channel = db.Column(db.String(50), default="In-App", index=True)
    is_read = db.Column(db.Boolean, default=False, index=True)
    read_at = db.Column(db.DateTime)
    reference_type = db.Column(db.String(100), index=True)
    reference_id = db.Column(db.Integer, index=True)


class ReportSnapshot(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "report_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    report_name = db.Column(db.String(200), nullable=False, index=True)
    module_name = db.Column(db.String(100), nullable=False, index=True)
    reporting_period = db.Column(db.String(100), index=True)
    generated_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    summary_json = db.Column(db.Text)
    notes = db.Column(db.Text)

    generated_by = db.relationship("User", backref=db.backref("report_snapshots", lazy=True), foreign_keys=[generated_by_user_id])


# =========================================================
# ANALYTICS SUPPORT
# =========================================================

class KPISetting(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "kpi_settings"

    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(100), nullable=False, index=True)
    kpi_name = db.Column(db.String(150), nullable=False, index=True)
    formula_description = db.Column(db.Text)
    target_value = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(50))


# =========================================================
# OPTIONAL DATABASE SEED HELPERS
# =========================================================

def seed_basic_departments():
    default_departments = [
        "Executive",
        "Human Resources",
        "Finance",
        "Operations",
        "Marketing",
        "Sales",
        "Technology",
        "Safety",
        "Administration",
    ]
    for name in default_departments:
        exists = Department.query.filter_by(name=name).first()
        if not exists:
            db.session.add(Department(name=name))
    db.session.commit()


def seed_basic_positions():
    default_positions = [
        "Chief Executive Officer",
        "HR Manager",
        "Recruiter",
        "HR Generalist",
        "Payroll Specialist",
        "Safety Coordinator",
        "Accountant",
        "Marketing Specialist",
        "CRM Manager",
        "Operations Analyst",
    ]
    for title in default_positions:
        exists = Position.query.filter_by(title=title).first()
        if not exists:
            db.session.add(Position(title=title))
    db.session.commit()

