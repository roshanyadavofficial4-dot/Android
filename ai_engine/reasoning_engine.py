import re
from core.logger import arya_logger
from core.event_bus import EventBus

class ReasoningEngine:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.logger.info("Reasoning Engine initialized. I shall attempt to follow your 'logic', Sir.")

    def evaluate_conditions(self, text: str) -> dict:
        """
        Parses complex logic like 'If I am at home, turn on WiFi'.
        Returns a dictionary of conditions and actions.
        """
        self.logger.debug(f"Evaluating conditional logic for: {text}")
        result = {"is_conditional": False, "condition": None, "action": None}
        
        # Simple regex for "If [condition], [action]" or "If [condition] then [action]"
        match = re.search(r'(?i)^if\s+(.*?)(?:,|\s+then)\s+(.*)', text)
        if match:
            result["is_conditional"] = True
            result["condition"] = match.group(1).strip()
            result["action"] = match.group(2).strip()
            self.logger.info(f"Conditional logic detected. Condition: '{result['condition']}', Action: '{result['action']}'")
        else:
            self.logger.debug("No conditional logic detected. A straightforward command for once.")
            
        return result
