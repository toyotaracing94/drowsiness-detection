import json
import math

import cv2
import numpy as np

from src.domain.dto.drowsiness_detection_result import (
    DrowsinessDetectionResult,
    FaceDrowsinessState,
)
from src.models.factory_model import get_face_model
from src.utils.landmark_constants import (
    HEAD_POSE_POINTS,
    LEFT_EYE_POINTS,
    OUTER_LIPS_POINTS,
    RIGHT_EYE_POINTS,
)
from src.utils.logging import logging_default


class DrowsinessDetection():
    def __init__(self, model_settings_path : str, model_path: str = None, inference_engine : str = None):
        
        # Load Configurations
        self.load_configuration(model_settings_path)

        # Get the model
        self.model = get_face_model(model_settings_path, model_path, inference_engine)

        # Counter for the Yawn and Drowsiness
        self.drowsiness_frame_counter = 0
        self.yawn_frame_counter = 0

    def load_configuration(self, path : str) -> None:
        """
        Load the detection settings from a configuration JSON file.

        Parameters
        ----------
        path : str
            Path to the configuration file containing threshold values for EAR, MAR, and etc.

        """
        logging_default.info(f"Loading drowsiness detection configs and model configuration from {path}")
        
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
        return

    def detect_face_landmarks(self, image: np.ndarray) -> list:
        """
        This function is to process an RGB image and returns the face landmarks on each detected face.

        Parameters
        ----------
        image : np.ndarray
            The image frame of which want to get the face landmark

        Return
        ----------
        face_landmarks :
            A list of lists of face landmark, where each inner list contains the landmarks of a detected face.
            Each landmark contains the (x, y, z) coordinates. To access the coordinates, simply loop through 
            the list and use item.x, item.y, or item.z with index array like item[0], item[1], item[2].

            Example:
            ```
            [
                [  # Coordinates for Face 1
                    (x1, y1, z1), (x2, y2, z2), ..., (x486, y486, z486)  # All 486 landmarks
                ],
                [  # Coordinates for Face 2
                    (x1, y1, z1), (x2, y2, z2), ..., (x486, y486, z486)  # All 486 landmarks
                ]
            ]
            ```
        """
        processed_image = self.model.preprocess(image)
        face_landmarks = self.model.inference(processed_image)
        return face_landmarks

    def extract_mouth_landmark(self, face_landmark, mouth_connections : list, frame_width : int = 640, frame_height : int = 480) -> list[tuple[int, int]]:
        """
        Extract the pixel location (x,y) of the selected mouth landmark position from the given a face landmark,
        based on the choosen mouth landmark position index.

        Parameters
        ----------
        face_landmark : list of tuple(float, float, float)
            A list of 3D landmarks (x, y, z) for a single detected face. Each landmark is a tuple of normalized coordinates.
        frame_width : int, optional
            The width of the image frame (default is 640).
        frame_height : int, optional
            The height of the image frame (default is 480).

        Return
        ----------
        list of tuple(int, int)
            A list of (x, y) pixel positions corresponding to the selected mouth landmarks, scaled to the image size.
        """
        mouth_pixels = []

        for idx in mouth_connections:
            landmark = face_landmark[idx]
            x = int(landmark[0] * frame_width)  
            y = int(landmark[1] * frame_height)
            mouth_pixels.append((x,y))
        
        return mouth_pixels
    
    def extract_eye_landmark(self, face_landmark, left_eye_connections : list, right_eye_connections : list,
                             frame_width : int = 640, frame_height : int = 480) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
        """
        Extract the pixel location (x,y) of the left-eye landmark and right-eye landmark from the given face landmark,
        based on the choosen left-eye landmark and right-eye landmark position index 

        Parameters
        ----------
        face_landmark : list of tuple(float, float, float)
            A list of normalized (x, y, z) landmarks for a single detected face.
        frame_width : int, optional
            Width of the image frame in pixels (default is 640).
        frame_height : int, optional
            Height of the image frame in pixels (default is 480).

        Return
        ----------
        tuple of list of tuple(int, int)
            A tuple containing:
            - A list of (x, y) pixel coordinates for left eye landmarks.
            - A list of (x, y) pixel coordinates for right eye landmarks.
        """
        left_eye_pixels = []
        right_eye_pixels = []

        for idx in left_eye_connections:
            landmark = face_landmark[idx]
            x = int(landmark[0] * frame_width)
            y = int(landmark[1] * frame_height)
            left_eye_pixels.append((x, y))

        for idx in right_eye_connections:
            landmark = face_landmark[idx]
            x = int(landmark[0] * frame_width)
            y = int(landmark[1] * frame_height)
            right_eye_pixels.append((x, y))
        
        return (left_eye_pixels, right_eye_pixels)
    
    def estimate_head_pose(self, image : np.ndarray, face_landmark, connections : list):
        """
        This function is to Estimate head pose (yaw, pitch, roll) from 
        6 points of face landmarks from Mediapipe by converting the image coordinates
        to the world coordinate using OpenCV SolvePnp.

        Notes
        ---------
        In my Opinion, the translation of the camera frame to the world frame coordinate
        is related the with inverse of Projection Matrix on the Camera Model. See this
        [reference](https://www.cs.cmu.edu/~16385/s17/Slides/11.1_Camera_matrix.pdf) and
        this [reference](https://homepages.inf.ed.ac.uk/rbf/CVonline/LOCAL_COPIES/EPSRC_SSAZ/node3.html)
        
        For background on camera matrices and pose estimation and some code reference, see:
        - https://www.cs.cmu.edu/~16385/s17/Slides/11.1_Camera_matrix.pdf
        - https://homepages.inf.ed.ac.uk/rbf/CVonline/LOCAL_COPIES/EPSRC_SSAZ/node3.html
        - https://learnopencv.com/head-pose-estimation-using-opencv-and-dlib/
        
        Parameters
        ----------
        image : np.ndarray
            The image frame of which want to get the face landmark

        face : 
            A list of 3D normalized coordinates (x, y, z) for a single face's landmarks.

        Return
        ----------
        tuple of float
            A tuple containing estimated head pose angles in degrees:
            - Roll(φ) (rotation around z-axis)
            - Pitch(θ) (rotation around x-axis)
            - Yaw(ψ) (rotation around y-axis)
        """
        face_2d = []
        face_3d = []
        img_h, img_w, _ = image.shape

        # Extract 3D and 2D landmarks for pose estimation
        for idx in connections:
            lm = face_landmark[idx]
            x, y = int(lm[0] * img_w), int(lm[1] * img_h)

            # 2D Coordinates
            face_2d.append([x, y])

            # 3D Coordinates (using the Z value)
            face_3d.append([x, y, lm[2]])

        face_2d = np.array(face_2d, dtype=np.float64)
        face_3d = np.array(face_3d, dtype=np.float64)

        # Camera matrix
        focal_length = 1 * img_w
        cam_matrix = np.array([[focal_length, 0             , img_w / 2],
                               [0           , focal_length  , img_h / 2],
                               [0           , 0             , 1        ]])

        dist_matrix = np.zeros((4, 1), dtype=np.float64)

        # Solve PnP (Perspective-n-Point) to get the rotation and translation vectors
        _, rot_vec, _ = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

        # Get rotational matrix from rotation vector
        rmat, _ = cv2.Rodrigues(rot_vec)

        # Decompose the rotation matrix to get Euler angles (yaw, pitch, roll)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

        x_angle = angles[0] * 360
        y_angle = angles[1] * 360
        z_angle = angles[2] * 360

        return x_angle, y_angle, z_angle

    def calculate_ear(self, eye:list) -> float:
        """
        Calculate Eye Aspect Ratio (EAR) using the left and right eye landmarks.
        The Formula for EAR is: EAR = (d1 + d2) / (2.0 * d3)
        where d1, d2, and d3 are distances between key points on the eye landmarks.

        Reference: 
         - https://vision.fe.uni-lj.si/cvww2016/proceedings/papers/05.pdf

        Parameters
        ----------
        eye : list
            The list of the point location of the pixel of the single eye
    
        Return
        ----------
            The Eye Aspect Ratio (EAR) value
        """
        # Calculate distances between points
        d1 = self.euclidean_distance(eye[1], eye[5])      # Vertical distance
        d2 = self.euclidean_distance(eye[2], eye[4])      # Vertical distance
        d3 = self.euclidean_distance(eye[0], eye[3])      # Horizontal distance

        ear = (d1 + d2) / (2.0 * d3)
        logging_default.debug("Ear Calculation: ", ear)

        return ear
    
    def calculate_mar(self, mouth:list):
        """
        Calculate Mouth Aspect Ratio (MAR) using the mouth of the lips landmark
        consist of 8 landmark, where the logic is the same as EAR where if the MAR value distance
        is more than the threshold, then it can be suggest that the driver is yawning

        Reference
         - https://www.mdpi.com/1424-8220/24/19/6261
         - https://www.mdpi.com/2313-433X/9/5/91

        Parameters
        ----------
        mouth : list
            The list of the point location of the pixel of the mouth landmark
        
        Return
        ----------
            The Mouth Aspect Ratio (EAR) value
        """
        a = self.euclidean_distance(mouth[1], mouth[7])
        b = self.euclidean_distance(mouth[2], mouth[6])
        c = self.euclidean_distance(mouth[3], mouth[5])
        d = self.euclidean_distance(mouth[0], mouth[4])

        mar = (a + b + c) / (2.0 * d)
        return mar

    def check_ear_below_threshold(self, ear: float) -> bool:
        """
        Check if the EAR is below the threshold, indicating possible drowsiness.

        Parameters
        ----------
        ear : float
            The EAR value

        Return
        ----------
        bool : 
            True if EAR is below the threshold, indicating potential drowsiness, False otherwise.
        """
        return ear < self.ear_ratio

    def check_mar_exceed_threshold(self, mar: float) -> bool:
        """
        Check if the MAR is exceed the threshold, indicating possible Yawning.

        Parameters
        ----------
        mar : float
            The MAR value

        Return
        ----------
        bool : 
            True if MAR is exceed the threshold, indicating potential yawning, False otherwise.
        """
        return mar > self.mouth_aspect_ratio_threshold

    def check_drowsiness(self, ear : float) -> bool:
        """
        Function to check the drowsiness based on the EAR value. The current default EAR
        threshold is 0.3 stored in the self.ear_ratio

        Parameters
        ----------
        ear : float
            The EAR value

        Return
        ----------
            True if EAR ratio is exceed theshold means driver sleepy sign by eye fatigue, False otherwise.  
        """
        if self.check_ear_below_threshold(ear):
            self.drowsiness_frame_counter += 1
            if self.drowsiness_frame_counter >= self.ear_consec_frames:
                return True
        else:
            self.drowsiness_frame_counter = 0
        return False
    
    def check_yawning(self, mar : float) -> bool:
        """
        Function to check the yawness based on the MAR value. The current default MAR
        threshold is 1.5 stored in the self.mouth_aspect_ratio_threshold

        Parameters
        ----------
        mar : float
            The MAR value

        Return
        ----------
            True if MAR ratio is exceed theshold means driver sleepy sign by yawning, False otherwise.  
        """
        if self.check_mar_exceed_threshold(mar):
            self.yawn_frame_counter +=1
            if self.yawn_frame_counter >= self.mouth_aspect_ratio_threshold:
                return True
        else:
            self.yawn_frame_counter = 0
        return False

    def euclidean_distance(self, point1 : list, point2 : list):
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
    
    def detects(self, original_frame : np.ndarray) -> DrowsinessDetectionResult:
        """
        Calculating the result of the detection and draw the results
        """
        results = DrowsinessDetectionResult()

        # Get the landmarks for the face
        face_landmarks = self.detect_face_landmarks(original_frame)

        # Drowsiness and pose detection
        if face_landmarks:
            face_id = 1

            for face_landmark in face_landmarks:
                face_result = FaceDrowsinessState()

                x_angle, y_angle, _ = self.estimate_head_pose(original_frame, face_landmark,HEAD_POSE_POINTS)
                face_result.x_angle = x_angle
                face_result.y_angle = y_angle
                
                direction_text = "Looking Forward"
                if y_angle < -10: direction_text = "Looking Left"
                elif y_angle > 10: direction_text = "Looking Right"
                elif x_angle < -10: direction_text = "Looking Down"
                elif x_angle > 10: direction_text = "Looking Up"
                face_result.direction_text = direction_text

                # Get the left-eye and right-eye landmark and mouth landmark
                left_eye, right_eye = self.extract_eye_landmark(face_landmark, LEFT_EYE_POINTS, RIGHT_EYE_POINTS, original_frame.shape[1], original_frame.shape[0])
                mouth = self.extract_mouth_landmark(face_landmark, OUTER_LIPS_POINTS, original_frame.shape[1], original_frame.shape[0])

                # Calculate the EAR Ratio and MAR ratio to check drowsiness
                ear = (self.calculate_ear(left_eye) + self.calculate_ear(right_eye)) / 2.0
                mar = self.calculate_mar(mouth)

                # Check for drowsines
                if self.check_drowsiness(ear):
                    face_result.is_drowsy = True

                # Check for yawning
                if self.check_yawning(mar):
                    face_result.is_yawning = True

                face_result.face_id = face_id
                face_result.ear = ear
                face_result.mar = mar
                face_result.face_landmark = face_landmark
                results.faces.append(face_result)

                face_id += 1
        return results

