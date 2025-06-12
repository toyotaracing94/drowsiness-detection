
import numpy as np

from src.domain.dto.hands_detection_result import HandsDetectionResult
from src.lib.hands_detection import HandsDetection
from src.lib.socket_trigger import SocketTrigger
from src.utils.logging import logging_default


class HandsDetectionService:
    def __init__(self, socket_trigger : SocketTrigger, inference_engine : str = None):
        logging_default.info("Initiated Hands Detection Service")

        self.hand_detector = HandsDetection("config/pose_detection_settings.json", inference_engine=inference_engine)
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
        return detection_result