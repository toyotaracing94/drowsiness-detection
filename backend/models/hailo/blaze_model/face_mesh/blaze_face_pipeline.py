import cv2
import numpy as np

from backend.models.base_model import BaseModelInference
from backend.models.hailo.blaze_model.face_mesh.blaze_face_detector import (
    BlazeFaceDetector,
)
from backend.models.hailo.blaze_model.face_mesh.blaze_face_landmark import (
    BlazeFaceLandmark,
)
from backend.models.hailo.hailo_runtime.hailo_inference_engine import (
    HailoInferenceEngine,
)


class BlazeFacePipeline(BaseModelInference):
    def __init__(self, hailo_engine : HailoInferenceEngine):
        super().__init__()

        self.hailo_inference = hailo_engine
        self.hailo_face_detection_model = "hailo_model/hailo8l/hef/face_detection_full_range.hef"
        self.face_detection_model_anchors = "hailo_model/hailo8l/anchors/face_detection_full_option.json"
        self.face_detection_model_inference_config = "hailo_model/hailo8l/configs/face_detection_full_config.json"
        self.hailo_face_landmark_model = "hailo_model/hailo8l/hef/face_landmark.hef"
    
        # Initiate the model pipeline
        self.load_model()
    
    def load_model(self):
        """
        This function is to load the model of the Mediapipe use, which is the Blaze Model.

        Notes
        ---------
        From the official Mediapipe explanation [here](https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/face_mesh.md), 
        truthfully for extracting the face landmark or the Face Mesh, Mediapipe use a solution by consist using
        two real-time deep neural network models that work together: A detector that operates on the full image and computes face locations 
        and a 3D face landmark model that operates on those locations and predicts the approximate 3D surface via regression. 

        That's why in this class, there are two models that will be run to the Hailo Engine.
        For the how detailed, you can see [here](https://learnopencv.com/introduction-to-mediapipe/).
        """
        self.blaze_face_detector = BlazeFaceDetector(
                                    self.hailo_face_detection_model, 
                                    self.face_detection_model_anchors,
                                    self.face_detection_model_inference_config,
                                    self.hailo_inference
                                    )
        self.blaze_face_landmark = BlazeFaceLandmark(
                                    self.hailo_face_landmark_model,
                                    self.hailo_inference
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
    
    def inference(self, image: np.ndarray, preprocessed: bool = True):
        """
        Runs the full BlazeFace pipeline: face detection followed by landmark prediction.

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

        img1, scale1, pad1 = self.blaze_face_detector.resize_pad(image)
        normalized_detections = self.blaze_face_detector.process(img1, False)

        faces_coordinates = []
        if len(normalized_detections) > 0:
            detections = self.blaze_face_detector.denormalize_detections(normalized_detections,scale1,pad1)
            xc, yc, scale, theta = self.blaze_face_detector.detection2roi(detections)

            roi_img, roi_affine, roi_box = self.blaze_face_landmark.extract_roi(image, xc, yc, theta, scale)
            flags, normalized_landmarks = self.blaze_face_landmark.process(roi_img, False)

            landmarks = self.blaze_face_landmark.denormalize_landmarks(normalized_landmarks.copy(), roi_affine.copy())
            original_normalized_landmarks = self.blaze_face_landmark.normalized_landmark_to_orginal_image_space(landmarks.copy(), image.shape)

            for face_landmark in original_normalized_landmarks:
                face_coords = [tuple(pt) for pt in face_landmark]
                faces_coordinates.append(face_coords)
            
        return faces_coordinates
