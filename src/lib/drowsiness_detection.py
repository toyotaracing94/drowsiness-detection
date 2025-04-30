import json
import cv2
import math
import numpy as np
from mediapipe.python.solutions import drawing_utils, face_mesh

from src.utils.logging import logging_default

class DrowsinessDetection():
    def __init__(self, detection_settings_path: str, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.face_mesh = face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=2,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.left_eye_landmarks = [33, 160, 158, 133, 153, 144]
        self.right_eye_landmarks = [362, 385, 387, 263, 373, 380]
        self.mouth_landmarks =  [61, 39, 0, 269, 291, 405, 17, 181]
        self.drowsiness_frame_counter = 0
        self.yawn_frame_counter = 0

        
        self.load_configuration(detection_settings_path)

    def load_configuration(self, path : str) -> None:
        logging_default.info("Loading detection configs and model configuration")
        
        with open(path, 'r') as f:
            config = json.load(f)

        self.ear_ratio = config["eye_aspect_ratio_threshold"]
        self.ear_consec_frames = config["eye_aspect_ratio_consec_frames"]
        self.mouth_aspect_ratio_threshold = config["mouth_aspect_ration_threshold"]
        self.mouth_aspect_ratio_consec_frames = config["mouth_aspect_ration_consec_frames"]

        logging_default.info(
            "Loaded config - EAR: %.2f, EAR Frames: %d, MAR: %.2f, MAR Frames: %d",
            self.ear_ratio, self.ear_consec_frames, self.mouth_aspect_ratio_threshold, self.mouth_aspect_ratio_consec_frames
        )
        return None


    def detect_landmarks(self, image: np.ndarray):
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)
        return results

    def extract_mouth_landmarks(self, face_landmarks, frame_width = 640, frame_height = 480):
        """
        Extract the pixel location of the mouth landmark from the given face landmark
        """
        mouth_pixels = []

        for idx in self.mouth_landmarks:
            landmark = face_landmarks.landmark[idx]
            x = int(landmark.x * frame_width)  
            y = int(landmark.y * frame_height)
            mouth_pixels.append((x,y))
        
        return mouth_pixels
    
    def extract_eye_landmarks(self, face_landmarks, frame_width = 640, frame_height = 480):
        """
        Extract the pixel location of the left-eye landmark and right-eye landmark from the given face landmark
        """
        left_eye_pixels = []
        right_eye_pixels = []

        for idx in self.left_eye_landmarks:
            landmark = face_landmarks.landmark[idx]
            x = int(landmark.x * frame_width)
            y = int(landmark.y * frame_height)
            left_eye_pixels.append((x, y))

        for idx in self.right_eye_landmarks:
            landmark = face_landmarks.landmark[idx]
            x = int(landmark.x * frame_width)
            y = int(landmark.y * frame_height)
            right_eye_pixels.append((x, y))
        
        return left_eye_pixels, right_eye_pixels

    def calculate_ear(self, left_eye:list, right_eye:list):
        """
        Calculate Eye Aspect Ratio (EAR) using the left and right eye landmarks
        Formula for EAR is: EAR = (d1 + d2) / (2.0 * d3)
        where d1, d2, and d3 are distances between key points on the eye landmarks.

        Reference : 
         - https://vision.fe.uni-lj.si/cvww2016/proceedings/papers/05.pdf
        """
        # Calculate distances between points
        d1 = self.euclidean_distance(left_eye[1], left_eye[5])      # Vertical distance
        d2 = self.euclidean_distance(right_eye[2], right_eye[4])    # Vertical distance
        d3 = self.euclidean_distance(left_eye[0], left_eye[3])      # Horizontal distance

        ear = (d1 + d2) / (2.0 * d3)
        logging_default.debug("Ear Calculation: ", ear)

        return ear
    
    def calculate_mar(self, mouth:list):
        """
        Calculate Mouth Aspect Ratio (MAR) using the mouth of the lips landmark
        consist of 8 landmark

        Reference
         - https://www.mdpi.com/2313-433X/9/5/91
        """
        A = self.euclidean_distance(mouth[1], mouth[7])
        B = self.euclidean_distance(mouth[2], mouth[6])
        C = self.euclidean_distance(mouth[3], mouth[5])
        D = self.euclidean_distance(mouth[0], mouth[4])

        mar = (A + B + C) / (2.0 * D)
        return mar

    def euclidean_distance(self, point1, point2):
        """
        Calculate the absolute distance (euclidian distance) between two points in single planar
        """
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

    def check_drowsiness(self, ear : float) -> bool:
        if ear < self.ear_ratio:
            self.drowsiness_frame_counter += 1
            if self.drowsiness_frame_counter >= self.ear_consec_frames:
                return True
        else:
            self.drowsiness_frame_counter = 0
        return False
    
    def check_yawning(self, mar : float) -> bool:
        if mar > self.mouth_aspect_ratio_threshold:
            self.yawn_frame_counter +=1
            if self.yawn_frame_counter >= self.mouth_aspect_ratio_threshold:
                return True
        else:
            self.yawn_frame_counter = 0
        return False
