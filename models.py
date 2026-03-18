# =========================================================
# UrbanHRPartners Enterprise Suite
# models.py
# FULL ENTERPRISE DATABASE MODELS - EXPANDED VERSION
# =========================================================

from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint, CheckConstraint

db = SQLAlchemy()


# =========================================================
# MIXINS
# =========================================================

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class SoftDeleteMixin:
    is_active = db.Column(db.Boolean, default=True, nullable=False)


# =========================================================
# CORE / SECURITY / ACCESS CONTROL
# =========================================================

class User(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50))
    profile_image_path = db.Column(db.String(255))
    last_login_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)

    user_roles = db.relationship("UserRole", backref="user", lazy=True, cascade="all, delete-orphan")
    audit_logs = db.relationship("AuditLog", backref="user", lazy=True)
    notifications = db.relationship("Notification", backref="user", lazy=True)


class Role(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)

    user_roles = db.relationship("UserRole", backref="role", lazy=True, cascade="all, delete-orphan")
    role_permissions = db.relationship("RolePermission", backref="role", lazy=True, cascade="all, delete-orphan")


class Permission(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String(80), nullable=False)
    action = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)

    role_permissions = db.relationship("RolePermission", backref="permission", lazy=True, cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("module", "action", name="uq_permission_module_action"),
    )


class UserRole(TimestampMixin, db.Model):
    __tablename__ = "user_roles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
    )


class RolePermission(TimestampMixin, db.Model):
    __tablename__ = "role_permissions"

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey("permissions.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )


class AuditLog(TimestampMixin, db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    module = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(150), nullable=False)
    target_type = db.Column(db.String(100))
    target_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(80))


class SystemSetting(TimestampMixin, db.Model):
    __tablename__ = "system_settings"

    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(120), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    description = db.Column(db.Text)


