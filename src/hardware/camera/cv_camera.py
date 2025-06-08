import cv2
import numpy as np

from src.hardware.camera.base_camera import BaseCamera
from src.utils.logging import logging_default


class CVCamera(BaseCamera):
    def __init__(self, cam_index=0):
        self.cap = cv2.VideoCapture(cam_index)

    def get_capture(self) -> np.ndarray:
        ret, frame = self.cap.read()
        if ret and frame is not None:
            return True, frame
        logging_default.warning("cv2.VideoCapture returned None Frame!")
        return False, None

    def release(self):
        if self.cap:
            logging_default.info("Releasing camera device!")
            self.cap.release()