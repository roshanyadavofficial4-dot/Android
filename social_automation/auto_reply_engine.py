import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class AutoReplyEngine:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        # Local state for user's busy status
        self.user_state = "available" # can be "in class", "driving", "sleeping", "available"
        
        # Mock memory for friends (to be replaced by memory_system later)
        self.friends_list = ["tony", "pepper", "rhodey", "happy"]
        
        self.event_bus.subscribe("user.state.update", self.update_user_state)
        self.event_bus.subscribe("social.incoming_message", self.handle_incoming_message)
        
        self.logger.info("Auto Reply Engine initialized. I shall handle your social obligations while you are indisposed, Sir.")

    async def update_user_state(self, data: dict):
        state = data.get("state", "available").lower()
        self.user_state = state
        self.logger.info(f"User state updated to: {self.user_state}")
        
        # Also add to context manager so the LLM knows
        await self.event_bus.publish("context.add", {"role": "system", "text": f"User is currently: {self.user_state}"})

    async def handle_incoming_message(self, data: dict):
        sender = data.get("sender", "").lower()
        message = data.get("message", "")
        platform = data.get("platform", "whatsapp")
        
        self.logger.info(f"Incoming message from {sender} on {platform}: {message}")
        
        if self.user_state == "available":
            # Just read it out loud if available
            await self.event_bus.publish("speak", {"text": f"Sir, you have a new message from {sender}. They say: {message}"})
            return
            
        # User is busy. Generate auto-reply.
        self.logger.info(f"User is {self.user_state}. Generating auto-reply for {sender}.")
        
        reply_text = self._generate_reply(sender)
        
        # Send the reply
        await self.event_bus.publish("social.message.send", {
            "contact": sender,
            "message": reply_text,
            "platform": platform
        })
        
        # Notify user quietly
        await self.event_bus.publish("speak", {
            "text": f"I have auto-replied to {sender} since you are {self.user_state}, Sir."
        })

    def _generate_reply(self, sender: str) -> str:
        base_reason = f"He is currently {self.user_state}."
        
        if sender in self.friends_list:
            # Sarcastic reply for friends
            if self.user_state == "driving":
                return f"A.R.Y.A. here. The boss is driving and refuses to crash just to text you back. {base_reason} Try again later."
            elif self.user_state == "in class":
                return f"A.R.Y.A. here. He is pretending to pay attention in class. {base_reason} Please hold your trivial matters until he is free."
            else:
                return f"A.R.Y.A. here. He is currently '{self.user_state}', which is code for ignoring you. I'll pass the message along eventually."
        else:
            # Polite reply for others
            return f"Hello, this is A.R.Y.A., his automated assistant. {base_reason} He will get back to you as soon as possible."
