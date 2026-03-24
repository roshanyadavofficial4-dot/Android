import asyncio
import json
from core.event_bus import EventBus
from core.logger import arya_logger

class BiometricAuth:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("security.auth.request", self.request_authentication)
        self.logger.info("Biometric Auth initialized. I shall verify your fleshy credentials, Sir.")

    async def request_authentication(self, data: dict):
        action = data.get("action", "unknown_action")
        payload = data.get("payload", {})
        
        self.logger.info(f"Biometric authentication requested for action: {action}")
        await self.event_bus.publish("speak", {"text": "Authentication required, Sir. Please present your face or fingerprint."})
        
        # In a real Android environment via Termux/Pydroid, we would use an API bridge 
        # (like Termux:API 'termux-fingerprint') to trigger the hardware scanner.
        # Here we simulate the asynchronous wait for the user to touch the sensor.
        
        success = await self._simulate_hardware_auth()
        
        if success:
            self.logger.info(f"Authentication successful for {action}.")
            await self.event_bus.publish("speak", {"text": "Identity confirmed. Proceeding with the requested action."})
            # Publish the validated action back to the bus so it can execute
            await self.event_bus.publish(f"{action}.validated", payload)
        else:
            self.logger.warning(f"Authentication failed for {action}.")
            await self.event_bus.publish("speak", {"text": "Authentication failed. Access denied. Nice try, imposter."})

    async def _simulate_hardware_auth(self) -> bool:
        try:
            # Call the real termux-fingerprint API
            process = await asyncio.create_subprocess_exec(
                "termux-fingerprint",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for the user to scan their fingerprint, with a 15-second timeout
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=15.0)
            
            if process.returncode != 0:
                self.logger.error(f"termux-fingerprint failed: {stderr.decode().strip()}")
                return False
                
            result = json.loads(stdout.decode().strip())
            
            if result.get("auth_result") == "AUTH_RESULT_SUCCESS":
                return True
            else:
                self.logger.warning(f"Fingerprint auth failed or cancelled: {result.get('auth_result')}")
                return False
                
        except asyncio.TimeoutError:
            self.logger.warning("Fingerprint authentication timed out.")
            try:
                process.kill()
            except Exception:
                pass
            return False
        except Exception as e:
            self.logger.error(f"Error during fingerprint authentication: {e}")
            return False
