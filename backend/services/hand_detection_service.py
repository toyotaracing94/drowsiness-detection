
import numpy as np

from backend.domain.dto.hands_detection_result import HandsDetectionResult
from backend.lib.hands_detection import HandsDetection
from backend.lib.socket_trigger import SocketTrigger
from backend.settings.app_config import settings
from backend.settings.model_config import model_settings
from backend.utils.drawing_utils import (
    draw_landmarks,
)
from backend.utils.landmark_constants import (
    HAND_CONNECTIONS,
)
from backend.utils.logging import logging_default


class HandsDetectionService:
    def __init__(self, socket_trigger : SocketTrigger):
        logging_default.info("Initiated Hands Detection Service")

        self.hand_detector = HandsDetection(model_settings.hands, inference_engine=settings.PipelineSettings.inference_engine)
        self.socket_trigger = socket_trigger
    
    def process_frame(self, frame : np.ndarray) -> HandsDetectionResult:
        """
        This function is to process the frame and run models to achieve the
        hands detection. This class service will also hold the logic to count
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
            The image frame of which want to get hands detection service result
        processed_frame : np.ndarray
            The image frame of which we want the draw happens

        Return
        ----------
        processed_frame
            An Image that has been process by the model, with landmark's draw has been
            draw directly to the image
        """
        detection_result = self.hand_detector.detect(frame)
        
        # Draw the annotate in the frame to save them into the result so in task orchestrator can get them
        detection_result.debug_frame = self.draw(frame, detection_result)

        return detection_result
    
    def draw(self, frame : np.ndarray, result : HandsDetectionResult) -> np.ndarray:
        """
        Draws hand landmarks on the processed video frame for each detected hand.

        Parameters
        ----------
        processed_frame : np.ndarray
            The video frame to be annotated with hand landmarks.

        result : HandDetectionResult
            The detection result containing a list of hand states. Each hand state may include
            hand landmarks if a hand is detected in the frame.

        Returns
        -------
        np.ndarray
            The annotated image frame with hand landmarks drawn.
        """
        annotated_frame = frame.copy()
        for hand_state in result.hands:
            if hand_state.hand_landmark is not None:
                draw_landmarks(annotated_frame, hand_state.hand_landmark, HAND_CONNECTIONS, color_points=(0, 0, 0))
        return annotated_frame