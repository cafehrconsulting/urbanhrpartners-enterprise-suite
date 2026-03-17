from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# =========================================================
# USERS
# =========================================================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(100), default="user")
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# CLIENTS / CRM
# =========================================================
class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)

    # Core identity
    name = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(200))
    contact_person = db.Column(db.String(200))

    # Contact
    email = db.Column(db.String(200))
    phone = db.Column(db.String(100))
    address = db.Column(db.String(300))

    # Global business intelligence
    industry = db.Column(db.String(200))
    country = db.Column(db.String(120), default="Colombia")
    language = db.Column(db.String(100), default="Spanish")
    region = db.Column(db.String(120))

    # Tax / legal identification
    tax_id_type = db.Column(db.String(50))
    tax_id_number = db.Column(db.String(100))

    # Business status
    status = db.Column(db.String(100), default="Prospect")
    risk_level = db.Column(db.String(50))

    # Strategic notes
    needs = db.Column(db.Text)
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    communication_logs = db.relationship("CommunicationLog", backref="client", lazy=True)
    projects = db.relationship("Project", backref="client", lazy=True)
    sgsst_documents = db.relationship("SGSSTDocument", backref="client", lazy=True)


class CommunicationLog(db.Model):
    __tablename__ = "communication_logs"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))
    client_name = db.Column(db.String(200))
    channel = db.Column(db.String(100))
    communication_type = db.Column(db.String(100))
    direction = db.Column(db.String(100))
    contact_person = db.Column(db.String(200))
    subject = db.Column(db.String(255))
    summary = db.Column(db.Text)
    message = db.Column(db.Text)
    action_items = db.Column(db.Text)
    action_required = db.Column(db.Boolean, default=False)
    log_date = db.Column(db.Date)
    follow_up_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))
    client_name = db.Column(db.String(200))
    name = db.Column(db.String(200))
    project_name = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(100), default="Planned")
    estimated_value = db.Column(db.Float, default=0)
    budget = db.Column(db.Float, default=0)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    status = db.Column(db.String(100), default="Open")
    priority = db.Column(db.String(50), default="Normal")
    due_date = db.Column(db.Date)
    client_id = db.Column(db.Integer)
    client_name = db.Column(db.String(200))
    project_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# INVENTORY
# =========================================================
class InventoryItem(db.Model):
    __tablename__ = "inventory_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(100))
    barcode = db.Column(db.String(200))
    category = db.Column(db.String(150))
    quantity = db.Column(db.Float, default=0)
    unit_cost = db.Column(db.Float, default=0)
    reorder_level = db.Column(db.Float, default=0)
    location = db.Column(db.String(200))
    status = db.Column(db.String(100), default="Available")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# FINANCE
# =========================================================
class Finance(db.Model):
    __tablename__ = "finance"

    id = db.Column(db.Integer, primary_key=True)
    entry_type = db.Column(db.String(100))
    category = db.Column(db.String(150))
    description = db.Column(db.String(500))
    amount = db.Column(db.Float, default=0)
    entry_date = db.Column(db.Date)
    status = db.Column(db.String(100), default="Posted")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(100))
    client_name = db.Column(db.String(200))
    project_name = db.Column(db.String(200))
    amount = db.Column(db.Float, default=0)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(100), default="Pending")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    account_type = db.Column(db.String(100))
    balance = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class LedgerEntry(db.Model):
    __tablename__ = "ledger_entries"

    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(200))
    description = db.Column(db.String(500))
    debit = db.Column(db.Float, default=0)
    credit = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(200))
    allocated_amount = db.Column(db.Float, default=0)
    spent_amount = db.Column(db.Float, default=0)
    year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Vendor(db.Model):
    __tablename__ = "vendors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Payable(db.Model):
    __tablename__ = "payables"

    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(200))
    amount = db.Column(db.Float, default=0)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# HRIS
# =========================================================
class EmployeeProfile(db.Model):
    __tablename__ = "employee_profiles"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(100))
    employee_number = db.Column(db.String(100))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    full_name = db.Column(db.String(200))
    name = db.Column(db.String(200))
    department = db.Column(db.String(150))
    role = db.Column(db.String(150))
    position = db.Column(db.String(150))
    status = db.Column(db.String(100))
    hire_date = db.Column(db.Date)
    email = db.Column(db.String(200))
    phone = db.Column(db.String(100))
    salary = db.Column(db.Float, default=0)
    manager = db.Column(db.String(200))
    location = db.Column(db.String(200))
    employment_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class DisciplinaryRecord(db.Model):
    __tablename__ = "disciplinary_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer)
    employee_name = db.Column(db.String(200))
    violation_type = db.Column(db.String(200))
    case_type = db.Column(db.String(200))
    description = db.Column(db.Text)
    action_taken = db.Column(db.Text)
    date = db.Column(db.Date)
    record_date = db.Column(db.Date)
    status = db.Column(db.String(100), default="Open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PointLog(db.Model):
    __tablename__ = "point_logs"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer)
    employee_name = db.Column(db.String(200))
    points = db.Column(db.Integer)
    reason = db.Column(db.Text)
    category = db.Column(db.String(100))
    date = db.Column(db.Date)
    log_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SOPRequirement(db.Model):
    __tablename__ = "sop_requirements"

    id = db.Column(db.Integer, primary_key=True)
    job_role = db.Column(db.String(200))
    job_title = db.Column(db.String(200))
    sop_name = db.Column(db.String(200))
    title = db.Column(db.String(200))
    requirement = db.Column(db.Text)
    description = db.Column(db.Text)
    required = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# ATS
