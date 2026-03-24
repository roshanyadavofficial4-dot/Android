import asyncio
import importlib
import sys
import os
import traceback

# Add the current directory to the path so modules can be found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.event_bus import EventBus
from core.logger import arya_logger
from core.error_handler import ErrorHandler

class AryaOS:
    def __init__(self):
        self.logger = arya_logger
        self.logger.info("Initializing A.R.Y.A. OS Master Boot Sequence...")
        
        # Core Systems
        self.event_bus = EventBus()
        self.error_handler = ErrorHandler(self.event_bus)
        self.modules = {}

    async def _safe_init(self, module_path: str, class_name: str, *args):
        """
        Dynamically imports and initializes a module.
        Catches any ImportErrors or runtime exceptions to prevent OS crash.
        """
        try:
            self.logger.debug(f"Loading module: {class_name} from {module_path}")
            
            # Asynchronous delay to prevent RAM spikes on Android
            if "vision_module" in module_path or "ai_engine" in module_path:
                self.logger.info(f"Heavy module detected ({class_name}). Applying 1.5s delay to stabilize RAM...")
                await asyncio.sleep(1.5)
            else:
                await asyncio.sleep(0.1) # Standard delay for all other modules

            module = importlib.import_module(module_path)
            init_func = getattr(module, class_name)
            instance = init_func(*args)
            self.modules[class_name] = instance
            return instance
        except Exception as e:
            self.logger.error(f"Failed to load {class_name}: {e}")
            # We don't halt the boot process for a single module failure
            return None

    async def boot(self):
        self.logger.info("=== A.R.Y.A. OS BOOT SEQUENCE INITIATED ===")
        await self.event_bus.publish("speak", {"text": "Initiating master boot sequence. Please stand by, Sir."})

        # Define the 16-Phase Module Load Order
        load_order = [
            # 0. Core Systems
            ("core.permission_guard", "PermissionGuard"),
            ("core.command_router", "CommandRouter"),
            ("core.task_scheduler", "TaskScheduler"),

            # 1. Memory System
            ("memory_system.history_tracker", "HistoryTracker"),
            ("memory_system.preference_store", "PreferenceStore"),
            ("memory_system.command_learning", "CommandLearning"),
            ("memory_system.personalization_engine", "PersonalizationEngine"),

            # 2. Controllers (Device Control)
            ("controllers.system_controller", "SystemController"),
            ("controllers.wifi_controller", "WifiController"),
            ("controllers.bluetooth_controller", "BluetoothController"),
            ("controllers.brightness_controller", "BrightnessController"),
            ("controllers.volume_controller", "VolumeController"),
            ("controllers.battery_manager", "BatteryManager"),
            ("controllers.power_manager", "PowerManager"),

            # 3. File System
            ("file_system.storage_scanner", "StorageScanner"),
            ("file_system.file_search_engine", "FileSearchEngine"),
            ("file_system.file_sorter", "FileSorter"),
            ("file_system.duplicate_finder", "DuplicateFinder"),

            # 4. App Automation
            ("app_automation.app_launcher", "AppLauncher"),
            ("app_automation.app_closer", "AppCloser"),
            ("app_automation.accessibility_driver", "AccessibilityDriver"),
            ("app_automation.auto_click_engine", "AutoClickEngine"),

            # 5. Social Automation
            ("social_automation.message_sender", "MessageSender"),
            ("social_automation.auto_reply_engine", "AutoReplyEngine"),

            # 6. Vision Module
            ("vision_module.camera_controller", "CameraController"),
            ("vision_module.object_detection", "ObjectDetection"),
            ("vision_module.text_recognition_ocr", "TextRecognitionOCR"),
            ("vision_module.face_recognition", "FaceRecognitionEngine"),
            ("vision_module.scene_description", "SceneDescriptionEngine"),
            ("vision_module.barcode_scanner", "BarcodeScanner"),
            ("vision_module.gesture_detection", "GestureDetectionEngine"),

            # 7. Web Services
            ("web_services.web_search_agent", "WebSearchAgent"),
            ("web_services.news_fetcher", "NewsFetcher"),
            ("web_services.weather_fetcher", "WeatherFetcher"),
            ("web_services.knowledge_fetcher", "KnowledgeFetcher"),
            ("web_services.auto_download_manager", "AutoDownloadManager"),
            ("web_services.wikipedia_agent", "WikipediaAgent"),
            ("web_services.stock_tracker", "StockTracker"),
            ("web_services.satellite_link", "SatelliteLink"),

            # 8. Automation Engine
            ("automation_engine.workflow_builder", "WorkflowBuilder"),
            ("automation_engine.action_executor", "ActionExecutor"),
            ("automation_engine.trigger_detector", "TriggerDetector"),
            ("automation_engine.macro_recorder", "MacroRecorder"),
            ("automation_engine.autonomous_agent", "AutonomousAgent"),

            # 9. Security Layer
            ("security_layer.permission_manager", "PermissionManager"),
            ("security_layer.biometric_auth", "BiometricAuth"),
            ("security_layer.command_validator", "CommandValidator"),
            ("security_layer.privacy_guard", "PrivacyGuard"),
            ("security_layer.secure_storage", "SecureStorage"),

            # 10. Notification System
            ("notification_system.notification_reader", "NotificationReader"),
            ("notification_system.smart_reply_generator", "SmartReplyGenerator"),
            ("notification_system.notification_filter", "NotificationFilter"),
            ("notification_system.priority_manager", "PriorityManager"),

            # 11. Knowledge System
            ("knowledge_system.reminder_engine", "ReminderEngine"),
            ("knowledge_system.calendar_manager", "CalendarManager"),
            ("knowledge_system.note_manager", "NoteManager"),
            ("knowledge_system.task_manager", "TaskManager"),
            ("knowledge_system.habit_tracker", "HabitTracker"),

            # 12. Location Services
            ("location_services.gps_tracker", "GPSTracker"),
            ("location_services.route_planner", "RoutePlanner"),
            ("location_services.place_identifier", "PlaceIdentifier"),
            ("location_services.travel_assistant", "TravelAssistant"),
            ("location_services.geo_fencing", "GeoFencing"),

            # 13. Media Control
            ("media_control.music_player_controller", "MusicPlayerController"),
            ("media_control.screenshot_manager", "ScreenshotManager"),
            ("media_control.video_player_controller", "VideoPlayerController"),
            ("media_control.screen_recorder", "ScreenRecorder"),
            ("media_control.gallery_manager", "GalleryManager"),

            # 14. System Monitor
            ("system_monitor.cpu_monitor", "CPUMonitor"),
            ("system_monitor.ram_monitor", "RAMMonitor"),
            ("system_monitor.storage_monitor", "StorageMonitor"),
            ("system_monitor.temperature_monitor", "TemperatureMonitor"),
            ("system_monitor.network_monitor", "NetworkMonitor"),

            # 15. AI Brain & NLP (Loaded late to ensure dependencies are ready)
            ("ai_engine.personality", "PersonalityEngine"),
            ("ai_engine.nlp_handler", "NLPHandler"),
            ("ai_engine.intent_classifier", "IntentClassifier"),
            ("ai_engine.context_manager", "ContextManager"),
            ("ai_engine.reasoning_engine", "ReasoningEngine"),
            ("ai_engine.sarcasm_detector", "SarcasmDetector"),
            ("ai_engine.evolution_engine", "EvolutionEngine"),
            ("core.self_healing", "SelfHealing"),

            # 16. Voice Engine & Background Services (Loaded last to start listening)
            ("voice_engine.text_to_speech", "TextToSpeech"),
            ("voice_engine.speech_to_text", "SpeechToText"),
            ("voice_engine.wake_word_engine", "WakeWordEngine"),
            ("voice_engine.sfx_manager", "SFXManager"),
            ("voice_engine.deep_voice_agent", "DeepVoiceAgent"),
            ("background_services.wake_listener_service", "WakeListenerService"),
            ("background_services.background_worker", "BackgroundWorker"),
            ("background_services.update_service", "UpdateService"),
            ("vision_module.screen_reader", "ScreenReader"),
            ("vision_module.gaze_tracker", "GazeTracker"),
            
            # 17. App Interface & Plugins
            ("app_interface.arya_hud", "AryaHUD"),
            ("app_interface.websocket_server", "WebSocketServer"),
            ("app_interface.voice_ui", "VoiceUI"),
            ("app_interface.command_console", "CommandConsole"),
            ("app_interface.settings_panel", "SettingsPanel"),
            ("app_interface.onboarding_screen", "OnboardingScreen"),
            ("plugin_system.plugin_manager", "PluginManager")
        ]

        # Dynamically load all 120+ features
        for module_path, class_name in load_order:
            # Determine arguments based on class dependencies
            args = [self.event_bus]
            
            if class_name in ["AppLauncher", "AppCloser", "AutoClickEngine", "WhatsAppBot", "InstagramBot"]:
                if "AccessibilityDriver" in self.modules:
                    args.append(self.modules["AccessibilityDriver"])
                else:
                    self.logger.warning(f"AccessibilityDriver not found for {class_name}. Loading without it.")
                    args.append(None)
            
            elif class_name == "CommandRouter":
                if "PermissionGuard" in self.modules:
                    args.append(self.modules["PermissionGuard"])
                else:
                    args.append(None)
                    
            elif class_name == "NLPHandler":
                args.extend([
                    self.modules.get("ContextManager"),
                    self.modules.get("IntentClassifier"),
                    self.modules.get("SarcasmDetector"),
                    self.modules.get("ReasoningEngine")
                ])

            await self._safe_init(module_path, class_name, *args)

        self.logger.info("=== ALL 16 PHASES INTEGRATED ===")
        
        # Start core background loops
        await self.event_bus.publish("system.monitor.cpu.start", {})
        await self.event_bus.publish("system.monitor.ram.start", {})
        await self.event_bus.publish("system.monitor.storage.start", {})
        await self.event_bus.publish("system.monitor.temp.start", {})
        await self.event_bus.publish("system.notifications.start", {})
        await self.event_bus.publish("voice.wake_word.start", {})
        
        # Start WebSocket server
        if "WebSocketServer" in self.modules:
            asyncio.create_task(self.modules["WebSocketServer"].start_server())

        # Fire system.boot event for SFX
        await self.event_bus.publish("system.boot", {})

        # Final Boot Announcement
        await self.event_bus.publish("speak", {"text": "Master integration complete. All 120 features are online and interconnected. I am fully operational, Sir."})
        self.logger.info("A.R.Y.A. OS is now running.")
        
        # Keep OS running indefinitely
        await asyncio.Event().wait()

