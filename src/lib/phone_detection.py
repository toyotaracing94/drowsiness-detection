import math

import numpy as np

from src.models.factory_model import get_body_pose_model


class PhoneDetection():
    def __init__(self, model_settings_path : str, model_path: str = None):
        
        self.model = get_body_pose_model(model_settings_path, model_path)

        # Landmarks (for now hardcoded)
        self.right_hand_landmark = [16, 22, 20, 18]
        self.left_hand_landmark = [15, 21, 19, 17]

    def detect_body_pose(self, image : np.ndarray) -> list:
        """
        This funcntion is to process an RGB image and
        returns body pose landmarks on each person captured in the frame

        Parameters
        ----------
        image : np.ndarray
            The image frame of which want to get the body landmark

        Return
        ----------
        results :
            A list of special tuple Class in Mediapipe where it will have 
            pose_landmarks depends on the maximum face detection configuration
            set in the first place
        """
        preprocess_image = self.model.preprocess(image)
        results = self.model.inference(preprocess_image)
        return results
    
    
    def detect_phone_usage(self, pose_landmarks, frame_width : int = 640, frame_height : int = 480, threshold : int = 150):
        """
        Detect if a hand is near the ear based on pose landmarks only. This was achieved by calculating
        the distance from the Wrist of both hand to their respective ear side

        Note: Man idk who the hell write this, but it is so fucking simple, I somehow ask myself
        why they do this to future batch

        Parameters
        ----------
        pose_landmarks :
            The body pose landmark results
        frame_width : int
            The width of image frame
        frame_width : int
            The height of image frame
        threshold : int
            The threshold minimum distance between the wrist and the ear to be categorized
            as `Making Phone Call`

        Return
        ----------
        results :
            True if exceed theshold means driver making phone call, False otherwise.  
        """
        if not pose_landmarks or not pose_landmarks.pose_landmarks:
            return False, None

        lm = pose_landmarks.pose_landmarks.landmark

        # Convert normalized coordinates to pixel coordinates
        def to_pixel(index):
            return int(lm[index].x * frame_width), int(lm[index].y * frame_height)

        left_wrist = to_pixel(15)
        right_wrist = to_pixel(16)
        left_ear = to_pixel(7)
        right_ear = to_pixel(8)

        # Calculate distances
        left_dist = self.calculate_distance(left_wrist, left_ear)
        right_dist = self.calculate_distance(right_wrist, right_ear)

        # Check if either wrist is close to the corresponding ear
        if left_dist < threshold or right_dist < threshold:
            return True, min(left_dist, right_dist)

        return False, None
    
    def calculate_distance(self, point1 : list, point2 : list):
        """
        Calculate the absolute distance (euclidian distance) between two points pixel in single planar

        Parameters
        ----------
        point1 : list
            The first point of feature
        point2 : list
            The second point of feature

        Return
        ----------
            The absolute distance between two points of the pixel in the image planar
        """
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)