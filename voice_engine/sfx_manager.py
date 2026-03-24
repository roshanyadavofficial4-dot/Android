import asyncio
import os
import subprocess
from core.event_bus import EventBus
from core.logger import arya_logger
from core.config import IS_ANDROID, IS_PC

if IS_PC:
    try:
        import playsound
    except ImportError:
        playsound = None

class SFXManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        # Map events to sound files
        self.sfx_map = {
            "system.boot": "boot_sequence.mp3",
            "listen_for_command": "listening_blip.mp3",
            "command_received": "data_processing.mp3",
            "action_result": "success_chime.mp3",
            "system_error": "error_buzzer.mp3"
        }
        
        # Subscribe to events
        self.event_bus.subscribe("system.boot", self.play_boot)
        self.event_bus.subscribe("listen_for_command", self.play_listen)
        self.event_bus.subscribe("command_received", self.play_processing)
        self.event_bus.subscribe("action_result", self.play_action_result)
        self.event_bus.subscribe("system_error", self.play_error)
        
        self.logger.info("SFX Manager initialized. Ready to make some sci-fi noises, Sir.")

    def _get_sfx_path(self, filename):
        # Assuming sounds are placed in an 'assets/sfx' folder in the root directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "assets", "sfx", filename)

    async def _play_sfx(self, filename: str):
        filepath = self._get_sfx_path(filename)
        if not os.path.exists(filepath):
            # We won't log an error every time to avoid spamming if files aren't downloaded yet
            return
            
        def _play():
            try:
                if IS_ANDROID:
                    os.system(f"termux-media-player play {filepath} > /dev/null 2>&1")
                elif IS_PC:
                    if playsound:
                        try:
                            playsound.playsound(filepath)
                        except Exception as e:
                            self.logger.error(f"PC audio player choked on SFX: {e}")
                    else:
                        import platform
                        sys_name = platform.system()
                        if sys_name == 'Windows':
                            subprocess.Popen(["start", "", filepath], shell=True)
                        elif sys_name == 'Darwin':
                            subprocess.Popen(["afplay", filepath])
                        else:
                            subprocess.Popen(["mpg123", filepath])
            except Exception as e:
                self.logger.error(f"SFX Playback Error: {e}")

        # Run in a separate thread so it doesn't block the event loop
        await asyncio.to_thread(_play)

    async def play_boot(self, data: dict = None):
        await self._play_sfx(self.sfx_map["system.boot"])

    async def play_listen(self, data: dict = None):
        await self._play_sfx(self.sfx_map["listen_for_command"])

    async def play_processing(self, data: dict = None):
        await self._play_sfx(self.sfx_map["command_received"])

    async def play_action_result(self, data: dict):
        status = data.get("status", "").lower()
        if status == "success":
            await self._play_sfx(self.sfx_map["action_result"])
        elif status == "failed":
            await self._play_sfx(self.sfx_map["system_error"])

    async def play_error(self, data: dict = None):
        await self._play_sfx(self.sfx_map["system_error"])
