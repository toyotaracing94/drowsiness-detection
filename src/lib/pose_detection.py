import math
import cv2
import json
import numpy as np

from mediapipe.python.solutions import pose, hands
import mediapipe.python.solutions.pose as mp_pose

from src.utils.logging import logging_default

class PoseDetection():
    def __init__(self, pose_detection_settings_path: str):

        # Load configurations first
        self.load_configurations(pose_detection_settings_path)

        # Landmarks (for now hardcoded)
        self.right_hand_landmark = [16, 22, 20, 18]
        self.left_hand_landmark = [15, 21, 19, 17]

        # Body Pose Model
        self.body_pose = pose.Pose(
            self.static_image_mode,
            1,
            self.smooth_landmarks,
            self.enable_segmentation,
            self.smooth_segmentation,
            self.min_detection_confidence,
            self.min_tracking_confidence
        )

        # Hand Landmarker model (for detailed hand landmarks)
        self.hand_landmarker = hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
    
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
        self.smooth_segmentation = config["smooth_segmentation"]
        self.enable_segmentation = config["enable_segmentation"]
        self.smooth_landmarks = config["smooth_landmarks"]
        self.min_tracking_confidence = config["min_tracking_confidence"]
        self.min_detection_confidence = config["min_detection_confidence"]


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
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.body_pose.process(rgb_image)
        return results
    
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
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        hand_results = self.hand_landmarker.process(rgb_image)
        return hand_results
    
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

    def extract_hand_landmarks_from_body_pose(self, body_pose, frame_width : int = 640, frame_height : int = 480):
        """
        Extract landmarks for the hands using specific indices for left and right hand.
        where the landmark is taken from the body pose landmark

        Parameters
        ----------
        body_pose :
            The body pose landmark results
        frame_width : int
            The width of image frame
        frame_width : int
            The height of image frame

        Return
        ----------
        results :
            The list of pixels(x,y) of the hand landmark based on the body landmark
        """
        body_landmark = body_pose.pose_landmarks.landmark

        # Collect pixel coordinates for right hand
        right_hand_pixels = []
        for idx in self.right_hand_landmark:
            lm = body_landmark[idx]
            x = int(lm.x * frame_width)
            y = int(lm.y * frame_height)
            right_hand_pixels.append((x, y))

        # Collect pixel coordinates for left hand
        left_hand_pixels = []
        for idx in self.left_hand_landmark:
            lm = body_landmark[idx]
            x = int(lm.x * frame_width)
            y = int(lm.y * frame_height)
            left_hand_pixels.append((x, y))

        return right_hand_pixels, left_hand_pixels
    
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