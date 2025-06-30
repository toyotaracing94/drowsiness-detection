import numpy as np

from backend.domain.dto.hands_detection_result import HandsDetectionResult, HandState
from backend.models.factory_model import get_hands_pose_model
from backend.settings.model_config import HandsConfig
from backend.utils.landmark_constants import (
    MIDDLE_POINTS,
)


class HandsDetection():
    def __init__(self, model_settings : HandsConfig, inference_engine : str = None):

        # Get the model
        self.model = get_hands_pose_model(model_settings, inference_engine)

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

    def extract_hand_landmark(self, hand_landmark : np.ndarray, hand_connections : list, frame_width : int = 640, frame_height : int = 480):
        """
        Extract the pixel location of the hands from the given hand landmark,
        based on the choosen hand landmark position index 

        Parameters
        ----------
        hand_landmark : list of list of tuple(float, float, float)
            A list where each inner list contains 21 normalized (x, y, z) coordinates of one hand.
        connections: list of index indices of hand landmark
            list of index indices of hand landmark
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

        for idx in hand_connections:
            landmark = hand_landmark[idx]
            x = int(landmark[0] * frame_width)  
            y = int(landmark[1] * frame_height)
            all_hands.append((x,y))

        return all_hands
    
    def detect(self, original_frame : np.ndarray) -> HandsDetectionResult:
        """
        Calculating the result of the detection and draw the results
        """
        results = HandsDetectionResult()

        # Get the landmarks for the hands
        hand_landmarks = self.detect_hand_landmarks(original_frame)

        if hand_landmarks:
            for hand_landmark in hand_landmarks:
                hand_result = HandState()
                hand_result.hand_landmark = hand_landmark

                # No need for getting the each of the coordinates, 
                # Because there is no purpose what's so ever right now
                # so I'm just gonna draw the result

                # Here some example how to get it, have no need for now
                _ = self.extract_hand_landmark(hand_landmark, MIDDLE_POINTS, original_frame.shape[1], original_frame.shape[0])
                results.hands.append(hand_result)
        return results