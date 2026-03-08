import datetime
import random

class XiomyAI:

    def __init__(self):
        self.name = "XIOMY"
        self.version = "1.0"
        self.status = "active"

    # ------------------------------------------------
    # Greeting system
    # ------------------------------------------------

    def greet(self, user="Juan Carlos Urbano"):
        hour = datetime.datetime.now().hour

        if hour < 12:
            period = "Good morning"
        elif hour < 18:
            period = "Good afternoon"
        else:
            period = "Good evening"

        return f"{period} {user}. I am XIOMY, your executive AI assistant. How can I assist you today?"

    # ------------------------------------------------
    # System Status
    # ------------------------------------------------

    def system_status(self):

        modules = {
            "CRM": "online",
            "HRIS": "online",
            "ATS": "online",
            "Orientation": "online",
            "SGSST": "online",
            "Finance": "online",
            "Inventory": "online",
            "Analytics": "online"
        }

        return modules

    # ------------------------------------------------
    # Task suggestion engine
    # ------------------------------------------------

    def recommend_tasks(self):

        suggestions = [
            "Review new CRM leads",
            "Check employee performance analytics",
            "Verify ATS candidate pipeline",
            "Review SG-SST compliance reports",
            "Analyze financial revenue projections",
            "Audit employee orientation completion"
        ]

        return random.choice(suggestions)

    # ------------------------------------------------
    # CRM Insights
    # ------------------------------------------------

    def crm_insight(self, client_count):

        if client_count < 10:
            return "Client acquisition should be prioritized."

        if client_count < 50:
            return "Client growth is stable. Consider marketing expansion."

        return "Client portfolio is strong. Focus on retention."

    # ------------------------------------------------
    # HRIS Insights
    # ------------------------------------------------

    def workforce_insight(self, employee_count):

        if employee_count == 0:
            return "No employees registered in HRIS."

        if employee_count < 10:
            return "Workforce is small. Recruitment may be required."

        return "Workforce capacity is sufficient."

    # ------------------------------------------------
    # Decision engine
    # ------------------------------------------------

    def analyze_request(self, request):

        request = request.lower()

        if "crm" in request:
            return "Opening CRM module."

        if "employees" in request:
            return "Opening HRIS employee records."

        if "candidates" in request:
            return "Opening ATS candidate pipeline."

        if "finance" in request:
            return "Opening financial analytics."

        if "inventory" in request:
            return "Opening inventory system."

        return "Processing request."