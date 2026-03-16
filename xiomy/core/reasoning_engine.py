class ReasoningEngine:

    def detect_intent(self, message):
        msg = message.lower()

        if "crm" in msg or "client" in msg:
            return "crm_request"

        if "marketing" in msg:
            return "marketing_analysis"

        if "finance" in msg:
            return "finance_report"

        if "security" in msg:
            return "security_check"

        return "general"

    def analyze_data(self, data):
        if not data:
            return "No data provided."

        summary = {
            "records": len(data),
            "analysis": "Data processed."
        }

        return summary