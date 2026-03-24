import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger
from app_automation.accessibility_driver import AccessibilityDriver

class AutoScrollEngine:
    def __init__(self, event_bus: EventBus, driver: AccessibilityDriver):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.driver = driver
        
        self.event_bus.subscribe("ui.scroll", self.handle_scroll)
        self.logger.info("Auto Scroll Engine initialized. Let's see what's at the bottom of this endless feed, Sir.")

    async def handle_scroll(self, data: dict):
        direction = data.get("direction", "forward") # forward (down), backward (up), to_beginning, to_end
        
        self.logger.info(f"Attempting to scroll {direction}.")
        device = self.driver.get_device()
        
        if not device:
            self.logger.warning("Device not connected. Simulating scroll.")
            await self.event_bus.publish("action_result", {"action": "ui.scroll", "status": "Success", "simulated": True})
            return

        try:
            await asyncio.to_thread(self._scroll_sync, device, direction)
            self.logger.info(f"Scroll {direction} successful.")
            
            # Report Success
            await self.event_bus.publish("action_result", {
                "action": "ui.scroll", 
                "status": "Success", 
                "direction": direction
            })
        except Exception as e:
            self.logger.error(f"Scroll failed: {e}")
            
            # Report Failure
            await self.event_bus.publish("action_result", {
                "action": "ui.scroll", 
                "status": "Failed", 
                "reason": str(e)
            })

    def _scroll_sync(self, device, direction: str):
        # uiautomator2 scroll logic
        if direction in ["forward", "down"]:
            # Scroll forward (moves content up, revealing content below)
            device(scrollable=True).scroll.forward()
        elif direction in ["backward", "up"]:
            # Scroll backward (moves content down, revealing content above)
            device(scrollable=True).scroll.backward()
        elif direction == "to_beginning":
            device(scrollable=True).scroll.toBeginning()
        elif direction == "to_end":
            device(scrollable=True).scroll.toEnd()
        else:
            # Fallback: Perform a generic swipe up to scroll down
            self.logger.debug("Using fallback swipe gesture for scrolling.")
            device.swipe_ext("up", scale=0.8)
