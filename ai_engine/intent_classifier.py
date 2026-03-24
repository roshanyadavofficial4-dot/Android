from core.logger import arya_logger
from core.event_bus import EventBus

class IntentClassifier:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.logger.info("Intent Classifier initialized. Ready to pigeonhole your requests, Sir.")
        
        # Define the core system intents that the command router understands
        self.valid_intents = [
            "turn_on_wifi", "turn_off_wifi", "turn_on_bluetooth", "turn_off_bluetooth",
            "turn_on_data", "turn_off_data",
            "set_brightness", "set_volume", "turn_on_airplane_mode", "turn_off_airplane_mode",
            "play_music", "play_video", "open_gallery", "take_screenshot",
            "start_screen_record", "stop_screen_record", "send_message", "search_web",
            "fetch_news", "fetch_weather", "fetch_stock", "query_knowledge",
            "search_wikipedia", "download_file", "set_reminder", "list_reminders",
            "add_calendar_event", "get_calendar_events", "open_app", "close_app",
            "system_status", "automation_workflow", "recognize_face", "describe_scene",
            "scan_barcode", "detect_gesture", "read_text", "identify_place",
            "assist_travel", "add_geofence", "remove_geofence", "lockdown",
            "store_secret", "retrieve_secret", "open_settings", "start_onboarding",
            "create_new_module", "fix_system_error", "unknown"
        ]

    def get_intent_prompt_fragment(self) -> str:
        """
        Provides the LLM with the rules for classifying the user's intent.
        """
        return f"""
        Classify the intent of the command into one of the following exact strings:
        {', '.join(self.valid_intents)}
        
        Rules:
        - If it maps to a specific action like turning on WiFi, use 'turn_on_wifi'.
        - If it involves complex conditional logic (e.g., 'If I am at home...'), use 'automation_workflow'.
        - If it does not match any known capability, use 'unknown'.
        """
