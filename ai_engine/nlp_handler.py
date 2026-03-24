import os
import json
import asyncio
import socket
from google import genai
from google.genai import types
from core.event_bus import EventBus
from core.logger import arya_logger
from ai_engine.intent_classifier import IntentClassifier
from ai_engine.context_manager import ContextManager
from ai_engine.sarcasm_detector import SarcasmDetector
from ai_engine.reasoning_engine import ReasoningEngine

class NLPHandler:
    def __init__(self, event_bus: EventBus, context_manager: ContextManager, 
                 intent_classifier: IntentClassifier, sarcasm_detector: SarcasmDetector,
                 reasoning_engine: ReasoningEngine):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.context_manager = context_manager
        self.intent_classifier = intent_classifier
        self.sarcasm_detector = sarcasm_detector
        self.reasoning_engine = reasoning_engine
        
        # Initialize Gemini API
        api_key = self._load_api_key()
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-3.1-pro-preview'
        
        self.event_bus.subscribe("VOICE_INPUT", self.process_input)
        self.event_bus.subscribe("api_keys_updated", self._update_api_keys)
        self.logger.info("NLP Handler initialized. Ready for offline or online duty, Sir.")

    def _load_api_key(self):
        import json
        import os
        try:
            with open("core/data/secrets.json", "r") as f:
                secrets = json.load(f)
                return secrets.get("gemini", os.environ.get("GEMINI_API_KEY", "AIzaSyABSqyqE4nKyKXZEHnToemhP-C6T1a9was"))
        except FileNotFoundError:
            return os.environ.get("GEMINI_API_KEY", "AIzaSyABSqyqE4nKyKXZEHnToemhP-C6T1a9was")

    async def _update_api_keys(self, payload: dict):
        gemini_key = payload.get("gemini")
        if gemini_key:
            self.client = genai.Client(api_key=gemini_key)
            self.logger.info("Gemini API Key updated in NLP Handler.")

    def _is_online(self):
        """Checks if the device has internet connectivity."""
        try:
            # Try to connect to Google's public DNS
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    async def _offline_fallback(self, user_text: str):
        """Simple rule-based intent classification for offline mode."""
        text = user_text.lower()
        intent = "unknown"
        entities = {}
        response = "I'm currently offline, Sir. My cognitive abilities are somewhat limited without the cloud."

        if "wifi" in text:
            if "on" in text or "enable" in text:
                intent = "turn_on_wifi"
                response = "Activating WiFi locally, Sir."
            elif "off" in text or "disable" in text:
                intent = "turn_off_wifi"
                response = "Disabling WiFi as requested."
        elif "bluetooth" in text:
            if "on" in text or "enable" in text:
                intent = "turn_on_bluetooth"
                response = "Bluetooth is coming online, Sir."
            elif "off" in text or "disable" in text:
                intent = "turn_off_bluetooth"
                response = "Shutting down Bluetooth."
        elif "data" in text or "mobile data" in text:
            if "on" in text or "enable" in text:
                intent = "turn_on_data"
                response = "I'll try to bring the mobile data back online, Sir."
            elif "off" in text or "disable" in text:
                intent = "turn_off_data"
                response = "Cutting the data link now."
        elif "flashlight" in text or "torch" in text:
            if "on" in text:
                intent = "turn_on_flashlight"
                response = "Let there be light, Sir."
            elif "off" in text:
                intent = "turn_off_flashlight"
                response = "Back to the shadows."
        elif "brightness" in text:
            intent = "set_brightness"
            response = "Adjusting the display glow."
        elif "volume" in text:
            intent = "set_volume"
            response = "Modulating the audio output."
        
        return {
            "intent": intent,
            "entities": entities,
            "sarcastic_response": response
        }

    async def process_input(self, data: dict):
        user_text = data.get("text", "")
        if not user_text:
            return

        self.logger.info(f"Analyzing input: '{user_text}'")
        self.context_manager.add_context("user", user_text)

        # 1. Check connectivity
        online = await asyncio.to_thread(self._is_online)
        
        # 2. Determine if we need internet for this command
        # (Simple heuristic: web search, news, weather, etc. need internet)
        needs_internet = any(word in user_text.lower() for word in ["search", "news", "weather", "stock", "wikipedia", "download", "who is", "what is"])

        if not online and needs_internet:
            self.logger.info("Command requires internet but device is offline. Attempting to enable data.")
            await self.event_bus.publish("speak", {"text": "That requires an internet connection, Sir. Attempting to activate mobile data now."})
            await self.event_bus.publish("controller.data.on", {})
            # Wait a bit for data to connect
            await asyncio.sleep(5)
            online = await asyncio.to_thread(self._is_online)

        if not online:
            self.logger.warning("Device is offline. Using local fallback.")
            parsed_result = await self._offline_fallback(user_text)
            reasoning_data = {"is_conditional": False, "offline": True}
        else:
            # 1. Pre-process for conditional logic
            reasoning_data = self.reasoning_engine.evaluate_conditions(user_text)
            
            # 2. Build the comprehensive prompt
            prompt = self._build_prompt(user_text, reasoning_data)
            
            try:
                # 3. Run the Gemini API call
                def _call_gemini():
                    return self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        )
                    )

                response = await asyncio.to_thread(_call_gemini)
                result_text = response.text
                parsed_result = json.loads(result_text)
            except Exception as e:
                self.logger.error(f"Online NLP failed: {e}. Falling back to local.")
                parsed_result = await self._offline_fallback(user_text)

        # 4. Extract results
        intent = parsed_result.get("intent", "unknown")
        entities = parsed_result.get("entities", {})
        sarcastic_response = parsed_result.get("sarcastic_response", "Very well, Sir.")
        
        self.logger.debug(f"NLP Result: {parsed_result}")
        
        # 5. Update context
        self.context_manager.add_context("arya", sarcastic_response)
        
        # 6. Speak the response
        await self.event_bus.publish("speak", {"text": sarcastic_response})
        
        # 7. Route the intent
        await self.event_bus.publish("intent_analyzed", {
            "intent": intent,
            "parameters": entities,
            "reasoning": reasoning_data
        })

    def _build_prompt(self, user_text: str, reasoning_data: dict) -> str:
        context_str = self.context_manager.get_context_string()
        intent_rules = self.intent_classifier.get_intent_prompt_fragment()
        sarcasm_rules = self.sarcasm_detector.get_personality_prompt_fragment()
        
        logic_str = f"Conditional Logic Detected: {reasoning_data}" if reasoning_data['is_conditional'] else ""
        
        return f"""
        You are the brain of ARYA_OS.
        
        Recent Context:
        {context_str}
        
        Current Command: "{user_text}"
        {logic_str}
        
        {intent_rules}
        
        {sarcasm_rules}
        
        Extract any relevant entities (e.g., app_name, time, location, search_query) into an 'entities' dictionary.
        
        Output MUST be a valid JSON object with EXACTLY these keys:
        {{
            "intent": "string",
            "entities": {{"key": "value"}},
            "sarcastic_response": "string"
        }}
        Do not include any markdown formatting or text outside the JSON object.
        """
