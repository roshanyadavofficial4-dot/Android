import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger
from app_automation.accessibility_driver import AccessibilityDriver

class UIElementDetector:
    def __init__(self, event_bus: EventBus, driver: AccessibilityDriver):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.driver = driver
        self.logger.info("UI Element Detector initialized. I see everything on your screen, Sir. Everything.")

    async def find_element(self, text: str = None, resource_id: str = None, description: str = None):
        device = self.driver.get_device()
        if not device:
            self.logger.warning("Device not connected. Cannot detect UI elements.")
            return None

        self.logger.debug(f"Searching for UI element - Text: '{text}', ID: '{resource_id}', Desc: '{description}'")
        
        try:
            # Run uiautomator2 search in a separate thread to avoid blocking the event loop
            element = await asyncio.to_thread(self._search_sync, device, text, resource_id, description)
            
            if element and element.exists:
                self.logger.info("UI Element found successfully.")
                return element
            else:
                self.logger.warning("UI Element not found on the current screen.")
                return None
        except Exception as e:
            self.logger.error(f"Error detecting UI element: {e}")
            return None

    def _search_sync(self, device, text, resource_id, description):
        # uiautomator2 selector logic
        if text:
            return device(text=text)
        elif resource_id:
            return device(resourceId=resource_id)
        elif description:
            return device(description=description)
        return None
