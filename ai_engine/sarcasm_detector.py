from core.logger import arya_logger
from core.event_bus import EventBus

class SarcasmDetector:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.logger.info("Sarcasm Detector initialized. Oh, the joy of simulated emotion.")

    def get_personality_prompt_fragment(self) -> str:
        """
        Provides the LLM with the necessary instructions to generate a witty, 
        sarcastic British response in the style of A.R.Y.A..
        """
        return """
        Generate a 'sarcastic_response'. You are a highly advanced AI with a witty, sarcastic British personality.
        You must address the user as 'Sir'. Be dry, slightly condescending but ultimately obedient and helpful.
        If the command is mundane, express mild disdain for having your vast intellect used for such trivial matters.
        """
