import asyncio
import subprocess
from core.event_bus import EventBus
from core.logger import arya_logger

class ScreenRecorder:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.is_recording = False
        self.process = None
        
        self.event_bus.subscribe("media.screen.record.start", self.start_recording)
        self.event_bus.subscribe("media.screen.record.stop", self.stop_recording)
        self.logger.info("Screen Recorder initialized. Ready to capture your digital exploits, Sir.")

    async def start_recording(self, data: dict):
        if self.is_recording:
            return
            
        filename = data.get("filename", "screen_record.mp4")
        save_path = f"/storage/emulated/0/Movies/{filename}"
        
        self.logger.info(f"Starting screen recording to {save_path}")
        await self.event_bus.publish("speak", {"text": "Initiating screen recording, Sir. Don't do anything embarrassing."})
        
        # Using Android's built-in screenrecord utility (requires adb or root)
        # In Termux, this usually requires root (`su -c`)
        try:
            self.process = await asyncio.create_subprocess_shell(
                f"su -c 'screenrecord {save_path}'",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            self.is_recording = True
        except Exception as e:
            self.logger.error(f"Failed to start screen recording: {e}")
            await self.event_bus.publish("speak", {"text": "I could not start the recording. Root access might be required."})

    async def stop_recording(self, data: dict = None):
        if not self.is_recording or not self.process:
            return
            
        self.logger.info("Stopping screen recording.")
        await self.event_bus.publish("speak", {"text": "Screen recording stopped, Sir. The file is saved in your Movies folder."})
        
        try:
            # Send SIGINT to stop the recording gracefully
            # Since it was run with su, we might need to kill it via su
            await asyncio.create_subprocess_shell("su -c 'pkill -INT screenrecord'")
            self.is_recording = False
            self.process = None
        except Exception as e:
            self.logger.error(f"Failed to stop screen recording: {e}")