# =========================================================
class Candidate(db.Model):
    __tablename__ = "candidates"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    full_name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(100))
    position_applied = db.Column(db.String(200))
    stage = db.Column(db.String(100), default="Applied")
    status = db.Column(db.String(100), default="New")
    notes = db.Column(db.Text)
    resume_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# SG-SST
# =========================================================
class SafetyPolicy(db.Model):
    __tablename__ = "safety_policies"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    version = db.Column(db.String(50))
    owner = db.Column(db.String(200))
    review_date = db.Column(db.Date)
    statement = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class LegalRequirement(db.Model):
    __tablename__ = "legal_requirements"

    id = db.Column(db.Integer, primary_key=True)
    standard = db.Column(db.String(200))
    reference = db.Column(db.String(200))
    topic = db.Column(db.String(200))
    owner = db.Column(db.String(200))
    status = db.Column(db.String(100))
    review_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RiskMatrixItem(db.Model):
    __tablename__ = "risk_matrix_items"

    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(200))
    hazard = db.Column(db.String(255))
    risk_level = db.Column(db.String(100), default="Medium")
    control_measure = db.Column(db.Text)
    responsible_party = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class InspectionRecord(db.Model):
    __tablename__ = "inspection_records"

    id = db.Column(db.Integer, primary_key=True)
    inspection_name = db.Column(db.String(255))
    area = db.Column(db.String(200))
    inspector = db.Column(db.String(200))
    inspection_date = db.Column(db.Date)
    findings = db.Column(db.Text)
    status = db.Column(db.String(100), default="Open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class IncidentRecord(db.Model):
    __tablename__ = "incident_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer)
    incident_type = db.Column(db.String(200))
    description = db.Column(db.Text)
    incident_date = db.Column(db.Date)
    status = db.Column(db.String(100), default="Open")
    corrective_action = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TrainingRecord(db.Model):
    __tablename__ = "training_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer)
    title = db.Column(db.String(200))
    training_name = db.Column(db.String(200))
    training_type = db.Column(db.String(200))
    training_date = db.Column(db.Date)
    facilitator = db.Column(db.String(200))
    trainer = db.Column(db.String(200))
    attendance_count = db.Column(db.Integer)
    status = db.Column(db.String(100))
    certificate = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Inspection(db.Model):
    __tablename__ = "inspections"

    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(200))
    inspection_type = db.Column(db.String(100))
    inspection_date = db.Column(db.Date)
    status = db.Column(db.String(100))
    owner = db.Column(db.String(200))
    due_date = db.Column(db.Date)
    findings = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PPERecord(db.Model):
    __tablename__ = "ppe_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(200))
    ppe_item = db.Column(db.String(200))
    status = db.Column(db.String(100))
    assignment_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    reference = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuditRecord(db.Model):
    __tablename__ = "audit_records"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    audit_date = db.Column(db.Date)
    scope = db.Column(db.String(200))
    status = db.Column(db.String(100))
    owner = db.Column(db.String(200))
    due_date = db.Column(db.Date)
    findings = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ImprovementPlan(db.Model):
    __tablename__ = "improvement_plans"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    owner = db.Column(db.String(200))
    due_date = db.Column(db.Date)
    status = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SGSSTDocument(db.Model):
    __tablename__ = "sgsst_documents"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))
    folder = db.Column(db.String(200))
    document_name = db.Column(db.String(200))
    file_path = db.Column(db.String(500))
    status = db.Column(db.String(50), default="pending")
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# MARKETING
# =========================================================
class MarketingCampaign(db.Model):
    __tablename__ = "marketing_campaigns"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    channel = db.Column(db.String(200))
    audience = db.Column(db.String(255))
    budget = db.Column(db.Float, default=0)
    status = db.Column(db.String(100), default="Draft")
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Lead(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    source = db.Column(db.String(200))
    status = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# CALENDAR
# =========================================================
class CalendarEvent(db.Model):
    __tablename__ = "calendar_events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(100), default="Scheduled")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    date = db.Column(db.Date)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# ANALYTICS
# =========================================================
class AnalyticsMetric(db.Model):
    __tablename__ = "analytics_metrics"

    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(200))
    metric_value = db.Column(db.Float)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# ORIENTATION
# =========================================================
class OrientationChecklist(db.Model):
    __tablename__ = "orientation_checklist"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer)
    employee_id = db.Column(db.Integer)
    employee_name = db.Column(db.String(200))
    title = db.Column(db.String(255))
    task = db.Column(db.String(300))
    description = db.Column(db.Text)
    status = db.Column(db.String(100), default="Pending")
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AssetAssignment(db.Model):
    __tablename__ = "asset_assignments"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer)
    employee_name = db.Column(db.String(200))
    inventory_item_id = db.Column(db.Integer)
    asset_name = db.Column(db.String(200))
    asset_barcode = db.Column(db.String(200))
    assignment_date = db.Column(db.Date)
    return_due_date = db.Column(db.Date)
    status = db.Column(db.String(100), default="Assigned")
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)


class PolicyAcknowledgement(db.Model):
    __tablename__ = "policy_acknowledgements"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer)
    employee_name = db.Column(db.String(200))
    policy_name = db.Column(db.String(200))
    acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_date = db.Column(db.Date)
    acknowledged_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
