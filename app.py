import os
from datetime import datetime

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()


def normalize_database_url(raw_url: str) -> str:
    if not raw_url:
        return "sqlite:///urbanhrpartners.db"
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql://", 1)
    return raw_url


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(120), nullable=True)
    region = db.Column(db.String(120), nullable=True)
    risk_level = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class EmployeeProfile(db.Model):
    __tablename__ = "employee_profiles"

    id = db.Column(db.Integer, primary_key=True)
    employee_number = db.Column(db.String(100), nullable=True)
    full_name = db.Column(db.String(200), nullable=False)
    role_title = db.Column(db.String(200), nullable=True)
    department = db.Column(db.String(200), nullable=True)
    employment_status = db.Column(db.String(100), nullable=True)
    hire_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class PointLog(db.Model):
    __tablename__ = "point_logs"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(
        db.Integer, db.ForeignKey("employee_profiles.id"), nullable=False
    )
    points = db.Column(db.Integer, nullable=False, default=0)
    reason = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class DisciplinaryRecord(db.Model):
    __tablename__ = "disciplinary_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(
        db.Integer, db.ForeignKey("employee_profiles.id"), nullable=False
    )
    case_type = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    contract_value = db.Column(db.Float, nullable=False, default=0.0)


class IncidentReport(db.Model):
    __tablename__ = "incident_reports"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=True)


class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False, default=0.0)


