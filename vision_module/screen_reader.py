import asyncio
import os
import json
from core.event_bus import EventBus
from core.logger import arya_logger
from google.genai import GoogleGenAI

try:
    import uiautomator2 as u2
except ImportError:
    u2 = None

class ScreenReader:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.device = None
        self.is_reading = False
        
        self.event_bus.subscribe("vision.screen.read", self.read_screen)
        self.logger.info("Vision Contextual Awareness (Screen Reader) initialized. I am watching you, Sir... for your benefit.")
        self._connect()

    def _connect(self):
        if not u2:
            self.logger.warning("uiautomator2 not installed. Screen reading will be simulated.")
            return
        try:
            self.device = u2.connect()
            self.logger.info("Successfully connected to Android UI Automator for Screen Reading.")
        except Exception as e:
            self.logger.error(f"Failed to connect to uiautomator2 for Screen Reading: {e}")

    async def read_screen(self, data: dict):
        if self.is_reading:
            return
        
        self.is_reading = True
        self.logger.info("Screen Reader: Capturing screen content...")
        await self.event_bus.publish("speak", {"text": "Analyzing your screen, Sir. Please stand by."})

        try:
            # 1. Capture screen hierarchy (XML or JSON)
            if self.device:
                # Get the view hierarchy as a string
                xml_dump = await asyncio.to_thread(self.device.dump_hierarchy)
                # We can also take a screenshot if needed
                # screenshot = await asyncio.to_thread(self.device.screenshot, format='opencv')
            else:
                # Simulated data for web preview
                xml_dump = "<node text='Instagram' class='android.widget.TextView'><node text='Post by @tonystark' class='android.widget.TextView'><node text='I love cheeseburgers' class='android.widget.TextView'></node></node></node>"
                self.logger.info("Simulated screen dump used.")

            # 2. Use Gemini to interpret the screen
            analysis_prompt = f"""
            You are the A.R.Y.A. OS Vision Engine. 
            The user is looking at their Android screen. 
            Here is the UI hierarchy dump:
            
            ```xml
            {xml_dump}
            ```
            
            Please analyze what the user is doing and provide a SMART, PROACTIVE suggestion or insight. 
            Address the user as "Sir". 
            Be concise and helpful. 
            Example: "Sir, I see you're looking at a restaurant on Instagram. Would you like me to check its reviews or book a table?"
            """
            
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                self.logger.error("GEMINI_API_KEY not found. Cannot analyze screen.")
                self.is_reading = False
                return

            ai = GoogleGenAI(apiKey=api_key)
            response = await ai.models.generateContent({
                "model": "gemini-3.1-flash-preview",
                "contents": analysis_prompt
            })
            
            suggestion = response.text.strip()
            if suggestion:
                self.logger.info(f"Screen Analysis: {suggestion}")
                await self.event_bus.publish("speak", {"text": suggestion})
                await self.event_bus.publish("ui.notification", {"title": "A.R.Y.A. Insight", "message": suggestion})

        except Exception as e:
            self.logger.error(f"Screen reading failed: {e}")
            await self.event_bus.publish("speak", {"text": "I'm having trouble seeing your screen clearly, Sir. My apologies."})
        finally:
            self.is_reading = False
