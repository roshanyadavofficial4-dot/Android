import asyncio
from core.event_bus import EventBus
from core.logger import arya_logger

class PermissionGuard:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.logger.info("Permission Guard initialized. Keeping us out of digital jail, Sir.")
        
        # Mock database of dangerous commands and required permissions
        self.restricted_commands = {
            "factory_reset": ["android.permission.MASTER_CLEAR"],
            "format_sd": ["android.permission.MOUNT_FORMAT_FILESYSTEMS"],
            "read_sms": ["android.permission.READ_SMS"],
            "send_sms": ["android.permission.SEND_SMS"],
            "access_camera": ["android.permission.CAMERA"]
        }

    async def validate_command(self, command_intent: str) -> bool:
        self.logger.debug(f"Validating permissions for intent: {command_intent}")
        
        if command_intent in self.restricted_commands:
            required_perms = self.restricted_commands[command_intent]
            # In a real Android environment (via plyer/jnius), we would check actual permissions here.
            # For now, we simulate a check.
            has_permission = await self._check_android_permissions(required_perms)
            
            if not has_permission:
                self.logger.warning(f"Permission denied for {command_intent}. We lack the authority, Sir.")
                await self.event_bus.publish("speak", {
                    "text": "I'm afraid I can't do that, Sir. We lack the necessary Android permissions. How embarrassing."
                })
                return False
                
        self.logger.debug(f"Command {command_intent} is safe to execute.")
        return True

    async def _check_android_permissions(self, permissions: list) -> bool:
        # In Termux, permissions are granted to the Termux app itself.
        # We assume the user has granted necessary permissions (Storage, Camera, Mic, Location)
        # via Android Settings -> Apps -> Termux -> Permissions.
        # We block highly destructive intents that Termux cannot execute anyway.
        if "android.permission.MASTER_CLEAR" in permissions:
            self.logger.warning("MASTER_CLEAR is not supported in Termux.")
            return False
        if "android.permission.MOUNT_FORMAT_FILESYSTEMS" in permissions:
            self.logger.warning("Formatting filesystems is blocked for safety.")
            return False
        return True
