
import cv2
import numpy as np

from backend.domain.dto.phone_detection_result import PhoneDetectionResult
from backend.lib.phone_detection import PhoneDetection
from backend.lib.socket_trigger import SocketTrigger
from backend.settings.app_config import settings
from backend.settings.detection_config import detection_settings
from backend.settings.model_config import model_settings
from backend.utils.drawing_utils import (
    draw_landmarks,
)
from backend.utils.landmark_constants import (
    BODY_POSE_FACE_CONNECTIONS,
)
from backend.utils.logging import logging_default


class PhoneDetectionService:
    def __init__(self, socket_trigger : SocketTrigger):
        logging_default.info("Initiated Phone Detection Service")

        self.phone_detection = PhoneDetection(model_settings.pose, detection_settings.phone_detection , inference_engine=settings.PipelineSettings.inference_engine)
        self.socket_trigger = socket_trigger
    
    def process_frame(self, frame : np.ndarray) -> PhoneDetectionResult:
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
        detection_result = self.phone_detection.detect(frame)

        # Draw the annotate in the frame to save them into the result so in task orchestrator can get them
        detection_result.debug_frame = self.draw(frame, detection_result)
        
        return detection_result
    
    def draw(self, frame : np.ndarray, result : PhoneDetectionResult) -> np.ndarray:
        """
        Draws visual annotations on the processed video frame for phone usage detection,
        including call status, estimated distance to the person, and body pose landmarks.

        Parameters
        ----------
        frame : np.ndarray
            The video frame (as a NumPy array) to annotate with phone detection results.

        result : PhoneDetectionResult
            The result object containing phone usage detection data. Each item in `result.detection`
            may include the calling status, distance estimate, and body pose landmarks.

        Returns
        -------
        np.ndarray
            The annotated image frame with phone usage indicators and pose visualizations.
        """
        annotated_frame = frame.copy()

        for phone_state in result.detection:
            # Draw the annotated text marking it's calling
            if phone_state.is_calling:
                cv2.putText(annotated_frame, "Making a phone call", (50, 150), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Draw the distance between wrist and the ear
            if phone_state.distance is not None:
                cv2.putText(annotated_frame, f"Distance: {phone_state.distance:.2f}", 
                            (20, annotated_frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

            # Draw the body landmark of the face
            if phone_state.body_landmark is not None:
                draw_landmarks(annotated_frame, phone_state.body_landmark, BODY_POSE_FACE_CONNECTIONS, 
                            color_lines=(255, 0, 0), color_points=(0, 0, 255))
        return annotated_frame