class Notification(TimestampMixin, db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    module = db.Column(db.String(80))
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    due_date = db.Column(db.DateTime)


# =========================================================
# CATALOG / REFERENCE
# =========================================================

class Department(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    code = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)

    employees = db.relationship("Employee", backref="department", lazy=True)
    job_openings = db.relationship("JobOpening", backref="department", lazy=True)
    budgets = db.relationship("Budget", backref="department", lazy=True)


class JobTitle(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "job_titles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text)
    salary_grade = db.Column(db.String(50))


class WorkLocation(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "work_locations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(255))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    country = db.Column(db.String(120))
    notes = db.Column(db.Text)


class CostCenter(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "cost_centers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    code = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text)


# =========================================================
# CRM MODULE
# =========================================================

class Client(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    client_code = db.Column(db.String(50), unique=True, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    legal_name = db.Column(db.String(255))
    industry = db.Column(db.String(255))
    subindustry = db.Column(db.String(255))
    country = db.Column(db.String(120))
    state = db.Column(db.String(120))
    city = db.Column(db.String(120))
    address = db.Column(db.String(255))
    website = db.Column(db.String(255))
    language = db.Column(db.String(100))
    tax_id_type = db.Column(db.String(50))
    tax_id_number = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(150))
    status = db.Column(db.String(50), default="Active", nullable=False)
    lead_source = db.Column(db.String(120))
    account_owner = db.Column(db.String(150))
    health_score = db.Column(db.Float, default=0)
    annual_revenue_estimate = db.Column(db.Float, default=0)
    employee_count_estimate = db.Column(db.Integer)
    notes = db.Column(db.Text)

    contacts = db.relationship("Contact", backref="client", lazy=True, cascade="all, delete-orphan")
    leads = db.relationship("Lead", backref="client", lazy=True)
    opportunities = db.relationship("Opportunity", backref="client", lazy=True)
    projects = db.relationship("Project", backref="client", lazy=True)
    communications = db.relationship("CommunicationLog", backref="client", lazy=True)
    client_documents = db.relationship("ClientDocument", backref="client", lazy=True)
    tasks = db.relationship("Task", backref="client", lazy=True)
    invoices = db.relationship("Invoice", backref="client", lazy=True)


class Contact(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False, index=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120))
    title = db.Column(db.String(120))
    department = db.Column(db.String(120))
    email = db.Column(db.String(150))
    phone = db.Column(db.String(50))
    mobile = db.Column(db.String(50))
    preferred_language = db.Column(db.String(100))
    is_primary = db.Column(db.Boolean, default=False, nullable=False)
    notes = db.Column(db.Text)


class Lead(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))
    lead_name = db.Column(db.String(255), nullable=False)
    source = db.Column(db.String(120))
    campaign_name = db.Column(db.String(150))
    status = db.Column(db.String(50), default="New", nullable=False)
    industry = db.Column(db.String(255))
    country = db.Column(db.String(120))
    estimated_value = db.Column(db.Float, default=0)
    probability = db.Column(db.Float, default=0)
    assigned_to = db.Column(db.String(150))
    next_follow_up = db.Column(db.Date)
    notes = db.Column(db.Text)

    conversions = db.relationship("LeadConversion", backref="lead", lazy=True)


class Opportunity(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "opportunities"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    stage = db.Column(db.String(80), nullable=False, default="Prospecting")
    value = db.Column(db.Float, default=0)
    probability = db.Column(db.Float, default=0)
    expected_close_date = db.Column(db.Date)
    service_line = db.Column(db.String(120))
    assigned_to = db.Column(db.String(150))
    notes = db.Column(db.Text)


class Project(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    project_code = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(80), default="Planned", nullable=False)
    priority = db.Column(db.String(50), default="Medium")
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Float, default=0)
    actual_cost = db.Column(db.Float, default=0)
    revenue = db.Column(db.Float, default=0)
    project_manager = db.Column(db.String(150))
    cost_center_id = db.Column(db.Integer, db.ForeignKey("cost_centers.id"))
    notes = db.Column(db.Text)


class CommunicationLog(TimestampMixin, db.Model):
    __tablename__ = "communication_logs"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    communication_type = db.Column(db.String(80), nullable=False)
    direction = db.Column(db.String(50), default="Outbound")
    subject = db.Column(db.String(255))
    summary = db.Column(db.Text, nullable=False)
    action_items = db.Column(db.Text)
    follow_up_date = db.Column(db.Date)
    created_by = db.Column(db.String(150))
    attachment_path = db.Column(db.String(255))


class ClientDocument(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "client_documents"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    document_name = db.Column(db.String(255), nullable=False)
    document_type = db.Column(db.String(120))
    file_path = db.Column(db.String(255), nullable=False)
    expiration_date = db.Column(db.Date)
    uploaded_by = db.Column(db.String(150))
    notes = db.Column(db.Text)


class Task(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default="Open", nullable=False)
    priority = db.Column(db.String(50), default="Medium")
    due_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    assigned_to = db.Column(db.String(150))
    module = db.Column(db.String(80))


# =========================================================
# HRIS MODULE
# =========================================================

class Employee(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(50), unique=True, index=True)
    first_name = db.Column(db.String(120), nullable=False)
    middle_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(255), nullable=False, index=True)
    email = db.Column(db.String(150), unique=True)
    phone = db.Column(db.String(50))
    alternate_phone = db.Column(db.String(50))
    address = db.Column(db.String(255))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    country = db.Column(db.String(120))
    national_id = db.Column(db.String(120))
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(50))
    marital_status = db.Column(db.String(50))
    emergency_contact_name = db.Column(db.String(150))
    emergency_contact_phone = db.Column(db.String(50))

    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    job_title_id = db.Column(db.Integer, db.ForeignKey("job_titles.id"))
    manager_id = db.Column(db.Integer, db.ForeignKey("employees.id"))
    work_location_id = db.Column(db.Integer, db.ForeignKey("work_locations.id"))

    employment_type = db.Column(db.String(80))
    contract_type = db.Column(db.String(80))
    hire_date = db.Column(db.Date)
    termination_date = db.Column(db.Date)
    employment_status = db.Column(db.String(80), default="Active", nullable=False)
    salary = db.Column(db.Float, default=0)
    currency = db.Column(db.String(10), default="USD")
    pay_frequency = db.Column(db.String(50))
    benefits_summary = db.Column(db.Text)
    profile_photo_path = db.Column(db.String(255))
    notes = db.Column(db.Text)

    manager = db.relationship("Employee", remote_side=[id], backref="team_members", lazy=True)
    attendance_logs = db.relationship("Attendance", backref="employee", lazy=True, cascade="all, delete-orphan")
    leave_requests = db.relationship("LeaveRequest", backref="employee", lazy=True)
    performance_reviews = db.relationship("PerformanceReview", backref="employee", lazy=True)
    disciplinary_records = db.relationship("DisciplinaryRecord", backref="employee", lazy=True)
    labor_cases = db.relationship("LaborCase", backref="employee", lazy=True)
    employee_documents = db.relationship("EmployeeDocument", backref="employee", lazy=True)
    training_records = db.relationship("TrainingRecord", backref="employee", lazy=True)
    policy_acknowledgements = db.relationship("PolicyAcknowledgement", backref="employee", lazy=True)
    orientation_checklists = db.relationship("OrientationChecklist", backref="employee", lazy=True)
    asset_assignments = db.relationship("AssetAssignment", backref="employee", lazy=True)
    ppe_assignments = db.relationship("PPEAssignment", backref="employee", lazy=True)
    medical_surveillance_records = db.relationship("MedicalSurveillance", backref="employee", lazy=True)
    payroll_records = db.relationship("PayrollRecord", backref="employee", lazy=True)
    tax_records = db.relationship("EmployeeTaxRecord", backref="employee", lazy=True)


class Attendance(TimestampMixin, db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    attendance_date = db.Column(db.Date, nullable=False, index=True)
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    hours_worked = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default="Present")
    notes = db.Column(db.Text)

    __table_args__ = (
        UniqueConstraint("employee_id", "attendance_date", name="uq_employee_attendance_date"),
    )


class LeaveRequest(TimestampMixin, db.Model):
    __tablename__ = "leave_requests"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    leave_type = db.Column(db.String(80), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days_requested = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default="Pending", nullable=False)
    request_reason = db.Column(db.Text)
    approver_name = db.Column(db.String(150))
    approval_notes = db.Column(db.Text)


class PerformanceReview(TimestampMixin, db.Model):
    __tablename__ = "performance_reviews"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    review_period = db.Column(db.String(100))
    reviewer_name = db.Column(db.String(150))
    score = db.Column(db.Float, default=0)
    strengths = db.Column(db.Text)
    improvement_areas = db.Column(db.Text)
    goals = db.Column(db.Text)
    status = db.Column(db.String(50), default="Draft")
    review_date = db.Column(db.Date)


class EmployeeDocument(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "employee_documents"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    document_name = db.Column(db.String(255), nullable=False)
    document_type = db.Column(db.String(120))
    file_path = db.Column(db.String(255), nullable=False)
    expiration_date = db.Column(db.Date)
    confidential = db.Column(db.Boolean, default=False, nullable=False)
    notes = db.Column(db.Text)


class TrainingRecord(TimestampMixin, db.Model):
    __tablename__ = "training_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    training_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(120))
    provider = db.Column(db.String(150))
    training_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    certificate_path = db.Column(db.String(255))
    status = db.Column(db.String(50), default="Completed")
    score = db.Column(db.Float, default=0)
    notes = db.Column(db.Text)


class DisciplinaryRecord(TimestampMixin, db.Model):
    __tablename__ = "disciplinary_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    case_number = db.Column(db.String(80), unique=True, index=True)
    country_framework = db.Column(db.String(50), nullable=False)
    labor_framework = db.Column(db.String(120))
    incident_date = db.Column(db.Date)
    report_date = db.Column(db.Date)
    incident_type = db.Column(db.String(120))
    violation_category = db.Column(db.String(120))
    severity_level = db.Column(db.String(50))
    policy_violation = db.Column(db.String(255))
    description = db.Column(db.Text, nullable=False)
    evidence_summary = db.Column(db.Text)
    witness_summary = db.Column(db.Text)
    investigator_name = db.Column(db.String(150))
    action_type = db.Column(db.String(120))
    action_taken = db.Column(db.String(255))
    suspension_days = db.Column(db.Integer, default=0)
    due_process_completed = db.Column(db.Boolean, default=False, nullable=False)
    employee_response_received = db.Column(db.Boolean, default=False, nullable=False)
    union_representation_requested = db.Column(db.Boolean, default=False, nullable=False)
    decision_official = db.Column(db.String(150))
    outcome = db.Column(db.Text)
    appeal_flag = db.Column(db.Boolean, default=False, nullable=False)
    appeal_status = db.Column(db.String(80))
    status = db.Column(db.String(50), default="Open", nullable=False)
    notice_file_path = db.Column(db.String(255))
    decision_file_path = db.Column(db.String(255))
    notes = db.Column(db.Text)


class LaborCase(TimestampMixin, db.Model):
    __tablename__ = "labor_cases"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    case_number = db.Column(db.String(80), unique=True, index=True)
    framework = db.Column(db.String(80), nullable=False)
    case_type = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    filed_date = db.Column(db.Date)
    hearing_date = db.Column(db.Date)
    response_deadline = db.Column(db.Date)
    union_name = db.Column(db.String(150))
    representative_name = db.Column(db.String(150))
    employer_representative = db.Column(db.String(150))
    status = db.Column(db.String(50), default="Open", nullable=False)
    resolution = db.Column(db.Text)
    resolution_date = db.Column(db.Date)
    legal_risk_level = db.Column(db.String(50))
    file_path = db.Column(db.String(255))
    notes = db.Column(db.Text)


# =========================================================
# ATS MODULE
# =========================================================

class JobOpening(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "job_openings"

    id = db.Column(db.Integer, primary_key=True)
    requisition_number = db.Column(db.String(80), unique=True, index=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    hiring_manager = db.Column(db.String(150))
    location = db.Column(db.String(150))
    employment_type = db.Column(db.String(80))
    salary_min = db.Column(db.Float, default=0)
    salary_max = db.Column(db.Float, default=0)
    currency = db.Column(db.String(10), default="USD")
    openings_count = db.Column(db.Integer, default=1)
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    status = db.Column(db.String(50), default="Open", nullable=False)
    posting_date = db.Column(db.Date)
    closing_date = db.Column(db.Date)
    source_channel = db.Column(db.String(120))
    notes = db.Column(db.Text)

    candidates = db.relationship("Candidate", backref="job_opening", lazy=True)
    interviews = db.relationship("Interview", backref="job_opening", lazy=True)
    offers = db.relationship("OfferLetter", backref="job_opening", lazy=True)


class Candidate(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "candidates"

    id = db.Column(db.Integer, primary_key=True)
    job_opening_id = db.Column(db.Integer, db.ForeignKey("job_openings.id"))
    candidate_code = db.Column(db.String(80), unique=True, index=True)
    first_name = db.Column(db.String(120), nullable=False)
    middle_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(255), nullable=False, index=True)
    email = db.Column(db.String(150), nullable=False, index=True)
    phone = db.Column(db.String(50))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    country = db.Column(db.String(120))
    linkedin_url = db.Column(db.String(255))
    portfolio_url = db.Column(db.String(255))
    source = db.Column(db.String(120))
    stage = db.Column(db.String(80), default="Applied", nullable=False)
    status = db.Column(db.String(50), default="Active", nullable=False)
    years_experience = db.Column(db.Float, default=0)
    desired_salary = db.Column(db.Float, default=0)
    available_start_date = db.Column(db.Date)
    recruiter_name = db.Column(db.String(150))
    federal_resume_mode = db.Column(db.Boolean, default=False, nullable=False)
    notes = db.Column(db.Text)

    resumes = db.relationship("Resume", backref="candidate", lazy=True, cascade="all, delete-orphan")
    interviews = db.relationship("Interview", backref="candidate", lazy=True)
    evaluations = db.relationship("CandidateEvaluation", backref="candidate", lazy=True)
    offer_letters = db.relationship("OfferLetter", backref="candidate", lazy=True)
    stage_history = db.relationship("CandidateStageHistory", backref="candidate", lazy=True)
    resume_services = db.relationship("ResumeOptimizationRecord", backref="candidate", lazy=True)


class Resume(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    parsed_text = db.Column(db.Text)
    skills = db.Column(db.Text)
    experience_summary = db.Column(db.Text)
    education_summary = db.Column(db.Text)
    ats_score = db.Column(db.Float, default=0)
    keyword_match_score = db.Column(db.Float, default=0)
    version_label = db.Column(db.String(100))
    is_primary = db.Column(db.Boolean, default=True, nullable=False)
    notes = db.Column(db.Text)


class ResumeOptimizationRecord(TimestampMixin, db.Model):
    __tablename__ = "resume_optimization_records"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False)
    target_role = db.Column(db.String(255))
    target_industry = db.Column(db.String(120))
    job_description_text = db.Column(db.Text)
    original_resume_path = db.Column(db.String(255))
    optimized_resume_path = db.Column(db.String(255))
    optimization_type = db.Column(db.String(120))
    ats_score_before = db.Column(db.Float, default=0)
    ats_score_after = db.Column(db.Float, default=0)
    match_score = db.Column(db.Float, default=0)
    recommendations = db.Column(db.Text)
    notes = db.Column(db.Text)


class Interview(TimestampMixin, db.Model):
    __tablename__ = "interviews"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False)
    job_opening_id = db.Column(db.Integer, db.ForeignKey("job_openings.id"), nullable=False)
    interview_type = db.Column(db.String(80))
    interview_round = db.Column(db.String(80))
    scheduled_at = db.Column(db.DateTime, nullable=False)
    interviewer_name = db.Column(db.String(150))
    location_or_link = db.Column(db.String(255))
    status = db.Column(db.String(50), default="Scheduled", nullable=False)
    feedback = db.Column(db.Text)
    score = db.Column(db.Float, default=0)


class CandidateEvaluation(TimestampMixin, db.Model):
    __tablename__ = "candidate_evaluations"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False)
    evaluator_name = db.Column(db.String(150))
    evaluation_type = db.Column(db.String(80))
    score = db.Column(db.Float, default=0)
    strengths = db.Column(db.Text)
    concerns = db.Column(db.Text)
    recommendation = db.Column(db.String(80))
    notes = db.Column(db.Text)


class CandidateStageHistory(TimestampMixin, db.Model):
    __tablename__ = "candidate_stage_history"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False)
    old_stage = db.Column(db.String(80))
    new_stage = db.Column(db.String(80), nullable=False)
    changed_by = db.Column(db.String(150))
    change_reason = db.Column(db.Text)


class OfferLetter(TimestampMixin, db.Model):
    __tablename__ = "offer_letters"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False)
    job_opening_id = db.Column(db.Integer, db.ForeignKey("job_openings.id"), nullable=False)
    offer_date = db.Column(db.Date)
    proposed_start_date = db.Column(db.Date)
    salary_offer = db.Column(db.Float, default=0)
    currency = db.Column(db.String(10), default="USD")
    employment_type = db.Column(db.String(80))
    status = db.Column(db.String(50), default="Draft", nullable=False)
    letter_path = db.Column(db.String(255))
    notes = db.Column(db.Text)


# =========================================================
# ORIENTATION / ONBOARDING
# =========================================================

class OrientationChecklist(TimestampMixin, db.Model):
    __tablename__ = "orientation_checklists"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    checklist_name = db.Column(db.String(255), nullable=False)
    item_name = db.Column(db.String(255), nullable=False)
    module = db.Column(db.String(80))
    responsible_person = db.Column(db.String(150))
    due_date = db.Column(db.Date)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_date = db.Column(db.Date)
    notes = db.Column(db.Text)


class PolicyAcknowledgement(TimestampMixin, db.Model):
    __tablename__ = "policy_acknowledgements"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    policy_name = db.Column(db.String(255), nullable=False)
    policy_version = db.Column(db.String(80))
    acknowledged = db.Column(db.Boolean, default=False, nullable=False)
    acknowledged_date = db.Column(db.Date)
    file_path = db.Column(db.String(255))
    notes = db.Column(db.Text)


# =========================================================
# SG-SST MODULE
# =========================================================

class SafetyPolicy(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "safety_policies"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(80))
    effective_date = db.Column(db.Date)
    review_date = db.Column(db.Date)
    approved_by = db.Column(db.String(150))
    file_path = db.Column(db.String(255))
    description = db.Column(db.Text)


class LegalRequirement(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "legal_requirements"

    id = db.Column(db.Integer, primary_key=True)
    jurisdiction = db.Column(db.String(120), default="Colombia")
    law_name = db.Column(db.String(255), nullable=False)
    article_or_section = db.Column(db.String(120))
    requirement_description = db.Column(db.Text, nullable=False)
    compliance_status = db.Column(db.String(50), default="Pending")
    responsible_person = db.Column(db.String(150))
    review_date = db.Column(db.Date)
    evidence_path = db.Column(db.String(255))
    notes = db.Column(db.Text)


class Hazard(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "hazards"

    id = db.Column(db.Integer, primary_key=True)
    hazard_code = db.Column(db.String(80), unique=True)
    area = db.Column(db.String(150))
    process = db.Column(db.String(150))
    activity = db.Column(db.String(150))
    hazard_type = db.Column(db.String(120))
    description = db.Column(db.Text, nullable=False)
    exposed_population = db.Column(db.String(150))
    existing_controls = db.Column(db.Text)
    probability = db.Column(db.Integer, default=1)
    consequence = db.Column(db.Integer, default=1)
    risk_score = db.Column(db.Integer, default=1)
    risk_level = db.Column(db.String(50))
    control_measures = db.Column(db.Text)
    responsible_person = db.Column(db.String(150))
    next_review_date = db.Column(db.Date)
    status = db.Column(db.String(50), default="Open", nullable=False)

    inspections = db.relationship("Inspection", backref="hazard", lazy=True)
    incidents = db.relationship("Incident", backref="hazard", lazy=True)


class AnnualWorkPlan(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "annual_work_plans"

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    activity = db.Column(db.String(255), nullable=False)
    objective = db.Column(db.Text)
    responsible_person = db.Column(db.String(150))
    due_date = db.Column(db.Date)
    progress_percent = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default="Pending", nullable=False)
    indicator_name = db.Column(db.String(150))
    evidence_path = db.Column(db.String(255))
    notes = db.Column(db.Text)


class SGSSTTraining(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "sgsst_trainings"

    id = db.Column(db.Integer, primary_key=True)
    training_name = db.Column(db.String(255), nullable=False)
    audience = db.Column(db.String(150))
    provider = db.Column(db.String(150))
    training_date = db.Column(db.Date)
    duration_hours = db.Column(db.Float, default=0)
    attendance_count = db.Column(db.Integer, default=0)
    evidence_path = db.Column(db.String(255))
    status = db.Column(db.String(50), default="Scheduled")
    notes = db.Column(db.Text)


class SGSSTTrainingAttendance(TimestampMixin, db.Model):
    __tablename__ = "sgsst_training_attendance"

    id = db.Column(db.Integer, primary_key=True)
    training_id = db.Column(db.Integer, db.ForeignKey("sgsst_trainings.id"), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    attended = db.Column(db.Boolean, default=False, nullable=False)
    score = db.Column(db.Float, default=0)
    certificate_path = db.Column(db.String(255))
    notes = db.Column(db.Text)

    __table_args__ = (
        UniqueConstraint("training_id", "employee_id", name="uq_sgsst_training_employee"),
    )


class MedicalSurveillance(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "medical_surveillance"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    exam_type = db.Column(db.String(80), nullable=False)
    exam_date = db.Column(db.Date)
    provider = db.Column(db.String(150))
    restrictions = db.Column(db.Text)
    fitness_status = db.Column(db.String(80))
    next_exam_date = db.Column(db.Date)
    confidential_notes = db.Column(db.Text)
    file_path = db.Column(db.String(255))


class Incident(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "incidents"

    id = db.Column(db.Integer, primary_key=True)
    incident_code = db.Column(db.String(80), unique=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"))
    hazard_id = db.Column(db.Integer, db.ForeignKey("hazards.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    incident_date = db.Column(db.Date)
    incident_time = db.Column(db.String(20))
    location = db.Column(db.String(255))
    incident_type = db.Column(db.String(120))
    severity = db.Column(db.String(80))
    description = db.Column(db.Text, nullable=False)
    immediate_actions = db.Column(db.Text)
    lost_time = db.Column(db.Boolean, default=False, nullable=False)
    reported_by = db.Column(db.String(150))
    status = db.Column(db.String(50), default="Open", nullable=False)
    evidence_path = db.Column(db.String(255))

    investigations = db.relationship("Investigation", backref="incident", lazy=True)
    corrective_actions = db.relationship("CorrectiveAction", backref="incident", lazy=True)


class Investigation(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "investigations"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=False)
    investigator_name = db.Column(db.String(150))
    methodology = db.Column(db.String(120))
    root_cause = db.Column(db.Text)
    contributing_factors = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    conclusion = db.Column(db.Text)
    closure_date = db.Column(db.Date)
    status = db.Column(db.String(50), default="Open", nullable=False)
    file_path = db.Column(db.String(255))


class Inspection(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "inspections"

    id = db.Column(db.Integer, primary_key=True)
    hazard_id = db.Column(db.Integer, db.ForeignKey("hazards.id"))
    inspection_type = db.Column(db.String(120))
    location = db.Column(db.String(255))
    inspection_date = db.Column(db.Date)
    inspector_name = db.Column(db.String(150))
    checklist_used = db.Column(db.String(150))
    findings = db.Column(db.Text)
    risk_level = db.Column(db.String(50))
    corrective_actions_required = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(50), default="Completed")
    evidence_path = db.Column(db.String(255))


class CorrectiveAction(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "corrective_actions"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"))
    source_type = db.Column(db.String(80))
    source_id = db.Column(db.Integer)
    action_type = db.Column(db.String(80))
    description = db.Column(db.Text, nullable=False)
    responsible_person = db.Column(db.String(150))
    due_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)
    effectiveness_review = db.Column(db.Text)
    status = db.Column(db.String(50), default="Open", nullable=False)
    evidence_path = db.Column(db.String(255))


class PPEAssignment(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "ppe_assignments"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"), nullable=False)
    assignment_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    condition_on_delivery = db.Column(db.String(80))
    signed_receipt = db.Column(db.Boolean, default=False, nullable=False)
    notes = db.Column(db.Text)


class EmergencyPlan(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "emergency_plans"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(80))
    responsible_person = db.Column(db.String(150))
    drill_frequency = db.Column(db.String(80))
    file_path = db.Column(db.String(255))
    notes = db.Column(db.Text)


class EmergencyDrill(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "emergency_drills"

    id = db.Column(db.Integer, primary_key=True)
    emergency_plan_id = db.Column(db.Integer, db.ForeignKey("emergency_plans.id"))
    drill_date = db.Column(db.Date)
    drill_type = db.Column(db.String(120))
    participants_count = db.Column(db.Integer, default=0)
    observations = db.Column(db.Text)
    improvement_actions = db.Column(db.Text)
    status = db.Column(db.String(50), default="Completed")
    evidence_path = db.Column(db.String(255))


class Contractor(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "contractors"

    id = db.Column(db.Integer, primary_key=True)
    contractor_name = db.Column(db.String(255), nullable=False)
    contact_person = db.Column(db.String(150))
    email = db.Column(db.String(150))
    phone = db.Column(db.String(50))
    service_type = db.Column(db.String(150))
    status = db.Column(db.String(50), default="Active")
    notes = db.Column(db.Text)

    compliance_documents = db.relationship("ContractorComplianceDocument", backref="contractor", lazy=True)


class ContractorComplianceDocument(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "contractor_compliance_documents"

    id = db.Column(db.Integer, primary_key=True)
    contractor_id = db.Column(db.Integer, db.ForeignKey("contractors.id"), nullable=False)
    document_name = db.Column(db.String(255), nullable=False)
    document_type = db.Column(db.String(120))
    file_path = db.Column(db.String(255), nullable=False)
    expiration_date = db.Column(db.Date)
    compliance_status = db.Column(db.String(50), default="Pending")
    notes = db.Column(db.Text)


class SafetyAudit(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "safety_audits"

    id = db.Column(db.Integer, primary_key=True)
    audit_name = db.Column(db.String(255), nullable=False)
    audit_type = db.Column(db.String(120))
    audit_date = db.Column(db.Date)
    auditor_name = db.Column(db.String(150))
    scope = db.Column(db.Text)
    findings = db.Column(db.Text)
    score = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default="Open")
    report_path = db.Column(db.String(255))


class ManagementReview(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "management_reviews"

    id = db.Column(db.Integer, primary_key=True)
    review_year = db.Column(db.Integer, nullable=False)
    review_date = db.Column(db.Date)
    attendees = db.Column(db.Text)
    summary = db.Column(db.Text)
    decisions = db.Column(db.Text)
    action_plan = db.Column(db.Text)
    report_path = db.Column(db.String(255))


class MinimumStandardAssessment(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "minimum_standard_assessments"

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    company_size = db.Column(db.String(80))
    standard_name = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Float, default=0)
    compliance_status = db.Column(db.String(50), default="Pending")
    evidence_path = db.Column(db.String(255))
    notes = db.Column(db.Text)


class Committee(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "committees"

    id = db.Column(db.Integer, primary_key=True)
    committee_name = db.Column(db.String(150), nullable=False)
    committee_type = db.Column(db.String(80), nullable=False)  # COPASST / Brigade / Convivencia
    period_start = db.Column(db.Date)
    period_end = db.Column(db.Date)
    status = db.Column(db.String(50), default="Active")
    notes = db.Column(db.Text)

    members = db.relationship("CommitteeMember", backref="committee", lazy=True, cascade="all, delete-orphan")


class CommitteeMember(TimestampMixin, db.Model):
    __tablename__ = "committee_members"

    id = db.Column(db.Integer, primary_key=True)
    committee_id = db.Column(db.Integer, db.ForeignKey("committees.id"), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    role_in_committee = db.Column(db.String(80))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    notes = db.Column(db.Text)

    __table_args__ = (
        UniqueConstraint("committee_id", "employee_id", name="uq_committee_employee"),
    )


# =========================================================
# FINANCE MODULE
# =========================================================

class Account(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    account_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    account_name = db.Column(db.String(255), nullable=False)
    account_type = db.Column(db.String(80), nullable=False)
    parent_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))
    description = db.Column(db.Text)

    parent_account = db.relationship("Account", remote_side=[id], backref="subaccounts", lazy=True)
    journal_lines = db.relationship("JournalLine", backref="account", lazy=True)


class FinancialPeriod(TimestampMixin, db.Model):
    __tablename__ = "financial_periods"

    id = db.Column(db.Integer, primary_key=True)
    period_name = db.Column(db.String(120), nullable=False, unique=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_closed = db.Column(db.Boolean, default=False, nullable=False)
    closed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)


class JournalEntry(TimestampMixin, db.Model):
    __tablename__ = "journal_entries"

    id = db.Column(db.Integer, primary_key=True)
    entry_number = db.Column(db.String(80), unique=True, index=True)
    entry_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    reference = db.Column(db.String(120))
    source_module = db.Column(db.String(80))
    source_id = db.Column(db.Integer)
    status = db.Column(db.String(50), default="Posted", nullable=False)
    financial_period_id = db.Column(db.Integer, db.ForeignKey("financial_periods.id"))
    created_by = db.Column(db.String(150))

    lines = db.relationship("JournalLine", backref="journal_entry", lazy=True, cascade="all, delete-orphan")


class JournalLine(TimestampMixin, db.Model):
    __tablename__ = "journal_lines"

    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey("journal_entries.id"), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    description = db.Column(db.String(255))
    debit = db.Column(db.Float, default=0, nullable=False)
    credit = db.Column(db.Float, default=0, nullable=False)
    cost_center_id = db.Column(db.Integer, db.ForeignKey("cost_centers.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))

    __table_args__ = (
        CheckConstraint("debit >= 0", name="ck_journal_line_debit_nonnegative"),
        CheckConstraint("credit >= 0", name="ck_journal_line_credit_nonnegative"),
    )


class Vendor(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "vendors"

    id = db.Column(db.Integer, primary_key=True)
    vendor_code = db.Column(db.String(80), unique=True, index=True)
    name = db.Column(db.String(255), nullable=False)
    tax_id = db.Column(db.String(120))
    contact_person = db.Column(db.String(150))
    email = db.Column(db.String(150))
    phone = db.Column(db.String(50))
    address = db.Column(db.String(255))
    city = db.Column(db.String(120))
    country = db.Column(db.String(120))
    payment_terms = db.Column(db.String(80))
    status = db.Column(db.String(50), default="Active")
    notes = db.Column(db.Text)

    bills = db.relationship("Bill", backref="vendor", lazy=True)
    purchase_orders = db.relationship("PurchaseOrder", backref="vendor", lazy=True)


class Invoice(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(80), unique=True, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date)
    subtotal = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, default=0, nullable=False)
    amount_paid = db.Column(db.Float, default=0)
    balance_due = db.Column(db.Float, default=0)
    currency = db.Column(db.String(10), default="USD")
    status = db.Column(db.String(50), default="Draft", nullable=False)
    notes = db.Column(db.Text)

    payments = db.relationship("Payment", backref="invoice", lazy=True)
    invoice_lines = db.relationship("InvoiceLine", backref="invoice", lazy=True, cascade="all, delete-orphan")


class InvoiceLine(TimestampMixin, db.Model):
    __tablename__ = "invoice_lines"

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float, default=1)
    unit_price = db.Column(db.Float, default=0)
    line_total = db.Column(db.Float, default=0)
    revenue_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))


class Bill(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "bills"

    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(80), unique=True, index=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey("purchase_orders.id"))
    bill_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date)
    subtotal = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, default=0, nullable=False)
    amount_paid = db.Column(db.Float, default=0)
    balance_due = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default="Open", nullable=False)
    notes = db.Column(db.Text)

    bill_lines = db.relationship("BillLine", backref="bill", lazy=True, cascade="all, delete-orphan")
    payments = db.relationship("Payment", backref="bill", lazy=True)


class BillLine(TimestampMixin, db.Model):
    __tablename__ = "bill_lines"

    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey("bills.id"), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float, default=1)
    unit_cost = db.Column(db.Float, default=0)
    line_total = db.Column(db.Float, default=0)
    expense_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))
    inventory_item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"))


class Payment(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    payment_number = db.Column(db.String(80), unique=True, index=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"))
    bill_id = db.Column(db.Integer, db.ForeignKey("bills.id"))
    payment_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(80))
    bank_account_id = db.Column(db.Integer, db.ForeignKey("bank_accounts.id"))
    reference = db.Column(db.String(120))
    direction = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default="Posted", nullable=False)
    notes = db.Column(db.Text)


class BankAccount(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "bank_accounts"

    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(150), nullable=False)
    bank_name = db.Column(db.String(150))
    account_number = db.Column(db.String(120))
    currency = db.Column(db.String(10), default="USD")
    opening_balance = db.Column(db.Float, default=0)
    current_balance = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default="Active")
    notes = db.Column(db.Text)

    transactions = db.relationship("BankTransaction", backref="bank_account", lazy=True)
    payments = db.relationship("Payment", backref="bank_account", lazy=True)


class BankTransaction(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "bank_transactions"

    id = db.Column(db.Integer, primary_key=True)
    bank_account_id = db.Column(db.Integer, db.ForeignKey("bank_accounts.id"), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    reference = db.Column(db.String(120))
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    reconciled = db.Column(db.Boolean, default=False, nullable=False)
    notes = db.Column(db.Text)


class Reconciliation(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "reconciliations"

    id = db.Column(db.Integer, primary_key=True)
    bank_account_id = db.Column(db.Integer, db.ForeignKey("bank_accounts.id"), nullable=False)
    statement_start_date = db.Column(db.Date)
    statement_end_date = db.Column(db.Date)
    statement_balance = db.Column(db.Float, default=0)
    book_balance = db.Column(db.Float, default=0)
    difference = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default="Draft")
    notes = db.Column(db.Text)


class Budget(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    budget_name = db.Column(db.String(255), nullable=False)
    fiscal_year = db.Column(db.Integer, nullable=False)
    cost_center_id = db.Column(db.Integer, db.ForeignKey("cost_centers.id"))
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))
    amount = db.Column(db.Float, default=0, nullable=False)
    notes = db.Column(db.Text)


class Forecast(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "forecasts"

    id = db.Column(db.Integer, primary_key=True)
    forecast_name = db.Column(db.String(255), nullable=False)
    forecast_period = db.Column(db.String(100))
    module = db.Column(db.String(80))
    projected_revenue = db.Column(db.Float, default=0)
    projected_expense = db.Column(db.Float, default=0)
    projected_profit = db.Column(db.Float, default=0)
    assumptions = db.Column(db.Text)
    notes = db.Column(db.Text)


class RecurringTransaction(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "recurring_transactions"

    id = db.Column(db.Integer, primary_key=True)
    transaction_name = db.Column(db.String(255), nullable=False)
    transaction_type = db.Column(db.String(80), nullable=False)
    frequency = db.Column(db.String(80), nullable=False)
    next_run_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default="Active")
    notes = db.Column(db.Text)


class PurchaseOrder(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "purchase_orders"

    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(80), unique=True, nullable=False, index=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    expected_date = db.Column(db.Date)
    subtotal = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default="Draft", nullable=False)
    approved_by = db.Column(db.String(150))
    notes = db.Column(db.Text)

    lines = db.relationship("PurchaseOrderLine", backref="purchase_order", lazy=True, cascade="all, delete-orphan")
    receipts = db.relationship("GoodsReceipt", backref="purchase_order", lazy=True)


class PurchaseOrderLine(TimestampMixin, db.Model):
    __tablename__ = "purchase_order_lines"

    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey("purchase_orders.id"), nullable=False)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"))
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float, default=0)
    unit_cost = db.Column(db.Float, default=0)
    line_total = db.Column(db.Float, default=0)


class GoodsReceipt(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "goods_receipts"

    id = db.Column(db.Integer, primary_key=True)
    receipt_number = db.Column(db.String(80), unique=True, nullable=False, index=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey("purchase_orders.id"), nullable=False)
    receipt_date = db.Column(db.Date, nullable=False)
    received_by = db.Column(db.String(150))
    status = db.Column(db.String(50), default="Received")
    notes = db.Column(db.Text)

    lines = db.relationship("GoodsReceiptLine", backref="goods_receipt", lazy=True, cascade="all, delete-orphan")


class GoodsReceiptLine(TimestampMixin, db.Model):
    __tablename__ = "goods_receipt_lines"

    id = db.Column(db.Integer, primary_key=True)
    goods_receipt_id = db.Column(db.Integer, db.ForeignKey("goods_receipts.id"), nullable=False)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"), nullable=False)
    quantity_received = db.Column(db.Float, default=0)
    condition_notes = db.Column(db.Text)


class PayrollRecord(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "payroll_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    pay_period_start = db.Column(db.Date, nullable=False)
    pay_period_end = db.Column(db.Date, nullable=False)
    gross_pay = db.Column(db.Float, default=0)
    overtime_pay = db.Column(db.Float, default=0)
    bonus_pay = db.Column(db.Float, default=0)
    deductions_total = db.Column(db.Float, default=0)
    taxes_total = db.Column(db.Float, default=0)
    employer_cost_total = db.Column(db.Float, default=0)
    net_pay = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default="Draft")
    journal_entry_id = db.Column(db.Integer, db.ForeignKey("journal_entries.id"))
    notes = db.Column(db.Text)

    payroll_items = db.relationship("PayrollItem", backref="payroll_record", lazy=True, cascade="all, delete-orphan")


class PayrollItem(TimestampMixin, db.Model):
    __tablename__ = "payroll_items"

    id = db.Column(db.Integer, primary_key=True)
    payroll_record_id = db.Column(db.Integer, db.ForeignKey("payroll_records.id"), nullable=False)
    item_type = db.Column(db.String(80), nullable=False)  # earning / deduction / employer_tax / employee_tax
    item_name = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, default=0)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))
    notes = db.Column(db.Text)


class EmployeeTaxRecord(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "employee_tax_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    jurisdiction = db.Column(db.String(120))
    tax_type = db.Column(db.String(120))
    tax_id_number = db.Column(db.String(120))
    filing_status = db.Column(db.String(80))
    effective_date = db.Column(db.Date)
    notes = db.Column(db.Text)


class TaxRate(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "tax_rates"

    id = db.Column(db.Integer, primary_key=True)
    tax_name = db.Column(db.String(120), nullable=False)
    jurisdiction = db.Column(db.String(120))
    rate_percent = db.Column(db.Float, default=0)
    tax_category = db.Column(db.String(80))  # sales / payroll / withholding / vat
    effective_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    notes = db.Column(db.Text)


# =========================================================
# INVENTORY MODULE
# =========================================================

class InventoryCategory(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "inventory_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text)


class WarehouseLocation(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "warehouse_locations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(50), unique=True)
    address = db.Column(db.String(255))
    city = db.Column(db.String(120))
    country = db.Column(db.String(120))
    notes = db.Column(db.Text)

    inventory_items = db.relationship("InventoryItem", backref="warehouse_location", lazy=True)


class InventoryItem(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "inventory_items"

    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(80), unique=True, index=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey("inventory_categories.id"))
    warehouse_location_id = db.Column(db.Integer, db.ForeignKey("warehouse_locations.id"))
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"))
    sku = db.Column(db.String(120), unique=True)
    serial_number = db.Column(db.String(120))
    barcode = db.Column(db.String(255), unique=True)
    qr_code = db.Column(db.String(255), unique=True)
    unit_of_measure = db.Column(db.String(50), default="Unit")
    quantity_on_hand = db.Column(db.Float, default=0)
    minimum_stock = db.Column(db.Float, default=0)
    maximum_stock = db.Column(db.Float, default=0)
    reorder_point = db.Column(db.Float, default=0)
    unit_cost = db.Column(db.Float, default=0)
    average_cost = db.Column(db.Float, default=0)
    sale_price = db.Column(db.Float, default=0)
    item_type = db.Column(db.String(80), default="Inventory")
    status = db.Column(db.String(50), default="Active")
    image_path = db.Column(db.String(255))
    notes = db.Column(db.Text)

    stock_movements = db.relationship("StockMovement", backref="inventory_item", lazy=True)
    asset_assignments = db.relationship("AssetAssignment", backref="inventory_item", lazy=True)
    ppe_assignments = db.relationship("PPEAssignment", backref="inventory_item", lazy=True)
    maintenance_logs = db.relationship("MaintenanceLog", backref="inventory_item", lazy=True)


class StockMovement(TimestampMixin, db.Model):
    __tablename__ = "stock_movements"

    id = db.Column(db.Integer, primary_key=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"), nullable=False)
    movement_type = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    movement_date = db.Column(db.Date, nullable=False, default=date.today)
    from_location_id = db.Column(db.Integer, db.ForeignKey("warehouse_locations.id"))
    to_location_id = db.Column(db.Integer, db.ForeignKey("warehouse_locations.id"))
    reference_type = db.Column(db.String(80))
    reference_id = db.Column(db.Integer)
    scanned_code = db.Column(db.String(255))
    performed_by = db.Column(db.String(150))
    notes = db.Column(db.Text)


class AssetAssignment(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "asset_assignments"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"), nullable=False)
    assigned_date = db.Column(db.Date, nullable=False)
    expected_return_date = db.Column(db.Date)
    actual_return_date = db.Column(db.Date)
    assignment_status = db.Column(db.String(50), default="Assigned", nullable=False)
    condition_on_issue = db.Column(db.String(80))
    condition_on_return = db.Column(db.String(80))
    signed_receipt = db.Column(db.Boolean, default=False, nullable=False)
    notes = db.Column(db.Text)


class MaintenanceLog(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "maintenance_logs"

    id = db.Column(db.Integer, primary_key=True)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"), nullable=False)
    maintenance_type = db.Column(db.String(120))
    maintenance_date = db.Column(db.Date)
    provider = db.Column(db.String(150))
    cost = db.Column(db.Float, default=0)
    findings = db.Column(db.Text)
    next_due_date = db.Column(db.Date)
    status = db.Column(db.String(50), default="Completed")
    notes = db.Column(db.Text)


# =========================================================
# MARKETING MODULE
# =========================================================

class Campaign(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    campaign_code = db.Column(db.String(80), unique=True, index=True)
    name = db.Column(db.String(255), nullable=False)
    channel = db.Column(db.String(120))
    objective = db.Column(db.String(255))
    target_audience = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Float, default=0)
    actual_spend = db.Column(db.Float, default=0)
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    leads_generated = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)
    revenue_generated = db.Column(db.Float, default=0)
    roi = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default="Draft")
    notes = db.Column(db.Text)

    content_assets = db.relationship("ContentAsset", backref="campaign", lazy=True)
    lead_conversions = db.relationship("LeadConversion", backref="campaign", lazy=True)


class ContentAsset(TimestampMixin, SoftDeleteMixin, db.Model):
    __tablename__ = "content_assets"

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"))
    asset_name = db.Column(db.String(255), nullable=False)
    asset_type = db.Column(db.String(120))
    platform = db.Column(db.String(120))
    file_path = db.Column(db.String(255))
    publish_date = db.Column(db.Date)
    status = db.Column(db.String(50), default="Draft")
    notes = db.Column(db.Text)


class LeadConversion(TimestampMixin, db.Model):
    __tablename__ = "lead_conversions"

    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey("leads.id"), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"))
    conversion_status = db.Column(db.String(80), default="Open")
    conversion_date = db.Column(db.Date)
    revenue_amount = db.Column(db.Float, default=0)
    notes = db.Column(db.Text)


# =========================================================
# REPORTS / ANALYTICS
# =========================================================

class KPIRecord(TimestampMixin, db.Model):
    __tablename__ = "kpi_records"

    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String(80), nullable=False)
    kpi_name = db.Column(db.String(255), nullable=False)
    kpi_value = db.Column(db.Float, default=0)
    kpi_date = db.Column(db.Date, nullable=False, default=date.today)
    unit = db.Column(db.String(50))
    notes = db.Column(db.Text)


class AnalyticsSnapshot(TimestampMixin, db.Model):
    __tablename__ = "analytics_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String(80), nullable=False)
    snapshot_name = db.Column(db.String(255), nullable=False)
    period_label = db.Column(db.String(120))
    json_data = db.Column(db.Text)
    summary = db.Column(db.Text)


class ReportRequest(TimestampMixin, db.Model):
    __tablename__ = "report_requests"

    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String(80), nullable=False)
    report_name = db.Column(db.String(255), nullable=False)
    filters_json = db.Column(db.Text)
    requested_by = db.Column(db.String(150))
    status = db.Column(db.String(50), default="Pending")
    generated_file_path = db.Column(db.String(255))
    notes = db.Column(db.Text)


class ExportLog(TimestampMixin, db.Model):
    __tablename__ = "export_logs"

    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String(80), nullable=False)
    export_type = db.Column(db.String(50), nullable=False)
    record_count = db.Column(db.Integer, default=0)
    generated_by = db.Column(db.String(150))
    file_path = db.Column(db.String(255))
    notes = db.Column(db.Text)