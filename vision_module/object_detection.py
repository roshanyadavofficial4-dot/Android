# To download the required YOLOv4-tiny model files, run the following commands in your terminal:
# wget https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg
# wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights

import asyncio
import os
from core.event_bus import EventBus
from core.logger import arya_logger

try:
    import cv2
    import numpy as np
    HAS_VISION = True
except ImportError:
    HAS_VISION = False

class ObjectDetectionEngine:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.logger = arya_logger
        
        self.model_loaded = False
        self.classes = ["person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat", "traffic light",
                        "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow",
                        "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
                        "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard",
                        "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
                        "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
                        "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse", "remote", "keyboard", "cell phone",
                        "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear",
                        "hair drier", "toothbrush", "stethoscope", "syringe", "scalpel"]
        
        self.event_bus.subscribe("vision.object.find", self.handle_find_object)
        if HAS_VISION:
            self.logger.info("Object Detection Engine initialized. I am ready to play 'I Spy', Sir.")
        else:
            self.logger.warning("OpenCV/NumPy not found. Object detection is disabled, Sir.")

    async def handle_find_object(self, data: dict):
        target_object = data.get("target_object", "").lower()
        image_path = data.get("image_path")
        
        if not image_path or not target_object:
            return

        self.logger.info(f"Searching for '{target_object}' in {image_path}...")
        await self.event_bus.publish("speak", {"text": f"Scanning the area for your {target_object}, Sir."})
        
        detected_objects = await asyncio.to_thread(self._detect_objects_sync, image_path)
        
        if target_object in detected_objects:
            await self.event_bus.publish("speak", {"text": f"Ah, I see the {target_object}, Sir. It is exactly where you left it. Shocking, I know."})
            self.logger.info(f"Target '{target_object}' found!")
        elif detected_objects:
            objects_str = ", ".join(list(set(detected_objects))[:3])
            await self.event_bus.publish("speak", {"text": f"I don't see a {target_object}. However, I do see a {objects_str}. Does that help?"})
        else:
            await self.event_bus.publish("speak", {"text": f"I see absolutely nothing of interest, Sir. Certainly not a {target_object}."})

    def _detect_objects_sync(self, image_path: str) -> list:
        self.logger.debug("Running neural network inference...")
        
        if not os.path.exists(image_path):
            self.logger.error(f"Image not found: {image_path}")
            return []
            
        weights_path = "yolov4-tiny.weights"
        config_path = "yolov4-tiny.cfg"
        
        if not os.path.exists(weights_path) or not os.path.exists(config_path):
            self.logger.error("YOLOv4-tiny model files not found. Please download them.")
            return []
            
        net = cv2.dnn.readNet(weights_path, config_path)
        image = cv2.imread(image_path)
        if image is None:
            self.logger.error("Failed to read image.")
            return []
            
        height, width = image.shape[:2]
        
        # Create a blob from the image
        blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        
        # Get output layer names
        layer_names = net.getLayerNames()
        try:
            output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
        except Exception:
            output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
            
        # Run forward pass
        outs = net.forward(output_layers)
        
        detected_classes = []
        conf_threshold = 0.5
        
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > conf_threshold:
                    if class_id < len(self.classes):
                        class_name = self.classes[class_id]
                        detected_classes.append(class_name)
                        
        # Return unique detected classes
        return list(set(detected_classes))
