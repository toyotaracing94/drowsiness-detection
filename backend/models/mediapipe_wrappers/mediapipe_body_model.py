
import cv2
import numpy as np
from mediapipe.python.solutions import pose

from backend.models.base_model import BaseModelInference
from backend.settings.model_config import PoseConfig
from backend.utils.logging import logging_default


class MediapipeBodyPoseModel(BaseModelInference):
    def __init__(self, model_settings : PoseConfig):
        super().__init__()

        # Load Model configurations first 
        self.load_configurations(model_settings)

        # Initiate the model
        self.load_model(None)

    def load_configurations(self, config : PoseConfig):
        """
        Load the detection settings from a configuration JSON file.

        Parameters
        ----------
        config : str
            configuration for pose model
        """

        logging_default.info("Loading pose detection configs and model configuration")
        self.static_image_mode = config.static_image_mode
        self.smooth_segmentation = config.smooth_segmentation
        self.enable_segmentation = config.enable_segmentation
        self.smooth_landmarks = config.smooth_landmarks
        self.min_tracking_confidence = config.min_tracking_confidence
        self.min_detection_confidence = config.min_detection_confidence

        # Log the configurations loaded
        logging_default.info(
            "Loaded configuration - "
            "Static Image Mode: {static_image_mode}, Smooth Segmentation: {smooth_segmentation}, "
            "Enable Segmentation: {enable_segmentation}, Smooth Landmarks: {smooth_landmarks}, "
            "Min Tracking Confidence: {min_tracking_confidence:.2f}, Min Detection Confidence: {min_detection_confidence:.2f}",
            static_image_mode=self.static_image_mode,
            smooth_segmentation=self.smooth_segmentation,
            enable_segmentation=self.enable_segmentation,
            smooth_landmarks=self.smooth_landmarks,
            min_tracking_confidence=self.min_tracking_confidence,
            min_detection_confidence=self.min_detection_confidence
        )

        return

    def load_model(self, model_path : str):
        """
        This function is to load the model of the Mediapipe body model to the class. 
        """
        self.body_pose = pose.Pose(
            self.static_image_mode,
            1,
            self.smooth_landmarks,
            self.enable_segmentation,
            self.smooth_segmentation,
            self.min_detection_confidence,
            self.min_tracking_confidence
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
    
    def inference(self, image : np.ndarray, preprocessed = True):
        """
        Perform the inference, extract the relevant body pose landmarks, 
        and return them as a list of tuples.

        Parameters
        ----------
        image : np.ndarray
            The input image to process.
        preprocessed : bool, optional
            If True, the image is already preprocessed; otherwise, preprocessing will be done here.

        Returns
        -------
        list
            A list of body landmarks, where each landmark contains the (x, y, z) coordinates.
            To use them, simply loop over the list and access the coordinates.

            Example:
            ```
                [
                    (0.574, 0.216, 0.012),  # Landmark 0 (right shoulder)
                    (0.596, 0.312, 0.011),  # Landmark 1 (right elbow)
                    (0.621, 0.398, 0.013),  # Landmark 2 (right wrist)
                    # Other landmarks...
                ]
            ```
        """
        if not preprocessed:
            image = self.preprocess(image)
            
        inference_result = self.body_pose.process(image)

        body_landmarks = []
        if inference_result.pose_landmarks:
            body_landmarks = [
                (lm.x, lm.y, lm.z) for lm in inference_result.pose_landmarks.landmark
            ]
        return body_landmarks