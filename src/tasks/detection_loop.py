import time

import cv2

from src.services.drowsiness_detection_service import DrowsinessDetectionService
from src.utils.frame_buffer import FrameBuffer


def detection_loop(drowsiness_service : DrowsinessDetectionService, frame_buffer : FrameBuffer):
    while True:
        ret, frame = drowsiness_service.camera.get_capture()
        if not ret:
            time.sleep(0.1)
            continue

        frame = cv2.flip(frame, 1)
        frame_buffer.update_raw(frame)

        processed_frame = drowsiness_service.process_frame(frame)
        frame_buffer.update_processed(processed_frame)

        time.sleep(0.01)