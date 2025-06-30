from abc import ABC, abstractmethod

import cv2


class BaseModelInference(ABC):
    """
    Abstract Base Model class that defines common methods to be implemented by all models. This is required to be implemented
    if one plan to make another class to encapsulated a model
    """
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def load_model(self, model_path :str):
        """
        Load the machine learning or deep learning model according to the step of the model and their spesific configuration needed
        typically a saved model file (e.g., .h5, .pkl, .pth, etc.) or if using 3rd Party like load the library here

        Parameters
        ----------
        model_path : str
            The file path to the model to be loaded. This should be the full path or relative path to the model file.
        """
        pass

    @abstractmethod
    def preprocess(self, image: cv2.Mat) -> cv2.Mat:
        """
        Custom preprocess function the input frame for inference if needed.
        
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
    def inference(self, image: cv2.Mat, preprocessed : bool = True):
        """
        Performing inference of the model to detect landmarks (e.g., face, hand, pose) based on the provided model.

        This method processes the input image and detects relevant landmarks using a pre-trained model.
        The specific type of landmarks (e.g., face, hand, pose) detected depends on the model being used (e.g., YOLO, ResNet, Mediapipe, etc.)

        Parameters
        ----------
        image : cv2.Mat
            The image that will be inputted to the model in form of cv2 array format
        preprocessed : bool
            Flag to tell the function does the image need to be preprocess or not, if it False then the image will be inputted to the inference stage first
            before going to do prediction/inference stage, if it's True is otherwise

        Return
        ----------
        The detected landmarks (could be face, hand, pose landmarks, etc.). It was up to the models that you are using (Yolo, Resnet, etc)
        for what kind of the result structure will be. This wrapper doesn't responsible for this
        """
        pass

    