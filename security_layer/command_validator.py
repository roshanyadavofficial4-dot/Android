import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class CommandValidator:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        # List of commands that require strict biometric verification
        self.dangerous_commands = [
            "file.delete",
            "system.factory_reset",
            "security.lockdown",
            "social.message.send_mass",
            "payment.transfer"
        ]
        
        self.event_bus.subscribe("command.validate", self.validate_command)
        self.logger.info("Command Validator initialized. I will prevent you from accidentally deleting your thesis, Sir.")

    async def validate_command(self, data: dict):
        action = data.get("action")
        payload = data.get("payload", {})
        
        if not action:
            self.logger.error("Received validation request with no action.")
            return

        self.logger.info(f"Validating command: {action}")
        
        if action in self.dangerous_commands:
            self.logger.warning(f"Dangerous command detected: {action}. Requesting biometric auth.")
            # Route to biometric auth instead of executing directly
            await self.event_bus.publish("security.auth.request", {
                "action": action,
                "payload": payload
            })
        else:
            # Safe command, execute directly
            self.logger.debug(f"Command '{action}' is safe. Executing.")
            await self.event_bus.publish(action, payload)
