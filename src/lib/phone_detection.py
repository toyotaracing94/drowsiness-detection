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
        This function is to process an RGB image and
        returns body pose landmarks on each person captured in the frame

        Parameters
        ----------
        image : np.ndarray
            The image frame of which want to get the body landmark

        Return
        ----------
        list
            A list of pose landmarks, where each item corresponds to one detected person.
            Each landmark is a tuple of normalized (x, y, z) coordinates.
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
        preprocess_image = self.model.preprocess(image)
        pose_landmark = self.model.inference(preprocess_image)
        return pose_landmark
    
    
    def detect_phone_usage(self, pose_landmark, frame_width : int = 640, frame_height : int = 480, threshold : int = 150):
        """
        Detect if a hand is near the ear based on pose landmarks only. This was achieved by calculating
        the distance from the Wrist of both hand to their respective ear side

        Note
        ----
        Man, idk who the hell wrote this, but it's so fucking simple, I somehow want to ask from them (batch 1) developer
        why they do this to future batch. Like man! This is somehow messed up! Like if we just lift our hand next to our ear
        it will be automatically flagged as making a phone call

        Parameters
        ----------
        pose_landmark : list of tuple(float, float, float)
            A list of normalized (x, y, z) body pose landmarks (e.g., as returned from MediaPipe Pose).
        frame_width : int, optional
            Width of the image frame in pixels (default is 640).
        frame_height : int, optional
            Height of the image frame in pixels (default is 480).
        threshold : int, optional
            Distance threshold (in pixels) between the wrist and ear to determine phone usage (default is 150).

        Return
        ----------
        tuple
            A tuple containing:
            - bool: True if phone usage is detected (wrist near ear), False otherwise.
            - float or None: The minimum distance between wrist and ear if phone usage is detected, None otherwise.
        """
        if not pose_landmark:
            return False, None

        # Convert normalized coordinates to pixel coordinates
        def to_pixel(index):
            return int(pose_landmark[index][0] * frame_width), int(pose_landmark[index][1] * frame_height)

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