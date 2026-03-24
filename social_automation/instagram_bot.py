import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger
from app_automation.accessibility_driver import AccessibilityDriver

class InstagramBot:
    def __init__(self, event_bus: EventBus, driver: AccessibilityDriver):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.driver = driver
        
        self.event_bus.subscribe("social.instagram.like", self.like_post)
        self.event_bus.subscribe("social.instagram.follow", self.follow_user)
        self.event_bus.subscribe("social.instagram.comment", self.comment_on_post)
        
        self.logger.info("Instagram Bot initialized. Ready to validate your existence with artificial likes, Sir.")

    async def like_post(self, data: dict = None):
        self.logger.info("Liking current Instagram post...")
        device = self.driver.get_device()
        
        if not device:
            self.logger.warning("Device not connected. Simulating Instagram like.")
            await self.event_bus.publish("speak", {"text": "Consider it liked, Sir. Not that it matters."})
            return

        try:
            await asyncio.to_thread(self._like_post_sync, device)
            self.logger.debug("Post liked successfully.")
        except Exception as e:
            self.logger.error(f"Failed to like post: {e}")

    def _like_post_sync(self, device):
        # Double tap the center of the screen to like
        width, height = device.window_size()
        device.double_click(width // 2, height // 2)

    async def follow_user(self, data: dict):
        username = data.get("username")
        if not username:
            return
            
        self.logger.info(f"Following user: {username}...")
        device = self.driver.get_device()
        
        if not device:
            self.logger.warning("Device not connected. Simulating Instagram follow.")
            await self.event_bus.publish("speak", {"text": f"I have virtually followed {username}. They must be thrilled."})
            return

        try:
            await asyncio.to_thread(self._follow_user_sync, device, username)
            await self.event_bus.publish("speak", {"text": f"You are now following {username}, Sir. Try not to stalk them."})
        except Exception as e:
            self.logger.error(f"Failed to follow user: {e}")

    def _follow_user_sync(self, device, username: str):
        device.app_start("com.instagram.android")
        # Click search icon (bottom nav)
        device(description="Search and explore").click(timeout=5)
        # Click search bar
        device(resourceId="com.instagram.android:id/action_bar_search_edit_text").set_text(username)
        # Click top result
        device(resourceId="com.instagram.android:id/row_search_user_username", text=username).click(timeout=5)
        # Click Follow button
        follow_btn = device(text="Follow", className="android.widget.Button")
        if follow_btn.exists:
            follow_btn.click(timeout=5)

    async def comment_on_post(self, data: dict):
        comment = data.get("comment", "Great post!")
        self.logger.info(f"Commenting on post: '{comment}'")
        device = self.driver.get_device()
        
        if not device:
            self.logger.warning("Device not connected. Simulating Instagram comment.")
            return

        try:
            await asyncio.to_thread(self._comment_sync, device, comment)
            self.logger.debug("Comment posted.")
        except Exception as e:
            self.logger.error(f"Failed to comment on post: {e}")

    def _comment_sync(self, device, comment: str):
        # Assuming we are already looking at a post
        comment_icon = device(description="Comment")
        if comment_icon.exists:
            comment_icon.click(timeout=5)
            # Type comment
            device(resourceId="com.instagram.android:id/layout_comment_thread_edittext").set_text(comment)
            # Click Post
            device(text="Post").click(timeout=5)
