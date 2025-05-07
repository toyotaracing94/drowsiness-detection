from abc import ABC, abstractmethod

import cv2


class BaseModelInference(ABC):
    """
    Abstract Base Model class that defines common methods to be implemented by all models. This is required!.
    """
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def load_model(self, model_path :str):
        pass

    @abstractmethod
    def preprocess(self, image: cv2.Mat) -> cv2.Mat:
        """
        Custom preprocess the input frame for inference if needed.
        
        Parameters
        ----------
        image : cv2.Mat
            The image that will be inputted to the model in form of cv2 array format

        Return
        ----------
        return: The preprocessed frame.
        """
        pass

    @abstractmethod
    def inference(self, image: cv2.Mat) -> cv2.Mat:
        """
        Detect the landmarks based on the model that are used

        Parameters
        ----------
        image : cv2.Mat
            The image that will be inputted to the model in form of cv2 array format

        Return
        ----------
        return: The detected landmarks (could be face, hand, pose landmarks, etc.). It was up to the models that you are using (Yolo, Resnet, etc)
        """
        pass