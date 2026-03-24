import os
import asyncio
import subprocess
from core.event_bus import EventBus
from core.logger import arya_logger
from core.config import IS_ANDROID

class FilePreviewEngine:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("file.preview", self.handle_preview)
        self.logger.info("File Preview Engine initialized. Ready to show you what you've downloaded, Sir.")

    async def handle_preview(self, data: dict):
        file_path = data.get("path")
        if not file_path:
            self.logger.error("No file path provided for preview.")
            return

        if not os.path.exists(file_path):
            self.logger.error(f"File does not exist: {file_path}")
            await self.event_bus.publish("speak", {"text": "The file you want to preview does not exist, Sir."})
            return

        self.logger.info(f"Previewing file: {file_path}")
        if IS_ANDROID:
            try:
                # Use termux-open to open the file with the default Android app
                process = await asyncio.create_subprocess_exec(
                    "termux-open", file_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                await process.communicate()
                self.logger.debug(f"Opened {file_path} for preview.")
                await self.event_bus.publish("speak", {"text": "Opening the file now, Sir."})
            except Exception as e:
                self.logger.error(f"Failed to preview file: {e}")
                await self.event_bus.publish("speak", {"text": "I encountered an error while trying to open the file, Sir."})
        else:
            self.logger.warning("Not on Android. Simulating file preview.")
            import platform
            sys_name = platform.system()
            try:
                if sys_name == 'Windows':
                    os.startfile(file_path)
                elif sys_name == 'Darwin':
                    subprocess.Popen(["open", file_path])
                else:
                    subprocess.Popen(["xdg-open", file_path])
                await self.event_bus.publish("speak", {"text": "Opening the file now, Sir."})
            except Exception as e:
                self.logger.error(f"Failed to preview file on PC: {e}")
