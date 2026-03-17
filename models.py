# =========================================================
# models.py - UrbanHRPartners Enterprise Suite
# CLEAN VERSION - STABLE / RUNNING
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
# CLIENTS (CRM CORE)
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


# =========================================================
# COMMUNICATION LOGS
# =========================================================
class CommunicationLog(db.Model):
    __tablename__ = "communication_logs"

    id = db.Column(db.Integer, primary_key=True)

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))

    subject = db.Column(db.String(255))
    message = db.Column(db.Text)

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
    budget = db.Column(db.Float, default=0)

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
    quantity = db.Column(db.Float, default=0)
    unit_cost = db.Column(db.Float, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# FINANCE
# =========================================================
class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)

    invoice_number = db.Column(db.String(100))
    amount = db.Column(db.Float, default=0)
    status = db.Column(db.String(100), default="Pending")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# HRIS
# =========================================================
class EmployeeProfile(db.Model):
    __tablename__ = "employee_profiles"

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))

    email = db.Column(db.String(200))
    role = db.Column(db.String(150))

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
    status = db.Column(db.String(100), default="New")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
