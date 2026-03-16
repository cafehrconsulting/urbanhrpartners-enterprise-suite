class MemoryEngine:

    def __init__(self):
        self.history = []

    def store_message(self, role, message):
        self.history.append({
            "role": role,
            "message": message
        })

    def retrieve_history(self):
        return self.history