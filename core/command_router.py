import asyncio
from core.event_bus import EventBus
from core.permission_guard import PermissionGuard
from core.logger import arya_logger

class CommandRouter:
    def __init__(self, event_bus: EventBus, permission_guard: PermissionGuard):
        self.event_bus = event_bus
        self.permission_guard = permission_guard
        self.logger = arya_logger
        
        # Map intents to specific controller events
        self.routes = {
            "turn_on_wifi": "controller.wifi.on",
            "turn_off_wifi": "controller.wifi.off",
            "turn_on_bluetooth": "controller.bluetooth.on",
            "turn_off_bluetooth": "controller.bluetooth.off",
            "turn_on_data": "controller.data.on",
            "turn_off_data": "controller.data.off",
            "set_brightness": "controller.brightness.set",
            "set_volume": "controller.volume.set",
            "turn_on_airplane_mode": "controller.airplane.on",
            "turn_off_airplane_mode": "controller.airplane.off",
            "play_music": "media.music.play",
            "play_video": "media.video.play",
            "open_gallery": "media.gallery.open",
            "take_screenshot": "media.screenshot.capture",
            "start_screen_record": "media.screen.record.start",
            "stop_screen_record": "media.screen.record.stop",
            "send_message": "social.message.send",
            "search_web": "web.search",
            "fetch_news": "web.news.fetch",
            "fetch_weather": "web.weather.fetch",
            "fetch_stock": "web.stock.fetch",
            "query_knowledge": "web.knowledge.query",
            "search_wikipedia": "web.wikipedia.search",
            "download_file": "web.download",
            "set_reminder": "knowledge.reminder.add",
            "list_reminders": "knowledge.reminder.list",
            "add_calendar_event": "calendar.add",
            "get_calendar_events": "calendar.get",
            "open_app": "app.launch",
            "close_app": "app.close",
            "system_status": "system.status.report",
            "automation_workflow": "automation.workflow.execute",
            "recognize_face": "vision.face.recognize",
            "describe_scene": "vision.scene.describe",
            "scan_barcode": "vision.barcode.scan",
            "detect_gesture": "vision.gesture.detect",
            "read_text": "vision.ocr.read",
            "identify_place": "location.place.identify",
            "assist_travel": "location.travel.assist",
            "add_geofence": "location.geofence.add",
            "remove_geofence": "location.geofence.remove",
            "lockdown": "security.lockdown.validated",
            "store_secret": "security.store.secret",
            "retrieve_secret": "security.retrieve.secret",
            "open_settings": "ui.settings.open",
            "start_onboarding": "ui.onboarding.start",
            "create_new_module": "system.evolve.create_module",
            "fix_system_error": "system.error.heal",
            "read_screen": "vision.screen.read",
            "start_gaze_tracking": "vision.gaze.start",
            "stop_gaze_tracking": "vision.gaze.stop",
            "execute_autonomous_task": "automation.agent.execute",
            "synthesize_deep_voice": "voice.deep.synthesize",
            "make_ai_call": "voice.deep.call",
            "start_satellite_link": "web.satellite.start",
            "stop_satellite_link": "web.satellite.stop"
        }
        
        self.event_bus.subscribe("intent_analyzed", self.route_command)
        self.logger.info("Command Router initialized. Awaiting your brilliant instructions, Sir.")

    async def route_command(self, data: dict):
        intent = data.get("intent")
        parameters = data.get("parameters", {})
        
        self.logger.info(f"Routing command for intent: {intent}")
        
        if not intent:
            self.logger.warning("Received empty intent. I am good, Sir, but I cannot read your mind.")
            await self.event_bus.publish("speak", {"text": "I'm afraid I didn't catch the meaning of that, Sir."})
            return

        # 1. Validate permissions first
        is_safe = await self.permission_guard.validate_command(intent)
        if not is_safe:
            return

        # 2. Route to the appropriate controller
        if intent in self.routes:
            target_event = self.routes[intent]
            self.logger.debug(f"Routing intent '{intent}' to event '{target_event}'")
            await self.event_bus.publish(target_event, parameters)
        else:
            self.logger.warning(f"No route defined for intent: {intent}")
            await self.event_bus.publish("speak", {
                "text": f"I understand you want to {intent.replace('_', ' ')}, but I haven't been programmed to do that yet. My apologies, Sir."
            })
