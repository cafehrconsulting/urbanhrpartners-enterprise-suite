from datetime import datetime
import random


class XiomyAI:

    def __init__(self, db):
        self.db = db
        self.name = "XIOMY"
        self.version = "2.0"
        self.status = "online"
        self.created = datetime.utcnow()

    # --------------------------------------------------
    # SYSTEM STATUS
    # --------------------------------------------------

    def system_status(self):

        return {
            "ai_name": self.name,
            "version": self.version,
            "status": self.status,
            "created": self.created.isoformat()
        }

    # --------------------------------------------------
    # GREETING
    # --------------------------------------------------

    def greeting(self):

        hour = datetime.now().hour

        if hour < 12:
            return "Good morning. I am XIOMY, your UrbanHRPartners executive AI."
        elif hour < 18:
            return "Good afternoon. XIOMY online and monitoring your enterprise systems."
        else:
            return "Good evening. XIOMY active and ready to assist."

    # --------------------------------------------------
    # MODULE MONITOR
    # --------------------------------------------------

    def system_overview(self):

        modules = [
            "CRM",
            "HRIS",
            "ATS",
            "Orientation",
            "SG-SST",
            "Finance",
            "Inventory",
            "Analytics"
        ]

        status = {}

        for module in modules:
            status[module] = random.choice(["Operational", "Monitoring", "Optimizing"])

        return status

    # --------------------------------------------------
    # BUSINESS INSIGHTS
    # --------------------------------------------------

    def generate_insight(self):

        insights = [
            "Employee engagement indicators suggest reviewing training schedules.",
            "Recruitment pipeline shows strong candidate flow.",
            "Compliance monitoring indicates SG-SST documentation review recommended.",
            "CRM revenue trends indicate potential expansion opportunities."
        ]

        return random.choice(insights)

    # --------------------------------------------------
    # TASK CREATION
    # --------------------------------------------------

    def create_task(self, title, description):

        task = {
            "title": title,
            "description": description,
            "created": datetime.utcnow().isoformat(),
            "status": "pending"
        }

        return task

    # --------------------------------------------------
    # CONVERSATION ENGINE
    # --------------------------------------------------

    def respond(self, message):

        message = message.lower()

        if "hello" in message:
            return self.greeting()

        if "status" in message:
            return self.system_overview()

        if "insight" in message:
            return self.generate_insight()

        if "modules" in message:
            return self.system_overview()

        return "I am analyzing your request. Please refine your command."