from datetime import datetime

from xiomy.core.reasoning_engine import ReasoningEngine
from xiomy.core.memory_engine import MemoryEngine
from xiomy.core.conversation_engine import ConversationEngine


class XiomyBrain:

    def __init__(self):
        self.name = "XIOMY"
        self.version = "1.0"
        self.status = "active"
        self.started = datetime.utcnow()

        self.reasoning = ReasoningEngine()
        self.memory = MemoryEngine()
        self.conversation = ConversationEngine()

    def system_status(self):
        uptime = datetime.utcnow() - self.started

        return {
            "ai_name": self.name,
            "version": self.version,
            "status": self.status,
            "uptime_seconds": int(uptime.total_seconds())
        }

    def greeting(self):
        hour = datetime.now().hour

        if hour < 12:
            return "Good morning Juan Carlos. XIOMY systems are operational."
        elif hour < 18:
            return "Good afternoon Juan Carlos. XIOMY is ready."
        else:
            return "Good evening Juan Carlos. All systems are running."

    def process_message(self, message):
        self.memory.store_message("user", message)

        intent = self.reasoning.detect_intent(message)
        response = self.conversation.generate_response(intent, message)

        self.memory.store_message("xiomy", response)

        return response