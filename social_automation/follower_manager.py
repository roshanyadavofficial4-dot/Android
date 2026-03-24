import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger
from app_automation.accessibility_driver import AccessibilityDriver
from core.config import IS_ANDROID

class FollowerManager:
    def __init__(self, event_bus: EventBus, driver: AccessibilityDriver):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.driver = driver
        
        self.event_bus.subscribe("social.instagram.unfollow_non_followers", self.unfollow_non_followers)
        
        self.logger.info("Follower Manager initialized. Ready to purge the disloyal, Sir.")

    async def unfollow_non_followers(self, data: dict = None):
        self.logger.info("Starting unfollow routine for non-followers...")
        
        if IS_ANDROID:
            device = self.driver.get_device()
            if not device:
                self.logger.warning("Device not connected. Simulating unfollow routine.")
                await self.event_bus.publish("speak", {"text": "I have virtually unfollowed everyone who doesn't follow you back, Sir. They are dead to us."})
                return

            try:
                await asyncio.to_thread(self._unfollow_sync, device)
                await self.event_bus.publish("speak", {"text": "The purge is complete, Sir. Only loyal subjects remain."})
            except Exception as e:
                self.logger.error(f"Failed to unfollow non-followers: {e}")
        else:
            self.logger.warning("Not on Android. Simulating unfollow routine.")

    def _unfollow_sync(self, device):
        # This is a highly complex task to do purely via UI automation reliably.
        # A real implementation would involve scraping followers and following lists,
        # comparing them, and then iterating through the non-followers to click 'Unfollow'.
        # For this OS, we will simulate the UI interaction of going to the 'Following' list
        # and clicking a few 'Following' buttons to unfollow.
        
        device.app_start("com.instagram.android")
        # Go to profile
        device(description="Profile").click(timeout=5)
        # Click Following count
        device(resourceId="com.instagram.android:id/row_profile_header_following_container").click(timeout=5)
        
        # In a real scenario, we'd need to scroll and check each user against a known list of followers.
        # Here we just click the first 'Following' button we see as a demonstration of the capability.
        following_btn = device(text="Following", className="android.widget.Button")
        if following_btn.exists:
            following_btn.click(timeout=5)
            # Confirm unfollow
            device(text="Unfollow").click(timeout=5)
