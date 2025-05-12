import json

import cv2
from mediapipe.python.solutions import face_mesh

from src.models.base_model import BaseModelInference
from src.utils.logging import logging_default


class MediapipeFaceMeshModel(BaseModelInference):
    def __init__(self, model_settings : str, model_path : str = None):
        super().__init__()

        # Load Model configurations first 
        self.load_configurations(model_settings)

        # Initiate the mdoel
        self.load_model(model_path)


    def load_configurations(self, path : str) -> None:
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
        self.refine_landmarks = config["refine_landmarks"]
        self.max_number_face_detection = config["max_number_face_detection"]
        self.min_tracking_confidence = config["min_tracking_confidence"]
        self.min_detection_confidence = config["min_detection_confidence"]

         # Log the configurations loaded
        logging_default.info(
            "Loaded configuration - "
            "Static Image Mode: %s, Refine Landmarks: %s, Max Number Face Detection: %d, "
            "Min Tracking Confidence: %.2f, Min Detection Confidence: %.2f",
            self.static_image_mode, self.refine_landmarks, self.max_number_face_detection,
            self.min_tracking_confidence, self.min_detection_confidence
        )

        return
    
    def load_model(self, model_path : str):
        """
        This function is to load the model of the Mediapipe face model to the class. 
        """
        self.face_mesh = face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=self.max_number_face_detection,
            refine_landmarks=True,
            min_detection_confidence = self.min_detection_confidence,
            min_tracking_confidence = self.min_tracking_confidence
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
        Perform the inference, extract the relevant face mesh result landmakrs,
        and return them as a list of tuples match with the according of maximum number faces detected configuration

        Parameters
        ----------
        image : np.ndarray
            The input image to process.
        preprocessed : bool, optional
            If True, the image is already preprocessed; otherwise, preprocessing will be done here.

        Returns
        ----------
        list
            A list of the face mesh landmarks, where if its detected in one frame have more than face, it will return an array of face mesh landmark.
            Each landmark of the body contains the (x, y, z). To use them simply loop of the list then accessing them with index

            Example:
            ```
            [
                [  # Coordinates for Face 1
                    (x1, y1, z1), (x2, y2, z2), ..., (x486, y486, z486)  # All 486 landmarks
                ],
                [  # Coordinates for Face 2
                    (x1, y1, z1), (x2, y2, z2), ..., (x486, y486, z486)  # All 486 landmarks
                ]
            ]
            ```
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
