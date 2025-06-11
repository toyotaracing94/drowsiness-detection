
import cv2
import numpy as np

from src.lib.phone_detection import PhoneDetection
from src.lib.socket_trigger import SocketTrigger
from src.utils.drawing_utils import (
    draw_landmarks,
)
from src.utils.landmark_constants import BODY_POSE_FACE_CONNECTIONS
from src.utils.logging import logging_default


class PhoneDetectionService:
    def __init__(self, socket_trigger : SocketTrigger, inference_engine : str = None):
        logging_default.info("Initiated Phone Detection Service")

        self.phone_detection = PhoneDetection("config/pose_detection_settings.json", inference_engine=inference_engine)
        self.socket_trigger = socket_trigger
    
    def process_frame(self, frame : np.ndarray, processed_frame : np.ndarray) -> np.ndarray:
        """
        This function is to process the frame and run models to achieve the
        phone detection. This class service will also hold the logic to count
        how time passed for the result of the model based on the `intent-wrapper` of the model

        Note
        ----------
        So the way it works is like this
        
        Workflow:  
            Controller --> Service --> Intent Use Case Wrapper --> Model [frame requested for processing]
            Controller <-- Service <-- Intent Use Case Wrapper <-- Model [results returned]

        Parameters
        ----------
        frame : np.ndarray
            The image frame of which want to get phone detection service result
        processed_frame : np.ndarray
            The image frame of which we want the draw happens

        Return
        ----------
        processed_frame
            An Image that has been process by the model, with landmark's draw has been
            draw directly to the image
        """
        # Get the landmarks for the body
        body_landmark = self.phone_detection.detect_body_pose(frame)

        # Phone usage detection feature get from pose information
        if body_landmark:      
            is_calling, distance = self.phone_detection.detect_phone_usage(
                body_landmark, frame.shape[1], frame.shape[0]
            )

            if is_calling:
                cv2.putText(processed_frame, "Making a phone call", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            if distance is not None:
                cv2.putText(processed_frame, f"Distance: {distance:.2f}", (20, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

            # Drawing the result
            draw_landmarks(processed_frame, body_landmark, BODY_POSE_FACE_CONNECTIONS, color_lines=(255,0,0), color_points=(0,0,255))

        return processed_frame