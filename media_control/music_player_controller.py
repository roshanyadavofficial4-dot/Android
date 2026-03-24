import asyncio
import subprocess
from core.event_bus import EventBus
from core.logger import arya_logger

class MusicPlayerController:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.event_bus.subscribe("media.play", self.play)
        self.event_bus.subscribe("media.pause", self.pause)
        self.event_bus.subscribe("media.next", self.next_track)
        self.logger.info("Music Player Controller initialized. I'm ready to drop the beat, Sir.")

    async def _send_media_command(self, command: str):
        try:
            proc = await asyncio.create_subprocess_exec(
                "termux-media-player", command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            self.logger.debug(f"Media command '{command}' executed.")
        except Exception as e:
            self.logger.error(f"Failed to execute media command '{command}': {e}")

    async def play(self, data: dict):
        self.logger.info("Resuming playback.")
        await self._send_media_command("play")

    async def pause(self, data: dict):
        self.logger.info("Pausing playback.")
        await self._send_media_command("pause")

    async def next_track(self, data: dict):
        self.logger.info("Skipping to the next track.")
        # termux-media-player doesn't natively support 'next' without a specific file,
        # but we can simulate a media key event if needed, or use 'termux-volume' if we want to hack it.
        # For now, we'll just log it as termux-media-player is limited for global control.
        # Alternatively, we can use input keyevent 87 (KEYCODE_MEDIA_NEXT) if rooted.
        try:
            proc = await asyncio.create_subprocess_exec(
                "su", "-c", "input keyevent 87",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            self.logger.info("Sent NEXT_TRACK keyevent via su.")
        except Exception as e:
            self.logger.warning(f"Could not send next track command (requires root for keyevent): {e}")
