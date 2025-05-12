import numpy as np

from src.models.factory_model import get_hands_pose_model


class HandsDetection():
    def __init__(self, model_settings_path : str, model_path: str = None):

        # Get the model
        self.model = get_hands_pose_model(model_settings_path, model_path)

    def detect_hand_landmarks(self, image : np.ndarray) -> list:
        """
        This function is to process an RGB image and returns the hands landmarks on each detected hand.

        This method preprocesses the input image, performs inference using the internal model,
        and returns the normalized 3D coordinates (x, y, z) of detected hand landmarks.
    
        Parameters
        ----------
        image : np.ndarray
            The RGB image frame in which to detect hand landmarks.
            
        Returns
        -------
        list of list of tuple(float, float, float)
            A list where each element corresponds to a detected hand.
            Each inner list contains 21 tuples representing (x, y, z) normalized coordinates of hand landmarks.

            Example:
            ```
            [
                [  # First hand
                    (0.574, 0.216, 0.012),  # Wrist
                    (0.596, 0.312, 0.011),  # Thumb base
                    ...
                ],
                [  # Second hand
                    ...
                ]
            ]
            ```
        """
        preprocess_image = self.model.preprocess(image)
        hand_results = self.model.inference(preprocess_image)
        return hand_results

    def extract_hand_landmark(self, hand_landmarks, frame_width : int = 640, frame_height : int = 480):
        """
        Extract all the 21 pixel location of the hands from the given hand landmark,
        based on the choosen hand landmark position index 

        Parameters
        ----------
        hand_landmarks : list of list of tuple(float, float, float)
            A list where each inner list contains 21 normalized (x, y, z) coordinates of one hand.
        frame_width : int, optional
            The width of the image frame in pixels. Default is 640.
        frame_height : int, optional
            The height of the image frame in pixels. Default is 480.

        Return
        ----------
        list of list of tuple(int, int)
            The list of pixels(x,y) of the hand landmark
        """
        all_hands = []

        for hand_landmark in hand_landmarks:
            hand_pixels = []
            for lm in hand_landmark:
                x = int(lm[0] * frame_width)
                y = int(lm[1] * frame_height)
                hand_pixels.append((x, y))
            all_hands.append(hand_pixels)
        
        return all_hands
