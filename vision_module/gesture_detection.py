import asyncio
import os
from core.event_bus import EventBus
from core.logger import arya_logger

try:
    import mediapipe as mp
    import cv2
    HAS_VISION = True
except ImportError:
    HAS_VISION = False

class GestureDetectionEngine:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.event_bus.subscribe("vision.gesture.detect", self.detect_gesture)
        if HAS_VISION:
            self.logger.info("Gesture Detection Engine initialized. Ready to interpret your hand waving, Sir.")
        else:
            self.logger.warning("Mediapipe/OpenCV not found. Gesture detection will be simulated, Sir.")

    async def detect_gesture(self, data: dict):
        if not HAS_VISION:
            # Simulate some movement if vision is missing
            import time
            import math
            t = time.time()
            simulated_data = {
                "action": "manipulate",
                "rotation": [math.sin(t) * 0.5, math.cos(t) * 0.5, 0],
                "scale": 1.0 + math.sin(t * 0.5) * 0.2,
                "position": [0, 0, math.sin(t * 0.3) * 1.0]
            }
            await self.event_bus.publish("ui.gesture_control", simulated_data)
            return

        image_path = data.get("image_path")
        if not image_path or not os.path.exists(image_path):
            self.logger.error("Invalid image path provided for gesture detection.")
            return

        self.logger.info(f"Analyzing hand spatial data in {image_path}...")
        
        spatial_data = await asyncio.to_thread(self._analyze_spatial_sync, image_path)
        
        if spatial_data:
            self.logger.debug(f"Spatial data: {spatial_data}")
            # Send to frontend via event bus (which will be picked up by the WebSocket server)
            await self.event_bus.publish("ui.gesture_control", spatial_data)
        else:
            self.logger.warning("No hand detected for spatial analysis.")

    def _analyze_spatial_sync(self, image_path: str) -> dict:
        if not HAS_VISION: return None
        try:
            mp_hands = mp.solutions.hands
            with mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5) as hands:
                image = cv2.imread(image_path)
                if image is None: return None
                
                h, w, _ = image.shape
                results = hands.process(cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB))
                
                if not results.multi_hand_landmarks:
                    return None
                    
                hand_landmarks = results.multi_hand_landmarks[0]
                
                # 1. Rotation: Based on palm center relative to image center
                # Map x, y to -1 to 1 range
                palm_x = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x
                palm_y = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y
                
                rot_y = (palm_x - 0.5) * 4  # Horizontal movement rotates around Y
                rot_x = (palm_y - 0.5) * 4  # Vertical movement rotates around X
                
                # 2. Zoom (Scale): Based on distance between thumb and index
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                
                distance = ((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)**0.5
                # Map distance (approx 0.05 to 0.3) to scale (0.5 to 2.5)
                scale = 0.5 + (distance * 8)
                
                # 3. Position Z: Based on hand area (bounding box size)
                # For simplicity, use distance between wrist and middle finger tip
                middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                hand_size = ((middle_tip.x - wrist.x)**2 + (middle_tip.y - wrist.y)**2)**0.5
                # Map hand_size to Z position (-2 to 2)
                pos_z = (hand_size - 0.3) * 10
                
                return {
                    "action": "manipulate",
                    "rotation": [rot_x, rot_y, 0],
                    "scale": scale,
                    "position": [0, 0, pos_z]
                }
        except Exception as e:
            self.logger.error(f"Spatial analysis error: {e}")
            return None
