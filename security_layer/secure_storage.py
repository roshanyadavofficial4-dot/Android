import asyncio
import os
import json
from core.event_bus import EventBus
from core.logger import arya_logger

try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

class SecureStorage:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.storage_dir = "security_layer/vault"
        self.key_file = "security_layer/.vault_key"
        self.vault_file = os.path.join(self.storage_dir, "secrets.enc")
        
        os.makedirs(self.storage_dir, exist_ok=True)
        self.cipher_suite = self._init_encryption()
        
        self.event_bus.subscribe("security.store.secret", self.store_secret)
        self.event_bus.subscribe("security.retrieve.secret", self.retrieve_secret)
        
        self.logger.info("Secure Storage initialized. Your API keys are locked in the vault, Sir.")

    def _init_encryption(self):
        if not Fernet:
            self.logger.warning("Cryptography library not found. Secure Storage will store data in plain text (NOT SECURE).")
            return None
            
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as key_file:
                key_file.write(key)
        else:
            with open(self.key_file, "rb") as key_file:
                key = key_file.read()
                
        return Fernet(key)

    def _read_vault(self) -> dict:
        if not os.path.exists(self.vault_file):
            return {}
            
        try:
            with open(self.vault_file, "rb") as f:
                data = f.read()
                
            if self.cipher_suite:
                decrypted_data = self.cipher_suite.decrypt(data)
                return json.loads(decrypted_data.decode('utf-8'))
            else:
                return json.loads(data.decode('utf-8'))
        except Exception as e:
            self.logger.error(f"Failed to read vault: {e}")
            return {}

    def _write_vault(self, data: dict):
        try:
            json_data = json.dumps(data).encode('utf-8')
            
            if self.cipher_suite:
                encrypted_data = self.cipher_suite.encrypt(json_data)
                with open(self.vault_file, "wb") as f:
                    f.write(encrypted_data)
            else:
                with open(self.vault_file, "wb") as f:
                    f.write(json_data)
        except Exception as e:
            self.logger.error(f"Failed to write to vault: {e}")

    async def store_secret(self, data: dict):
        key = data.get("key")
        value = data.get("value")
        
        if not key or not value:
            self.logger.error("Cannot store secret without key and value.")
            return
            
        vault_data = await asyncio.to_thread(self._read_vault)
        vault_data[key] = value
        await asyncio.to_thread(self._write_vault, vault_data)
        
        self.logger.info(f"Secret stored for key: {key}")
        await self.event_bus.publish("speak", {"text": "The secret has been securely stored in the vault, Sir."})

    async def retrieve_secret(self, data: dict):
        key = data.get("key")
        reply_to = data.get("reply_to") # Event to publish the result to
        
        if not key:
            self.logger.error("Cannot retrieve secret without a key.")
            return
            
        vault_data = await asyncio.to_thread(self._read_vault)
        value = vault_data.get(key)
        
        if value:
            self.logger.info(f"Secret retrieved for key: {key}")
            if reply_to:
                await self.event_bus.publish(reply_to, {"key": key, "value": value})
        else:
            self.logger.warning(f"Secret not found for key: {key}")
            if reply_to:
                await self.event_bus.publish(reply_to, {"key": key, "value": None})
