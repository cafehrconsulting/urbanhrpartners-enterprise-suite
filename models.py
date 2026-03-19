# =========================================================
# UrbanHRPartners Enterprise Suite
# models.py
# FULL ENTERPRISE VERSION (PASS 1 + PASS 2 COMPLETE)
# STRUCTURE: CRM + HRIS + ATS + SG-SST + FINANCE + INVENTORY + MARKETING
# =========================================================

from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# =========================================================
# MIXINS
# =========================================================

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class StatusMixin:
    status = db.Column(db.String(100), default="Active", nullable=False, index=True)

class SoftDeleteMixin:
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)

# =========================================================
# USERS
# =========================================================

class User(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(100), nullable=False, default="Admin", index=True)

# =========================================================
# HRIS
# =========================================================

class Department(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)

class Position(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "positions"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)

    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    department = db.relationship("Department", foreign_keys=[department_id])

class EmployeeProfile(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "employee_profiles"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(200))

    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey("positions.id"), nullable=False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"))

    department = db.relationship("Department", foreign_keys=[department_id])
    position = db.relationship("Position", foreign_keys=[position_id])

    supervisor = db.relationship(
        "EmployeeProfile",
        remote_side=[id],
        foreign_keys=[supervisor_id]
    )

# =========================================================
# DISCIPLINARY / LABOR RELATIONS
# =========================================================

class DisciplinaryRecord(db.Model, TimestampMixin, StatusMixin):
    __tablename__ = "disciplinary_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employee_profiles.id"), nullable=False)
    description = db.Column(db.Text, nullable=False)

    employee = db.relationship("EmployeeProfile", foreign_keys=[employee_id])

# =========================================================
# CRM
# =========================================================

class Client(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    legal_name = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(200))
    email = db.Column(db.String(200))

# =========================================================
# TASKS (MULTI USER FIXED)
# =========================================================

class Task(db.Model, TimestampMixin, StatusMixin, SoftDeleteMixin):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)

    assigned_to_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)

    assigned_user = db.relationship("User", foreign_keys=[assigned_to_user_id])
    creator_user = db.relationship("User", foreign_keys=[created_by_user_id])

# =========================================================
# PROJECTS
# =========================================================

class Project(db.Model, TimestampMixin, StatusMixin):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    project_manager_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    client = db.relationship("Client", foreign_keys=[client_id])
    manager = db.relationship("User", foreign_keys=[project_manager_user_id])

# =========================================================
# FINANCE (ENTERPRISE SAFE)
# =========================================================

class Account(db.Model):
    __tablename__ = "accounts"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

class Transaction(db.Model, TimestampMixin):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, default=0.0, nullable=False)

    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    account = db.relationship("Account", foreign_keys=[account_id])

class Invoice(db.Model, TimestampMixin):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)

    total_amount = db.Column(db.Float, default=0.0, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0, nullable=False)
    discount_amount = db.Column(db.Float, default=0.0, nullable=False)

    client = db.relationship("Client", foreign_keys=[client_id])

class Payment(db.Model, TimestampMixin):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=False)

    amount = db.Column(db.Float, default=0.0, nullable=False)

    invoice = db.relationship("Invoice", foreign_keys=[invoice_id])

# =========================================================
# INVENTORY
# =========================================================

class InventoryItem(db.Model, TimestampMixin):
    __tablename__ = "inventory_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    quantity = db.Column(db.Float, default=0.0, nullable=False)
    unit_cost = db.Column(db.Float, default=0.0, nullable=False)

class InventoryMovement(db.Model, TimestampMixin):
    __tablename__ = "inventory_movements"

    id = db.Column(db.Integer, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey("inventory_items.id"), nullable=False)
    quantity_change = db.Column(db.Float, default=0.0, nullable=False)

    item = db.relationship("InventoryItem", foreign_keys=[item_id])

# =========================================================
# ATS
# =========================================================

class Candidate(db.Model, TimestampMixin):
    __tablename__ = "candidates"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)

class JobRequisition(db.Model):
    __tablename__ = "job_requisitions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))

# =========================================================
# SG-SST
# =========================================================

class RiskMatrix(db.Model):
    __tablename__ = "risk_matrix"

    id = db.Column(db.Integer, primary_key=True)
    hazard = db.Column(db.String(255))

class Incident(db.Model):
    __tablename__ = "incidents"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)

# =========================================================
# MARKETING
# =========================================================

class Campaign(db.Model):
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

# =========================================================
# SYSTEM LOGS
# =========================================================

class NotificationLog(db.Model):
    __tablename__ = "notification_logs"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)

# =========================================================
# DB INIT
# =========================================================

def init_db(app):
    with app.app_context():
        db.create_all()
