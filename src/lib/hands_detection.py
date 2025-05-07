import numpy as np

from src.models.factory_model import get_hands_pose_model


class HandsDetection():
    def __init__(self, model_settings_path : str, model_path: str = None):

        # Get the model
        self.model = get_hands_pose_model(model_settings_path, model_path)

    def extract_hand_landmarks(self, hand_results, frame_width : int = 640, frame_height : int = 480):
        """
        Extract the 21 pixel location of the hands from the given hand landmark,
        based on the choosen hand landmark position index 

        Parameters
        ----------
        hand_results : np.ndarray
            The hand lanmark results
        frame_width : int
            The width of image frame
        frame_width : int
            The height of image frame

        Return
        ----------
        results :
            The list of pixels(x,y) of the hand landmark
        """
        all_hands = []

        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                hand_pixels = []
                for lm in hand_landmarks.landmark:
                    x = int(lm.x * frame_width)
                    y = int(lm.y * frame_height)
                    hand_pixels.append((x, y))
                all_hands.append(hand_pixels)
        
        return all_hands


    def detect_hand_landmarks(self, image : np.ndarray) -> list:
        """
        This function is to process an RGM image and
        returns only the mesh of the hand (both hands) total of 21 landmarks
        using the Hands Mediapipe Object

        Parameters
        ----------
        image : np.ndarray
            The image frame of which want to get the hand landmark
            
        Return
        ----------
        results :
            A list of special tuple Class in Mediapipe where it will have 
            multi_hand_landmarks
        """
        preprocess_image = self.model.preprocess(image)
        hand_results = self.model.inference(preprocess_image)
        return hand_results