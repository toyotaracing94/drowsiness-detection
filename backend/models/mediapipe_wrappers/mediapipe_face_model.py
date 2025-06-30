
import cv2
import numpy as np
from mediapipe.python.solutions import face_mesh

from backend.models.base_model import BaseModelInference
from backend.settings.model_config import FaceMeshConfig
from backend.utils.logging import logging_default


class MediapipeFaceMeshModel(BaseModelInference):
    def __init__(self, model_settings : FaceMeshConfig):
        super().__init__()

        # Load Model configurations first 
        self.load_configurations(model_settings)

        # Initiate the mdoel
        self.load_model(None)


    def load_configurations(self, config : FaceMeshConfig) -> None:
        """
        Load the detection settings from a configuration JSON file.

        Parameters
        ----------
        config : FaceMeshConfig
            Path to the configuration file containing threshold values for EAR, MAR, and etc.
        """

        logging_default.info("Loading face detection configs and model configuration")
        
        self.static_image_mode = config.static_image_mode
        self.refine_landmarks = config.refine_landmarks
        self.max_number_face_detection = config.max_number_face_detection
        self.min_tracking_confidence = config.min_tracking_confidence
        self.min_detection_confidence = config.min_detection_confidence

        # Log the configurations loaded
        logging_default.info(
            "Loaded configuration - "
            "Static Image Mode: {static_image_mode}, Refine Landmarks: {refine_landmarks}, "
            "Max Number Face Detection: {max_number_face_detection}, "
            "Min Tracking Confidence: {min_tracking_confidence:.2f}, Min Detection Confidence: {min_detection_confidence:.2f}",
            static_image_mode=self.static_image_mode,
            refine_landmarks=self.refine_landmarks,
            max_number_face_detection=self.max_number_face_detection,
            min_tracking_confidence=self.min_tracking_confidence,
            min_detection_confidence=self.min_detection_confidence
        )

        return
    
    def load_model(self, model_path : str):
        """
        This function is to load the model of the Mediapipe face model to the class. 
        """
        self.face_mesh = face_mesh.FaceMesh(
            static_image_mode=self.static_image_mode,
            max_num_faces=self.max_number_face_detection,
            refine_landmarks=self.refine_landmarks,
            min_detection_confidence = self.min_detection_confidence,
            min_tracking_confidence = self.min_tracking_confidence
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

    def inference(self, image : np.ndarray, preprocessed: bool = True):
        """
        Runs the face mesh detection by Mediapipe Library

        Parameters
        ----------
        image : np.ndarray
            Input image (BGR format if preprocessed=False). Expected shape: (H, W, 3).
        preprocessed : bool, optional
            Whether the input image has already been converted to RGB (default is True).

        Returns
        -------
        list[np.ndarray]
            A list of np.ndarrays, each of shape (N, 3), where N is the number of landmarks per face.
            If no faces are detected, returns an empty list.
        """
        if not preprocessed:
            image = self.preprocess(image)

        inference_result = self.face_mesh.process(image)

        faces_coordinates = []
        if inference_result.multi_face_landmarks:
            for face_landmarks in inference_result.multi_face_landmarks:
                face_coordinates = [
                    (lm.x, lm.y, lm.z) for lm in face_landmarks.landmark
                ]
                faces_coordinates.append(face_coordinates)

        return faces_coordinates
