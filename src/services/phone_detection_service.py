
import numpy as np

from src.domain.dto.phone_detection_result import PhoneDetectionResult
from src.lib.phone_detection import PhoneDetection
from src.lib.socket_trigger import SocketTrigger
from src.utils.logging import logging_default


class PhoneDetectionService:
    def __init__(self, socket_trigger : SocketTrigger, inference_engine : str = None):
        logging_default.info("Initiated Phone Detection Service")

        self.phone_detection = PhoneDetection("config/pose_detection_settings.json", inference_engine=inference_engine)
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
        return detection_result