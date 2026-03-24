import cv2
import asyncio
import os
from core.event_bus import EventBus
from core.logger import arya_logger

class CameraController:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.is_streaming = False
        self.camera_index = 0 # 0 for back camera, 1 for front camera usually
        
        self.event_bus.subscribe("vision.camera.take_photo", self.take_photo)
        self.event_bus.subscribe("vision.camera.start_stream", self.start_stream)
        self.event_bus.subscribe("vision.camera.stop_stream", self.stop_stream)
        
        self.logger.info("Camera Controller initialized. I am now capable of visual judgment, Sir.")

    async def take_photo(self, data: dict):
        save_path = data.get("save_path", "/storage/emulated/0/DCIM/arya_capture.jpg")
        self.logger.info(f"Attempting to capture a photo to {save_path}...")
        
        success = await asyncio.to_thread(self._take_photo_sync, save_path)
        
        if success:
            await self.event_bus.publish("speak", {"text": "Photo captured, Sir. I hope you got my good side."})
            await self.event_bus.publish("vision.photo_ready", {"path": save_path})
        else:
            await self.event_bus.publish("speak", {"text": "Failed to access the camera. Perhaps the lens cap is on, or Android is denying me permissions again."})

    def _take_photo_sync(self, save_path: str) -> bool:
        try:
            cap = cv2.VideoCapture(self.camera_index)
            if not cap.isOpened():
                self.logger.error("Cannot open camera.")
                return False
                
            # Warm up the camera sensor
            for _ in range(5):
                cap.read()
                
            ret, frame = cap.read()
            if ret:
                # Ensure directory exists
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                cv2.imwrite(save_path, frame)
                self.logger.debug(f"Image saved to {save_path}")
            cap.release()
            return ret
        except Exception as e:
            self.logger.error(f"Camera capture error: {e}")
            return False

    async def start_stream(self, data: dict):
        if self.is_streaming:
            self.logger.warning("Camera stream is already running.")
            return
            
        self.is_streaming = True
        self.logger.info("Starting live camera stream for analysis...")
        await self.event_bus.publish("speak", {"text": "Live vision activated. I am watching, Sir."})
        asyncio.create_task(self._stream_loop())

    async def stop_stream(self, data: dict = None):
        self.is_streaming = False
        self.logger.info("Stopping live camera stream.")
        await self.event_bus.publish("speak", {"text": "Vision stream deactivated. I am blind once more."})

    async def _stream_loop(self):
        # In a real Android environment, continuous cv2.VideoCapture might be heavy.
        # This loop captures frames periodically for the object detection and gesture engine.
        self.logger.info("Camera stream loop started.")
        
        # Temporary path for internal analysis frames
        analysis_path = "/tmp/arya_analysis.jpg"
        os.makedirs(os.path.dirname(analysis_path), exist_ok=True)
        
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            self.logger.error("Cannot open camera for streaming.")
            self.is_streaming = False
            return

        try:
            while self.is_streaming:
                ret, frame = cap.read()
                if ret:
                    # Save frame for analysis
                    cv2.imwrite(analysis_path, frame)
                    # Trigger gesture detection for UI manipulation
                    await self.event_bus.publish("vision.gesture.detect", {"image_path": analysis_path})
                
                # Frequency of analysis (higher = smoother UI, but more CPU)
                # 0.1s = 10 FPS for gestures
                await asyncio.sleep(0.1)
        except Exception as e:
            self.logger.error(f"Stream loop error: {e}")
        finally:
            cap.release()
            self.logger.info("Camera stream loop terminated.")
