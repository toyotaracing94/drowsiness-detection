import json
import time

import cv2

from src.hardware.camera.base_camera import BaseCamera
from src.services.drowsiness_detection_service import DrowsinessDetectionService
from src.services.hand_detection_service import HandsDetectionService
from src.services.phone_detection_service import PhoneDetectionService
from src.utils.drawing_utils import draw_fps
from src.utils.frame_buffer import FrameBuffer
from src.utils.logging import logging_default


class DetectionTask:
    def __init__(self, pipeline_config : str):
        self.load_configuration(pipeline_config)

    def load_configuration(self, path : str):
        with open(path, 'r') as f:
            config = json.load(f)

        self.drowsiness_model_run = config["drowsiness_model_run"]
        self.phone_detection_model_run = config["phone_detection_model_run"]
        self.hands_detection_model_run = config["hands_detection_model_run"]

        logging_default.info(
            "Loaded config - drowsiness_model_run: %s, phone_detection_model_run: %s, hands_detection_model_run: %s",
            self.drowsiness_model_run, self.phone_detection_model_run, self.hands_detection_model_run
        )

    def detection_loop(self, drowsiness_service : DrowsinessDetectionService, 
                   phone_detection_service : PhoneDetectionService,
                   hand_detection_service : HandsDetectionService,
                   camera : BaseCamera, frame_buffer : FrameBuffer):
        """
        This function serves as the main inference of the loop of the machine learning models.

        Parameters
        ----------
        drowsiness_service (DrowsinessDetectionService):
            The service responsible for detecting driver drowsiness and triggering alerts.
        phone_detection_service (PhoneDetectionService):
            The service used to detect if the driver is using a phone while driving.
        hand_detection_service (HandsDetectionService):
            The service used to detect hand presence or gestures.
        camera (BaseCamera):
            The camera interface used to capture frames from the video stream.
        frame_buffer (FrameBuffer):
            Shared object for storing the latest raw and processed frames 
            for access by other components (e.g., HTTP endpoints).
        
        Notes
        ----------
        - This method is intended to be run in a background thread.
        - Detection modules are only invoked if enabled in the config (pipeline_settings.json).
        - To prevent CPU overload, the loop includes a short sleep (~10ms) between iterations.
        """
    
        self.prev_time = time.time()

        while True:
            ret, original_frame = camera.get_capture()
            if not ret:
                time.sleep(0.01)
                continue
            
            original_frame = cv2.flip(original_frame, 1)
            processed_frame = original_frame.copy()

            # Save the frame to the shared global instance
            frame_buffer.update_raw(original_frame)

            # Run them into detection service
            if self.drowsiness_model_run:
                processed_frame = drowsiness_service.process_frame(original_frame, processed_frame)
            if self.phone_detection_model_run:
                processed_frame = phone_detection_service.process_frame(original_frame, processed_frame)
            if self.hands_detection_model_run:
                processed_frame = hand_detection_service.process_frame(original_frame, processed_frame)

            # Draw the FPS
            # FPS calculation
            current_time = time.time()
            fps = 1 / (current_time - self.prev_time)
            self.prev_time = current_time
            draw_fps(processed_frame, f"FPS : {fps:.2f}")

            # Save the processed 
            frame_buffer.update_processed(processed_frame)

            time.sleep(0.01)