import cv2
import os
import numpy as np

from src.utils.logging import logging_default

# Only import PiCamera2 on Linux systems (Raspberry Pi)
if os.name == 'posix':
    try:
        from picamera2 import Picamera2
        PI_CAMERA_AVAILABLE = True
    except ImportError:
        PI_CAMERA_AVAILABLE = False
else:
    PI_CAMERA_AVAILABLE = False


class Camera:
    def __init__(self):
        self.cap = None
        
        # if running on windows
        if os.name == 'nt': 
            self.cap = cv2.VideoCapture(0)
        # if running on linux
        elif os.name == 'posix':
            if PI_CAMERA_AVAILABLE:
                self.picam2 = Picamera2()
                self.picam2.start()
            else:
                self.cap = cv2.VideoCapture(0)

    def get_capture(self) -> tuple[bool, np.ndarray]:
        if PI_CAMERA_AVAILABLE and hasattr(self, "picam2"):
            try:
                frame = self.picam2.capture_array()
                if frame is not None:
                    return True, frame
                else:
                    logging_default.warning("Pi Camera 2 returned None Frame!")
                    return False, None
            except Exception as e:
                logging_default.error(f"Error capturing frame image from Pi Camera 2: {e}")
        elif self.cap:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                return True, frame
            else:
                logging_default.warning("cv2.VideoCapture returned None Frame!")
        else:
            logging_default.error("No Camera available!")
            return False, None

    def release(self):
        if self.cap:
            self.cap.release()
