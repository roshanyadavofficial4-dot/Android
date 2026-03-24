import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class OnboardingScreen:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("ui.onboarding.start", self.start_onboarding)
        self.logger.info("Onboarding Screen initialized. Welcome to the future, Sir.")

    async def start_onboarding(self, data: dict = None):
        self.logger.info("Starting Onboarding flow...")
        await self.event_bus.publish("speak", {"text": "Welcome, Sir. I am A.R.Y.A., your advanced personal assistant. Let's get you set up."})
        
        # 1. Ask for name
        await self.event_bus.publish("speak", {"text": "What shall I call you?"})
        # Wait for response...
        
        # 2. Ask for permissions
        await self.event_bus.publish("speak", {"text": "I will need access to your device's core functions to operate efficiently. Do I have your permission?"})
        # Wait for response...
        
        # 3. Complete
        await self.event_bus.publish("speak", {"text": "Excellent. All systems are go. How may I serve you today, Sir?"})
