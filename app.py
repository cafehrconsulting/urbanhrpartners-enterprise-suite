import os
from flask import Flask, render_template, jsonify
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


class EmployeeProfile(db.Model):
    __tablename__ = "employee_profiles"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)


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
        revenue = db.session.query(
            func.coalesce(func.sum(Project.contract_value), 0)
        ).scalar() or 0
        invoices = db.session.query(
            func.coalesce(func.sum(Invoice.amount), 0)
        ).scalar() or 0

        return jsonify(
            {
                "clients": client_count,
                "employees": employee_count,
                "incidents": incident_count,
                "revenue": float(revenue),
                "invoices": float(invoices),
            }
        )

    @app.route("/crm")
    def crm():
        return render_template("crm.html")

    @app.route("/hris")
    def hris():
        return render_template("hris.html")

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

    @app.route("/sami")
    def sami():
        return render_template("sami.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)