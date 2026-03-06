from flask import Flask, render_template

app = Flask(__name__)

# Core routing for the UrbanHR Integrated System
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/crm')
def crm():
    return "<h1>CRM Module: Under Construction</h1>"

@app.route('/ats')
def ats():
    return "<h1>ATS Module: Under Construction</h1>"

@app.route('/ledger')
def ledger():
    return "<h1>Ledger Module: Under Construction</h1>"

@app.route('/risk')
def risk():
    return "<h1>Risk/SGSST Module: Under Construction</h1>"

if __name__ == '__main__':
    app.run(debug=True, port=5000)