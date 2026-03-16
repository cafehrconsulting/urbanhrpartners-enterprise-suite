class ConversationEngine:

    def generate_response(self, intent, message):

        if intent == "crm_request":
            return "Opening CRM intelligence panel."

        if intent == "marketing_analysis":
            return "Analyzing marketing campaigns."

        if intent == "finance_report":
            return "Preparing financial overview."

        if intent == "security_check":
            return "Running system security diagnostics."

        return "I am processing your request."