import numpy as np
from picamera2 import Picamera2

from backend.hardware.camera.base_camera import BaseCamera
from backend.utils.logging import logging_default


class RPiCamera(BaseCamera):
    def __init__(self):
        logging_default.info("Setting up the camera")
        self.picam2 = Picamera2()
        self.picam2.start()

    def get_capture(self) -> np.ndarray:
        try:
            frame = self.picam2.capture_array()
            if frame is not None:
                return True, frame
            logging_default.warning("PiCamera2 returned None")
        except Exception as e:
            logging_default.error(f"Error capturing frame image from Pi Camera 2: {e}")
        return False, None

    def release(self):
        pass