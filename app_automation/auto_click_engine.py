import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger
from app_automation.ui_element_detector import UIElementDetector
from app_automation.accessibility_driver import AccessibilityDriver

class AutoClickEngine:
    def __init__(self, event_bus: EventBus, driver: AccessibilityDriver):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.detector = UIElementDetector(event_bus, driver)
        
        self.event_bus.subscribe("ui.click", self.handle_click)
        self.logger.info("Auto Click Engine initialized. My virtual fingers are ready, Sir.")

    async def handle_click(self, data: dict):
        text = data.get("text")
        resource_id = data.get("resource_id")
        desc = data.get("description")
        
        target_name = text or resource_id or desc or "Unknown"
        self.logger.info(f"Attempting to click element: {target_name}")
        
        element = await self.detector.find_element(text=text, resource_id=resource_id, description=desc)
        
        if element:
            try:
                # Perform the click asynchronously
                await asyncio.to_thread(element.click)
                self.logger.info(f"Successfully clicked '{target_name}'.")
                
                # Report Success back to the Event Bus
                await self.event_bus.publish("action_result", {
                    "action": "ui.click", 
                    "status": "Success", 
                    "target": target_name
                })
            except Exception as e:
                self.logger.error(f"Click failed on '{target_name}': {e}")
                
                # Report Failure back to the Event Bus
                await self.event_bus.publish("action_result", {
                    "action": "ui.click", 
                    "status": "Failed", 
                    "reason": str(e)
                })
        else:
            self.logger.warning(f"Cannot click. Element '{target_name}' not found.")
            await self.event_bus.publish("action_result", {
                "action": "ui.click", 
                "status": "Failed", 
                "reason": "Element not found on screen"
            })
