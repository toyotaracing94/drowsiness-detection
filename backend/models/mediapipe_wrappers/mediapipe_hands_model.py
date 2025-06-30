
import cv2
import numpy as np
from mediapipe.python.solutions import hands

from backend.models.base_model import BaseModelInference
from backend.settings.model_config import HandsConfig
from backend.utils.logging import logging_default


class MediapipeHandsModel(BaseModelInference):
    def __init__(self, model_settings : HandsConfig):
        super().__init__()

        # Load Model configurations first 
        self.load_configurations(model_settings)

        # Initiate the model
        self.load_model(None)

    def load_configurations(self, config : HandsConfig):
        """
        Load the detection of model settings configurations from a configuration JSON file.

        Parameters
        ----------
        path : config
        """

        logging_default.info("Loading hands detection configs and model configuration")

        self.min_detection_confidence = config.min_detection_confidence
        self.min_tracking_confidence = config.min_tracking_confidence

        # Log the configurations loaded
        logging_default.info(
            "Loaded configuration - "
            "Min Tracking Confidence: {min_tracking_confidence:.2f}, Min Detection Confidence: {min_detection_confidence:.2f}",
            min_tracking_confidence=self.min_tracking_confidence,
            min_detection_confidence=self.min_detection_confidence
        )
        return

    def load_model(self, model_path : str):
        self.hands_pose = hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )

    def preprocess(self, image : np.ndarray):
        """
        This function is to preprocess the image before going to the Mediapipe model.
        Process an BGR image and return the image in RGB format

        Parameters
        ----------
        image : np.ndarray
            The image frame of which want to get the face landmark
        """
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    def inference(self, image : np.ndarray, preprocessed : bool = True):
        """
        Perform inference using the MediaPipe Hands model, extract the relevant hand landmarks,
        and return them as a list of tuples.

        Parameters
        ----------
        image : cv2.Mat
            The input image to process.

        Returns
        -------
        list
            A list of lists of hand landmarks, where each inner list contains landmarks of one hand.
            Each landmark contains the (x, y, z) coordinates. To use them, simply loop over the list 
            and access the coordinates.

            Example:
            ```
                [
                    [
                        (0.574, 0.216, 0.012),  # Landmark 0 (wrist)
                        (0.596, 0.312, 0.011),  # Landmark 1 (thumb base)
                        (0.621, 0.398, 0.013),  # Landmark 2 (thumb tip)
                        # Other landmarks...
                    ],  # First hand (e.g., left hand)
                    
                    [
                        (0.486, 0.239, 0.014),  # Landmark 0 (wrist)
                        (0.505, 0.297, 0.018),  # Landmark 1 (thumb base)
                        (0.523, 0.349, 0.016),  # Landmark 2 (thumb tip)
                        # Other landmarks...
                    ]  # Second hand (e.g., right hand)
                ]
            ```
        """
        if not preprocessed:
            image = self.preprocess(image)
        inference_result = self.hands_pose.process(image)
        
        hand_landmarks = []
        if inference_result.multi_hand_landmarks:
            for hand_landmark in inference_result.multi_hand_landmarks:
                hand_landmarks.append([
                    (lm.x, lm.y, lm.z) for lm in hand_landmark.landmark
                ])

        return hand_landmarks