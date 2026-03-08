from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ==============================
# CLIENT MODEL
# ==============================

class Client(db.Model):

    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)

    industry = db.Column(db.String(120))

    region = db.Column(db.String(120))

    risk_level = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)



# ==============================
# EMPLOYEE PROFILE
# ==============================

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



# ==============================
# DISCIPLINARY RECORD
# ==============================

class DisciplinaryRecord(db.Model):

    __tablename__ = "disciplinary_records"

    id = db.Column(db.Integer, primary_key=True)

    employee_name = db.Column(db.String(200))

    violation_type = db.Column(db.String(200))

    description = db.Column(db.Text)

    date = db.Column(db.Date)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)



# ==============================
# PERFORMANCE POINT LOG
# ==============================

class PointLog(db.Model):

    __tablename__ = "point_logs"

    id = db.Column(db.Integer, primary_key=True)

    employee_name = db.Column(db.String(200))

    points = db.Column(db.Integer)

    reason = db.Column(db.Text)

    date = db.Column(db.Date)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)



# ==============================
# SOP REQUIREMENTS
# ==============================

class SOPRequirement(db.Model):

    __tablename__ = "sop_requirements"

    id = db.Column(db.Integer, primary_key=True)

    job_role = db.Column(db.String(200))

    sop_name = db.Column(db.String(200))

    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)



# ==============================
# SG-SST DOCUMENT TRACKING
# ==============================

class SGSSTDocument(db.Model):

    __tablename__ = "sgsst_documents"

    id = db.Column(db.Integer, primary_key=True)

    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))

    folder = db.Column(db.String(200))

    document_name = db.Column(db.String(200))

    file_path = db.Column(db.String(500))

    status = db.Column(db.String(50), default="pending")

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)



# ==============================
# ORIENTATION CHECKLIST
# ==============================

class OrientationChecklist(db.Model):

    __tablename__ = "orientation_checklist"

    id = db.Column(db.Integer, primary_key=True)

    employee_name = db.Column(db.String(200))

    task = db.Column(db.String(300))

    completed = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)



# ==============================
# ASSET ASSIGNMENT
# ==============================

class AssetAssignment(db.Model):

    __tablename__ = "asset_assignments"

    id = db.Column(db.Integer, primary_key=True)

    employee_name = db.Column(db.String(200))

    asset_name = db.Column(db.String(200))

    asset_barcode = db.Column(db.String(200))

    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)



# ==============================
# POLICY ACKNOWLEDGEMENT
# ==============================

class PolicyAcknowledgement(db.Model):

    __tablename__ = "policy_acknowledgements"

    id = db.Column(db.Integer, primary_key=True)

    employee_name = db.Column(db.String(200))

    policy_name = db.Column(db.String(200))

    acknowledged = db.Column(db.Boolean, default=False)

    acknowledged_at = db.Column(db.DateTime)