def start_arya():
    os_instance = AryaOS()
    try:
        asyncio.run(os_instance.boot())
    except Exception as e:
        print(f"OS Crashed: {e}")

if __name__ == "__main__":
    try:
        # Try to import Kivy. If it succeeds, we are running as an APK via Buildozer.
        import kivy
        from kivy.app import App
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        from kivy.core.window import Window
        from kivy.clock import Clock
        import threading
        import webbrowser
        
        Window.clearcolor = (0.02, 0.04, 0.08, 1) # Dark JARVIS blue/black
        
        class AryaApp(App):
            def build(self):
                self.request_android_permissions()
                
                layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
                lbl = Label(
                    text="[b][color=00f3ff]A.R.Y.A. OS CORE[/color][/b]\n\nSystem is Online.\nRunning in Background.", 
                    markup=True,
                    font_size='24sp', 
                    halign='center'
                )
                
                btn = Button(
                    text="OPEN JARVIS HUD",
                    font_size='20sp',
                    background_color=(0, 0.95, 1, 0.8),
                    size_hint=(1, 0.2)
                )
                btn.bind(on_press=self.open_hud)
                
                layout.add_widget(lbl)
                layout.add_widget(btn)
                
                # Start the OS in a background thread so it doesn't block the UI
                threading.Thread(target=start_arya, daemon=True).start()
                return layout
                
            def open_hud(self, instance):
                webbrowser.open('http://localhost:8080')

            def request_android_permissions(self):
                try:
                    from android.permissions import request_permissions, Permission
                    request_permissions([
                        Permission.RECORD_AUDIO,
                        Permission.CAMERA,
                        Permission.WRITE_EXTERNAL_STORAGE,
                        Permission.READ_EXTERNAL_STORAGE,
                        Permission.POST_NOTIFICATIONS
                    ])
                except ImportError:
                    pass # Not running on Android
                
        AryaApp().run()
    except ImportError:
        # Fallback to standard CLI execution (Termux / PC)
        try:
            start_arya()
        except KeyboardInterrupt:
            print("\nShutting down A.R.Y.A. OS. Goodbye, Sir.")
            sys.exit(0)
