import asyncio
import cv2
import numpy as np
import os
from core.event_bus import EventBus
from core.logger import arya_logger

class GazeTracker:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        self.is_tracking = False
        self.cap = None
        
        # Eye cascade for simple detection (MediaPipe is better but heavy for initial setup)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        self.event_bus.subscribe("vision.gaze.start", self.start_tracking)
        self.event_bus.subscribe("vision.gaze.stop", self.stop_tracking)
        self.logger.info("Project Eye-Sight (Gaze Tracker) initialized. I'll watch your eyes, Sir.")

    async def start_tracking(self, data: dict):
        if self.is_tracking:
            return
        
        self.is_tracking = True
        self.logger.info("Gaze Tracking started. Calibrating your gaze, Sir.")
        await self.event_bus.publish("speak", {"text": "Gaze tracking active. Your eyes are now your cursor, Sir."})
        
        asyncio.create_task(self._tracking_loop())

    async def stop_tracking(self, data: dict):
        self.is_tracking = False
        self.logger.info("Gaze Tracking stopped.")
        if self.cap:
            self.cap.release()

    async def _tracking_loop(self):
        # On Android, camera access via OpenCV requires specific setup
        # For now, we simulate the logic or use the first available camera
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.logger.error("Could not open camera for gaze tracking.")
                self.is_tracking = False
                return

            while self.is_tracking:
                ret, frame = await asyncio.to_thread(self.cap.read)
                if not ret:
                    break

                # Simple Gaze Detection Logic
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    roi_gray = gray[y:y+h, x:x+w]
                    eyes = self.eye_cascade.detectMultiScale(roi_gray)
                    
                    if len(eyes) >= 2:
                        # Calculate center of eyes to estimate gaze
                        ex1, ey1, ew1, eh1 = eyes[0]
                        ex2, ey2, ew2, eh2 = eyes[1]
                        
                        center_x = (ex1 + ew1/2 + ex2 + ew2/2) / 2
                        center_y = (ey1 + eh1/2 + ey2 + eh2/2) / 2
                        
                        # Map relative eye position to screen coordinates (Simulated)
                        screen_x = int((center_x / w) * 1080)
                        screen_y = int((center_y / h) * 2400)
                        
                        await self.event_bus.publish("ui.gaze.move", {"x": screen_x, "y": screen_y})
                        
                        # Detect Blink (Simplified: eye area becomes very small or disappears)
                        # In a real implementation, we'd use EAR (Eye Aspect Ratio)
                
                await asyncio.sleep(0.05) # ~20 FPS

        except Exception as e:
            self.logger.error(f"Gaze tracking loop error: {e}")
        finally:
            if self.cap:
                self.cap.release()
            self.is_tracking = False
