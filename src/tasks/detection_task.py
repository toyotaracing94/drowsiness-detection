import time

import cv2
import numpy as np
import os

from src.hardware.camera.base_camera import BaseCamera
from src.services.drowsiness_detection_service import DrowsinessDetectionService
from src.services.hand_detection_service import HandsDetectionService
from src.services.phone_detection_service import PhoneDetectionService
from src.settings.app_config import PipelineSettings
from src.utils.drawing_utils import (
    draw_fps,
    draw_timestamp,
)
from src.utils.frame_buffer import FrameBuffer
from src.utils.logging import logging_default


class DetectionTask:
    def __init__(self, pipeline_config : PipelineSettings):
        self.load_configuration(pipeline_config)

    def load_configuration(self, config : PipelineSettings):
        self.drowsiness_model_run = config.drowsiness_model_run
        self.phone_detection_model_run = config.phone_detection_model_run
        self.hands_detection_model_run = config.hands_detection_model_run

        logging_default.info(
            "Loaded config - drowsiness_model_run: {drowsiness_model_run}, phone_detection_model_run: {phone_detection_model_run}, hands_detection_model_run: {hands_detection_model_run}",
            drowsiness_model_run=self.drowsiness_model_run,
            phone_detection_model_run=self.phone_detection_model_run,
            hands_detection_model_run=self.hands_detection_model_run
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
            
            # Don't flip when in Raspberry Pi or in Linux, as it use 3rd Party Camera rather Built-in Camera
            if os.name == "nt":
                original_frame = cv2.flip(original_frame, 1)

            processed_frame = original_frame.copy()
            # Draw the result
            debug_frames = []

            # Draw timestamp on original frame
            draw_timestamp(original_frame)

            # Run them into detection service
            drowsiness_detection_result = None
            phone_detection_result = None
            hands_detection_result = None

            if self.drowsiness_model_run:
                drowsiness_detection_result = drowsiness_service.process_frame(original_frame)
                debug_frames.append(drowsiness_detection_result.debug_frame)

            if self.phone_detection_model_run:
                phone_detection_result = phone_detection_service.process_frame(original_frame)
                debug_frames.append(phone_detection_result.debug_frame)

            if self.hands_detection_model_run:
                hands_detection_result = hand_detection_service.process_frame(original_frame)
                debug_frames.append(hands_detection_result.debug_frame)

            # Draw the result
            if drowsiness_detection_result:
                processed_frame = drowsiness_service.draw(processed_frame, drowsiness_detection_result, False)
            if phone_detection_result:
                processed_frame = phone_detection_service.draw(processed_frame, phone_detection_result)
            if hands_detection_result:
                processed_frame = hand_detection_service.draw(processed_frame, hands_detection_result)

            # Process the debug frame
            debug_frame = self.combine_debug_frames(debug_frames)

            # Draw the FPS
            # FPS calculation
            current_time = time.time()
            fps = 1 / (current_time - self.prev_time)
            self.prev_time = current_time
            draw_fps(processed_frame, f"FPS : {fps:.2f}")

            # Draw timestamp on processed frame
            draw_timestamp(processed_frame)

            # Save the frame to the shared global instance
            frame_buffer.update_raw(original_frame)
            frame_buffer.update_processed(processed_frame)
            frame_buffer.update_debug(debug_frame)

            # Exposing facial metrics to websocket communication
            if drowsiness_detection_result.faces:
                face = drowsiness_detection_result.faces[0]
                frame_buffer.update_facial_metrics(face.ear, face.mar, face.is_drowsy, face.is_yawning)
            else:
                frame_buffer.update_facial_metrics(0, 0, False, False)

            # Exposing recent detected event to websocket communication
            if drowsiness_detection_result:
                frame_buffer.update_drowsiness_event_recent(drowsiness_detection_result.drowsiness_event, drowsiness_detection_result.yawning_event)

            time.sleep(0.01)

    def combine_debug_frames(self, frames: list[np.ndarray], concat_axis: str = "horizontal") -> np.ndarray:
        """
        Combines a list of debug frames into a single image.

        Parameters:
            frames (List[np.ndarray]): List of debug frames to combine.
            concat_axis (str): 'horizontal' or 'vertical' for stacking direction.

        Returns:
            np.ndarray or None: Combined debug frame or None if input is empty or failed.
        """
        if not frames:
            return None
        
        try:
            if concat_axis == "horizontal":
                target_height = min(f.shape[0] for f in frames)
                resized = [cv2.resize(f, (int(f.shape[1] * target_height / f.shape[0]), target_height)) for f in frames]
                return cv2.hconcat(resized)
            if concat_axis == "vertical":
                target_width = min(f.shape[1] for f in frames)
                resized = [cv2.resize(f, (target_width, int(f.shape[0] * target_width / f.shape[1]))) for f in frames]
                return cv2.vconcat(resized)
            raise ValueError("concat_axis must be 'horizontal' or 'vertical'")
        except Exception as e:
            logging_default.warning(f"Failed to combine debug frames: {e}")
            return None