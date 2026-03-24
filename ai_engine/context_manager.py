from collections import deque
from core.logger import arya_logger
from core.event_bus import EventBus

class ContextManager:
    def __init__(self, event_bus: EventBus, max_history=10):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.history = deque(maxlen=max_history)
        self.logger.info("Context Manager initialized. I will try to remember what you said 5 minutes ago, Sir.")
        
        self.event_bus.subscribe("context.add", self._handle_add_context)
        self.event_bus.subscribe("context.clear", self._handle_clear_context)

    async def _handle_add_context(self, data: dict):
        role = data.get("role", "system")
        text = data.get("text", "")
        if text:
            self.add_context(role, text)

    async def _handle_clear_context(self, data: dict):
        self.clear_context()

    def add_context(self, role: str, text: str):
        self.history.append({"role": role, "content": text})
        self.logger.debug(f"Context added for {role}: {text[:30]}...")

    def get_context_string(self) -> str:
        if not self.history:
            return "No recent context."
        return "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in self.history])
        
    def clear_context(self):
        self.history.clear()
        self.logger.info("Context cleared. Ignorance is bliss, Sir.")
