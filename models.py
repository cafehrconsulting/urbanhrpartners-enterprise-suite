from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# =========================================================
# CLIENTS
# =========================================================

class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(120))
    region = db.Column(db.String(120))
    risk_level = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# FINANCE
# =========================================================

class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(100))
    client_name = db.Column(db.String(200))
    amount = db.Column(db.Float)
    status = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    account_type = db.Column(db.String(100))
    balance = db.Column(db.Float, default=0)


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
    allocated_amount = db.Column(db.Float)
    spent_amount = db.Column(db.Float)
    year = db.Column(db.Integer)


class Vendor(db.Model):
    __tablename__ = "vendors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))


class Payable(db.Model):
    __tablename__ = "payables"

    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(200))
    amount = db.Column(db.Float)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(100))


# =========================================================
# HRIS
# =========================================================

class EmployeeProfile(db.Model):
    __tablename__ = "employee_profiles"

    id = db.Column(db.Integer, primary_key=True)
    employee_number = db.Column(db.String(100))
    name = db.Column(db.String(200))
    department = db.Column(db.String(150))
    role = db.Column(db.String(150))
    status = db.Column(db.String(100))
    hire_date = db.Column(db.Date)
    email = db.Column(db.String(200))
    phone = db.Column(db.String(100))
    salary = db.Column(db.Float)
    manager = db.Column(db.String(200))
    location = db.Column(db.String(200))
    employment_type = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class DisciplinaryRecord(db.Model):
    __tablename__ = "disciplinary_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(200))
    violation_type = db.Column(db.String(200))
    description = db.Column(db.Text)
    date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PointLog(db.Model):
    __tablename__ = "point_logs"

    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(200))
    points = db.Column(db.Integer)
    reason = db.Column(db.Text)
    date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SOPRequirement(db.Model):
    __tablename__ = "sop_requirements"

    id = db.Column(db.Integer, primary_key=True)
    job_role = db.Column(db.String(200))
    sop_name = db.Column(db.String(200))
    description = db.Column(db.Text)
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


class TrainingRecord(db.Model):
    __tablename__ = "training_records"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    training_type = db.Column(db.String(200))
    training_date = db.Column(db.Date)
    facilitator = db.Column(db.String(200))
    attendance_count = db.Column(db.Integer)
    status = db.Column(db.String(100))
    notes = db.Column(db.Text)


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


class ImprovementPlan(db.Model):
    __tablename__ = "improvement_plans"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    owner = db.Column(db.String(200))
    due_date = db.Column(db.Date)
    status = db.Column(db.String(100))


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

class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    date = db.Column(db.Date)
    description = db.Column(db.Text)


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
    employee_name = db.Column(db.String(200))
    task = db.Column(db.String(300))
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AssetAssignment(db.Model):
    __tablename__ = "asset_assignments"

    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(200))
    asset_name = db.Column(db.String(200))
    asset_barcode = db.Column(db.String(200))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)


class PolicyAcknowledgement(db.Model):
    __tablename__ = "policy_acknowledgements"

    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(200))
    policy_name = db.Column(db.String(200))
    acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_at = db.Column(db.DateTime)