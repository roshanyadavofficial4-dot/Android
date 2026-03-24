import asyncio
import subprocess
from core.event_bus import EventBus
from core.logger import arya_logger

class VideoPlayerController:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("media.video.play", self.play_video)
        self.logger.info("Video Player Controller initialized. I'll queue up the moving pictures, Sir.")

    async def play_video(self, data: dict):
        video_path = data.get("path")
        if not video_path:
            self.logger.error("No video path provided.")
            return

        self.logger.info(f"Playing video: {video_path}")
        await self.event_bus.publish("speak", {"text": "Playing the requested video, Sir."})
        
        # In Termux, we can use termux-open to launch the default video player
        try:
            process = await asyncio.create_subprocess_exec(
                "termux-open", video_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Failed to play video: {stderr.decode().strip()}")
                await self.event_bus.publish("speak", {"text": "I encountered an error trying to play the video. Perhaps the format is unsupported."})
        except Exception as e:
            self.logger.error(f"Video playback error: {e}")
