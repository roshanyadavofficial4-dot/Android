import asyncio
import os
from core.event_bus import EventBus
from core.logger import arya_logger

try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

class PrivacyGuard:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.key_file = "security_layer/.encryption_key"
        self.cipher_suite = self._init_encryption()
        
        self.emergency_contact = "Mom" # Could be pulled from user_memory.db
        
        self.event_bus.subscribe("security.lockdown.validated", self.execute_lockdown)
        self.event_bus.subscribe("security.encrypt.file", self.encrypt_file)
        self.event_bus.subscribe("security.decrypt.file", self.decrypt_file)
        
        self.logger.info("Privacy Guard initialized. Your secrets are safe with me, Sir.")

    def _init_encryption(self):
        if not Fernet:
            self.logger.warning("Cryptography library not found. Encryption will be simulated.")
            return None
            
        if not os.path.exists(self.key_file):
            os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as key_file:
                key_file.write(key)
        else:
            with open(self.key_file, "rb") as key_file:
                key = key_file.read()
                
        return Fernet(key)

    async def execute_lockdown(self, data: dict = None):
        self.logger.critical("LOCKDOWN MODE INITIATED.")
        await self.event_bus.publish("speak", {"text": "Lockdown mode engaged. Encrypting memory, freezing device, and alerting emergency contacts. Good luck, Sir."})
        
        # 1. Encrypt user memory
        await self.encrypt_file({"filepath": "memory_system/user_memory.db"})
        
        # 2. Alert emergency contact
        location_msg = "Unknown location" # In a real scenario, fetch from location_services
        emergency_message = f"EMERGENCY: A.R.Y.A. Lockdown Mode activated. The user may be in danger. Last known status: {location_msg}."
        await self.event_bus.publish("social.message.send", {
            "contact": self.emergency_contact,
            "message": emergency_message,
            "platform": "sms"
        })
        
        # 3. Freeze the phone (Simulated via Accessibility Driver / Device Admin)
        self.logger.critical("Sending system lock command...")
        await self.event_bus.publish("system.screen.lock", {})
        
        # 4. Disable network (Optional, depending on threat model)
        # await self.event_bus.publish("system.wifi.set", {"state": "off"})

    async def encrypt_file(self, data: dict):
        filepath = data.get("filepath")
        if not filepath or not os.path.exists(filepath):
            self.logger.error(f"Cannot encrypt. File not found: {filepath}")
            return
            
        if not self.cipher_suite:
            self.logger.warning(f"Simulating encryption for {filepath}")
            return
            
        try:
            with open(filepath, "rb") as file:
                file_data = file.read()
            encrypted_data = self.cipher_suite.encrypt(file_data)
            with open(filepath, "wb") as file:
                file.write(encrypted_data)
            self.logger.info(f"Successfully encrypted {filepath}")
        except Exception as e:
            self.logger.error(f"Encryption failed for {filepath}: {e}")

    async def decrypt_file(self, data: dict):
        filepath = data.get("filepath")
        if not filepath or not os.path.exists(filepath):
            return
            
        if not self.cipher_suite:
            return
            
        try:
            with open(filepath, "rb") as file:
                encrypted_data = file.read()
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            with open(filepath, "wb") as file:
                file.write(decrypted_data)
            self.logger.info(f"Successfully decrypted {filepath}")
        except Exception as e:
            self.logger.error(f"Decryption failed for {filepath}: {e}")
