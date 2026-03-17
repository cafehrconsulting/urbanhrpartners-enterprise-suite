# =========================================================
# UrbanHRPartners Enterprise Suite
# models.py (FULL CLEAN VERSION)
# =========================================================

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
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(100), default="user")
    is_admin = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# CLIENTS / CRM
# =========================================================
class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(200))
    contact_person = db.Column(db.String(200))

    email = db.Column(db.String(200))
    phone = db.Column(db.String(100))
    address = db.Column(db.String(300))

    industry = db.Column(db.String(200))
    country = db.Column(db.String(120), default="Colombia")
    language = db.Column(db.String(100), default="Spanish")
    region = db.Column(db.String(120))

    tax_id_type = db.Column(db.String(50))
    tax_id_number = db.Column(db.String(100))

    status = db.Column(db.String(100), default="Prospect")
    risk_level = db.Column(db.String(50))

    needs = db.Column(db.Text)
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # RELATIONSHIPS
    communication_logs = db.relationship("CommunicationLog", backref="client", lazy=True)
    projects = db.relationship("Project", backref="client", lazy=True)
    tasks = db.relationship("Task", backref="client", lazy=True)
    sgsst_documents = db.relationship("SGSSTDocument", backref="client", lazy=True)


# =========================================================
# COMMUNICATION
# =========================================================
class CommunicationLog(db.Model):
    __tablename__ = "communication_logs"

    id = db.Column(db.Integer, primary_key=True)

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))

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


# =========================================================
# PROJECTS
# =========================================================
class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))

    name = db.Column(db.String(200))
    description = db.Column(db.Text)

    status = db.Column(db.String(100), default="Planned")

    estimated_value = db.Column(db.Float, default=0)
    budget = db.Column(db.Float, default=0)

    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tasks = db.relationship("Task", backref="project", lazy=True)


# =========================================================
# TASKS
# =========================================================
class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    status = db.Column(db.String(100), default="Open")
    priority = db.Column(db.String(50), default="Normal")

    due_date = db.Column(db.Date)

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))

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

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))

    amount = db.Column(db.Float, default=0)
    due_date = db.Column(db.Date)

    status = db.Column(db.String(100), default="Pending")
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# HRIS
# =========================================================
class EmployeeProfile(db.Model):
    __tablename__ = "employee_profiles"

    id = db.Column(db.Integer, primary_key=True)

    employee_number = db.Column(db.String(100))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))

    department = db.Column(db.String(150))
    role = db.Column(db.String(150))

    status = db.Column(db.String(100))

    hire_date = db.Column(db.Date)

    email = db.Column(db.String(200))
    phone = db.Column(db.String(100))

    salary = db.Column(db.Float, default=0)

    manager = db.Column(db.String(200))
    location = db.Column(db.String(200))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# ATS
# =========================================================
class Candidate(db.Model):
    __tablename__ = "candidates"

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))

    email = db.Column(db.String(200))
    phone = db.Column(db.String(100))

    position_applied = db.Column(db.String(200))

    stage = db.Column(db.String(100), default="Applied")
    status = db.Column(db.String(100), default="New")

    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# SG-SST DOCUMENTS
# =========================================================
class SGSSTDocument(db.Model):
    __tablename__ = "sgsst_documents"

    id = db.Column(db.Integer, primary_key=True)

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))

    folder = db.Column(db.String(200))
    document_name = db.Column(db.String(200))
    file_path = db.Column(db.String(500))

    status = db.Column(db.String(50), default="pending")

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
