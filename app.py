import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'urban_hr_master_suite_2026'

# --- 1. DATABASE CONFIGURATION (RENDER + LOCAL) ---
if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urbanhr.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- 2. CUMULATIVE DATABASE MODELS ---

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    source = db.Column(db.String(50)) 
    budget = db.Column(db.Float, default=0.0)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50))
    points = db.Column(db.Integer, default=100)
    status = db.Column(db.String(20), default='Active')

class Risk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hazard = db.Column(db.String(200), nullable=False)
    level = db.Column(db.String(20)) # High, Medium, Low
    resolved = db.Column(db.Boolean, default=False)

# --- 3. ALL ROUTES (CUMULATIVE) ---

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# CRM Logic
@app.route('/crm')
def crm():
    clients = Client.query.all()
    return render_template('crm.html', clients=clients)

@app.route('/add_client', methods=['POST'])
def add_client():
    name = request.form.get('name')
    source = request.form.get('source')
    budget = float(request.form.get('budget') or 0)
    db.session.add(Client(name=name, source=source, budget=budget))
    db.session.commit()
    return redirect(url_for('crm'))

# HRIS Logic
@app.route('/hris')
def hris():
    employees = Employee.query.all()
    return render_template('hris.html', employees=employees)

# SGSST Logic
@app.route('/sgsst')
def sgsst():
    risks = Risk.query.all()
    return render_template('sgsst.html', risks=risks)

@app.route('/add_risk', methods=['POST'])
def add_risk():
    hazard = request.form.get('hazard')
    level = request.form.get('level')
    db.session.add(Risk(hazard=hazard, level=level))
    db.session.commit()
    return redirect(url_for('sgsst'))

# ATS & Analytics Placeholders
@app.route('/ats')
def ats(): return render_template('ats.html')

@app.route('/analytics')
def analytics(): return render_template('analytics.html')

# --- 4. SYSTEM INITIALIZATION ---
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)