class Lead(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    lead_name = db.Column(db.String(200), nullable=False)
    source = db.Column(db.String(120), nullable=True)
    stage = db.Column(db.String(120), nullable=True)
    expected_value = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Campaign(db.Model):
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    campaign_name = db.Column(db.String(200), nullable=False)
    channel = db.Column(db.String(120), nullable=True)
    cost = db.Column(db.Float, nullable=False, default=0.0)
    roi = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class CalendarEvent(db.Model):
    __tablename__ = "calendar_events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    category = db.Column(db.String(120), nullable=True)
    start_at = db.Column(db.DateTime, nullable=False)
    end_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "urbanhrpartners-dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = normalize_database_url(
        os.getenv("DATABASE_URL", "sqlite:///urbanhrpartners.db")
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/api/analytics")
    def analytics():
        client_count = Client.query.count()
        employee_count = EmployeeProfile.query.count()
        incident_count = IncidentReport.query.count()

        revenue = (
            db.session.query(func.coalesce(func.sum(Project.contract_value), 0)).scalar()
            or 0
        )
        invoices = (
            db.session.query(func.coalesce(func.sum(Invoice.amount), 0)).scalar() or 0
        )

        return jsonify(
            {
                "clients": client_count,
                "employees": employee_count,
                "incidents": incident_count,
                "revenue": float(revenue),
                "invoices": float(invoices),
            }
        )

    # ---------------------------
    # CRM
    # ---------------------------

    @app.route("/crm", methods=["GET"])
    def crm():
        clients = Client.query.order_by(Client.id.desc()).all()
        return render_template("crm.html", clients=clients)

    @app.route("/crm/create", methods=["POST"])
    def create_client():
        name = (request.form.get("name") or "").strip()
        industry = (request.form.get("industry") or "").strip()
        region = (request.form.get("region") or "").strip()
        risk_level = (request.form.get("risk_level") or "").strip()

        if not name:
            flash("Client name is required.", "error")
            return redirect(url_for("crm"))

        client = Client(
            name=name,
            industry=industry or None,
            region=region or None,
            risk_level=risk_level or None,
        )

        db.session.add(client)
        db.session.commit()
        flash(f"Client '{name}' created successfully.", "success")
        return redirect(url_for("crm"))

    # ---------------------------
    # HRIS
    # ---------------------------

    @app.route("/hris", methods=["GET"])
    def hris():
        employees = EmployeeProfile.query.order_by(EmployeeProfile.id.desc()).all()

        point_logs = (
            db.session.query(PointLog, EmployeeProfile.full_name)
            .outerjoin(EmployeeProfile, PointLog.employee_id == EmployeeProfile.id)
            .order_by(PointLog.id.desc())
            .limit(20)
            .all()
        )

        disciplinary_records = (
            db.session.query(DisciplinaryRecord, EmployeeProfile.full_name)
            .outerjoin(
                EmployeeProfile,
                DisciplinaryRecord.employee_id == EmployeeProfile.id,
            )
            .order_by(DisciplinaryRecord.id.desc())
            .limit(20)
            .all()
        )

        return render_template(
            "hris.html",
            employees=employees,
            point_logs=point_logs,
            disciplinary_records=disciplinary_records,
        )

    @app.route("/hris/employee/create", methods=["POST"])
    def create_employee():
        employee_number = (request.form.get("employee_number") or "").strip()
        full_name = (request.form.get("full_name") or "").strip()
        role_title = (request.form.get("role_title") or "").strip()
        department = (request.form.get("department") or "").strip()
        employment_status = (request.form.get("employment_status") or "").strip()
        hire_date_raw = (request.form.get("hire_date") or "").strip()

        if not full_name:
            flash("Employee full name is required.", "error")
            return redirect(url_for("hris"))

        hire_date = None
        if hire_date_raw:
            try:
                hire_date = datetime.strptime(hire_date_raw, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid hire date format. Use YYYY-MM-DD.", "error")
                return redirect(url_for("hris"))

        employee = EmployeeProfile(
            employee_number=employee_number or None,
            full_name=full_name,
            role_title=role_title or None,
            department=department or None,
            employment_status=employment_status or None,
            hire_date=hire_date,
        )

        db.session.add(employee)
        db.session.commit()
        flash(f"Employee '{full_name}' created successfully.", "success")
        return redirect(url_for("hris"))

    @app.route("/hris/points/create", methods=["POST"])
    def create_point_log():
        employee_id_raw = (request.form.get("employee_id") or "").strip()
        points_raw = (request.form.get("points") or "0").strip()
        reason = (request.form.get("reason") or "").strip()

        if not employee_id_raw or not reason:
            flash("Employee and reason are required for point log.", "error")
            return redirect(url_for("hris"))

        try:
            employee_id = int(employee_id_raw)
            points = int(points_raw)
        except ValueError:
            flash("Invalid employee or points value.", "error")
            return redirect(url_for("hris"))

        employee = db.session.get(EmployeeProfile, employee_id)
        if not employee:
            flash("Employee not found.", "error")
            return redirect(url_for("hris"))

        point_log = PointLog(
            employee_id=employee_id,
            points=points,
            reason=reason,
        )

        db.session.add(point_log)
        db.session.commit()
        flash("Point log created successfully.", "success")
        return redirect(url_for("hris"))

    @app.route("/hris/disciplinary/create", methods=["POST"])
    def create_disciplinary_record():
        employee_id_raw = (request.form.get("employee_id") or "").strip()
        case_type = (request.form.get("case_type") or "").strip()
        description = (request.form.get("description") or "").strip()
        status = (request.form.get("status") or "").strip()

        if not employee_id_raw or not case_type:
            flash(
                "Employee and case type are required for disciplinary record.",
                "error",
            )
            return redirect(url_for("hris"))

        try:
            employee_id = int(employee_id_raw)
        except ValueError:
            flash("Invalid employee value.", "error")
            return redirect(url_for("hris"))

        employee = db.session.get(EmployeeProfile, employee_id)
        if not employee:
            flash("Employee not found.", "error")
            return redirect(url_for("hris"))

        record = DisciplinaryRecord(
            employee_id=employee_id,
            case_type=case_type,
            description=description or None,
            status=status or None,
        )

        db.session.add(record)
        db.session.commit()
        flash("Disciplinary record created successfully.", "success")
        return redirect(url_for("hris"))

    # ---------------------------
    # MARKETING
    # ---------------------------

    @app.route("/marketing", methods=["GET"])
    def marketing():
        leads = Lead.query.order_by(Lead.id.desc()).all()
        campaigns = Campaign.query.order_by(Campaign.id.desc()).all()
        return render_template("marketing.html", leads=leads, campaigns=campaigns)

    @app.route("/marketing/lead/create", methods=["POST"])
    def create_lead():
        lead_name = (request.form.get("lead_name") or "").strip()
        source = (request.form.get("source") or "").strip()
        stage = (request.form.get("stage") or "").strip()
        expected_value_raw = (request.form.get("expected_value") or "0").strip()

        if not lead_name:
            flash("Lead name is required.", "error")
            return redirect(url_for("marketing"))

        try:
            expected_value = float(expected_value_raw or 0)
        except ValueError:
            expected_value = 0.0

        lead = Lead(
            lead_name=lead_name,
            source=source or None,
            stage=stage or None,
            expected_value=expected_value,
        )

        db.session.add(lead)
        db.session.commit()
        flash(f"Lead '{lead_name}' created successfully.", "success")
        return redirect(url_for("marketing"))

    @app.route("/marketing/campaign/create", methods=["POST"])
    def create_campaign():
        campaign_name = (request.form.get("campaign_name") or "").strip()
        channel = (request.form.get("channel") or "").strip()
        cost_raw = (request.form.get("cost") or "0").strip()
        roi = (request.form.get("roi") or "").strip()

        if not campaign_name:
            flash("Campaign name is required.", "error")
            return redirect(url_for("marketing"))

        try:
            cost = float(cost_raw or 0)
        except ValueError:
            cost = 0.0

        campaign = Campaign(
            campaign_name=campaign_name,
            channel=channel or None,
            cost=cost,
            roi=roi or None,
        )

        db.session.add(campaign)
        db.session.commit()
        flash(f"Campaign '{campaign_name}' created successfully.", "success")
        return redirect(url_for("marketing"))

    # ---------------------------
    # CALENDAR
    # ---------------------------

    @app.route("/calendar", methods=["GET"])
    def calendar():
        events = CalendarEvent.query.order_by(CalendarEvent.start_at.asc()).all()
        return render_template("calendar.html", events=events)

    @app.route("/calendar/create", methods=["POST"])
    def create_calendar_event():
        title = (request.form.get("title") or "").strip()
        location = (request.form.get("location") or "").strip()
        category = (request.form.get("category") or "").strip()
        start_at_raw = (request.form.get("start_at") or "").strip()
        end_at_raw = (request.form.get("end_at") or "").strip()

        if not title or not start_at_raw or not end_at_raw:
            flash("Title, start date, and end date are required.", "error")
            return redirect(url_for("calendar"))

        try:
            start_at = datetime.strptime(start_at_raw, "%Y-%m-%dT%H:%M")
            end_at = datetime.strptime(end_at_raw, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Invalid calendar date format.", "error")
            return redirect(url_for("calendar"))

        if end_at < start_at:
            flash("End date must be after start date.", "error")
            return redirect(url_for("calendar"))

        event = CalendarEvent(
            title=title,
            location=location or None,
            category=category or None,
            start_at=start_at,
            end_at=end_at,
        )

        db.session.add(event)
        db.session.commit()
        flash(f"Calendar event '{title}' created successfully.", "success")
        return redirect(url_for("calendar"))

    # ---------------------------
    # OTHER MODULE PAGES
    # ---------------------------

    @app.route("/ats")
    def ats():
        return render_template("ats.html")

    @app.route("/orientation")
    def orientation():
        return render_template("orientation.html")

    @app.route("/sgsst")
    def sgsst():
        return render_template("sgsst.html")

    @app.route("/inventory")
    def inventory():
        return render_template("inventory.html")

    @app.route("/finance")
    def finance():
        return render_template("finance.html")

    @app.route("/xiomy")
    def xiomy():
        return render_template("xiomy.html")

    @app.route("/sami")
    def sami_redirect():
        return redirect(url_for("xiomy"))

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)