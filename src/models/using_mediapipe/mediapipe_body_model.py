import json

import cv2
from mediapipe.python.solutions import pose

from src.models.base_model import BaseModelInference
from src.utils.logging import logging_default


class MediapipeBodyPoseModel(BaseModelInference):
    def __init__(self, model_settings : str, model_path : str = None):
        super().__init__()

        # Load Model configurations first 
        self.load_configurations(model_settings)

        # Initiate the model
        self.load_model(model_path)

    def load_configurations(self, path : str):
        """
        Load the detection settings from a configuration JSON file.

        Parameters
        ----------
        path : str
            Path to the configuration file containing threshold values for EAR, MAR, and etc.
        """

        logging_default.info("Loading pose detection configs and model configuration")

        with open(path, 'r') as f:
            config = json.load(f)
        
        self.static_image_mode = config["static_image_mode"]
        self.smooth_segmentation = config["smooth_segmentation"]
        self.enable_segmentation = config["enable_segmentation"]
        self.smooth_landmarks = config["smooth_landmarks"]
        self.min_tracking_confidence = config["min_tracking_confidence"]
        self.min_detection_confidence = config["min_detection_confidence"]

        # Log the configurations loaded
        logging_default.info(
            "Loaded configuration - "
            "Static Image Mode: %s, Smooth Segmentation: %s, Enable Segmentation: %s, "
            "Smooth Landmarks: %s, Min Tracking Confidence: %.2f, Min Detection Confidence: %.2f",
            self.static_image_mode, self.smooth_segmentation, self.enable_segmentation, 
            self.smooth_landmarks, self.min_tracking_confidence, self.min_detection_confidence
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
    
    def preprocess(self, image : cv2.Mat):
        """
        This function is to preprocess the image before going to the Mediapipe model.
        Process an BGR image and return the image in RGB format

        Parameters
        ----------
        image : np.ndarray
            The image frame of which want to get the face landmark
        """
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    def inference(self, image, preprocessed = True):
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