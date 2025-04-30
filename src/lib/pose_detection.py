import math
import cv2

from mediapipe.python.solutions import pose, hands
import mediapipe.python.solutions.pose as mp_pose

from src.utils.logging import logging_default

class PoseDetection():
    def __init__(self, detection_settings_path: str):
        self.static_image_mode = False
        self.model_complexity = 1
        self.smooth_landmarks = True
        self.enable_segmentation = False
        self.smooth_segmentation = True
        self.min_detection_confidence = 0.5
        self.min_tracking_confidence = 0.5

        self.right_hand_landmark = [16, 22, 20, 18]
        self.left_hand_landmark = [15, 21, 19, 17]

        self.body_pose = pose.Pose(
            self.static_image_mode,
            self.model_complexity,
            self.smooth_landmarks,
            self.enable_segmentation,
            self.smooth_segmentation,
            self.min_detection_confidence,
            self.min_tracking_confidence
        )
        # Hand Landmarker setup (for detailed hand landmarks)
        self.hand_landmarker = hands.Hands(
            static_image_mode=False,
            max_num_hands=2,  # Maximum number of hands detected
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    
    def find_pose(self, image):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.body_pose.process(rgb_image)
        return results
    
    def find_hand_landmarks(self, image):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        hand_results = self.hand_landmarker.process(rgb_image)
        return hand_results
    
    def extract_hand_landmarks2(self, hand_results, frame_width=640, frame_height=480):
        """
        Extract 21 hand landmarks (fingers + palm) in pixel coordinates.
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

    def extract_hand_landmarks(self, pose_landmarks, frame_width=640, frame_height=480):
        """
        Extract landmarks for the hands using specific indices for left and right hand.
        """
        landmarks = pose_landmarks.pose_landmarks.landmark

        # Right hand landmarks (indices based on the input you provided)
        right_hand_indices = self.right_hand_landmark
        left_hand_indices = self.left_hand_landmark

        # Collect pixel coordinates for right hand
        right_hand_pixels = []
        for idx in right_hand_indices:
            lm = landmarks[idx]
            x = int(lm.x * frame_width)
            y = int(lm.y * frame_height)
            right_hand_pixels.append((x, y))

        # Collect pixel coordinates for left hand
        left_hand_pixels = []
        for idx in left_hand_indices:
            lm = landmarks[idx]
            x = int(lm.x * frame_width)
            y = int(lm.y * frame_height)
            left_hand_pixels.append((x, y))

        return right_hand_pixels, left_hand_pixels
    
    def detect_phone_usage(self, pose_landmarks, frame_width=640, frame_height=480, threshold=150):
        """
        Detect if a hand is near the ear based on pose landmarks only.
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
    
    def calculate_distance(self, point1, point2):
        """
        Calculate Euclidean distance between two (x, y) points.
        """
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)