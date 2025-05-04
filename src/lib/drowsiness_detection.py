import json
import math

import cv2
import numpy as np
from mediapipe.python.solutions import face_mesh

from src.utils.logging import logging_default


class DrowsinessDetection():
    def __init__(self, detection_settings_path: str):
        
        # Load configurations first 
        self.load_configuration(detection_settings_path)

        # Landmarks
        self.left_eye_landmarks = [33, 160, 158, 133, 153, 144]
        self.right_eye_landmarks = [362, 385, 387, 263, 373, 380]
        self.mouth_landmarks =  [61, 39, 0, 269, 291, 405, 17, 181]
        self.pose_landmarks = [1, 33, 61, 199, 263, 291]

        # Counter for the Yawn and Drowsiness
        self.drowsiness_frame_counter = 0
        self.yawn_frame_counter = 0

        # Face Mesh Model
        self.face_mesh = face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=self.max_number_face_detection,
            refine_landmarks=True,
            min_detection_confidence = self.min_detection_confidence,
            min_tracking_confidence = self.min_tracking_confidence
        )
        

    def load_configuration(self, path : str) -> None:
        """
        Load the detection settings from a configuration JSON file.

        Parameters
        ----------
        path : str
            Path to the configuration file containing threshold values for EAR, MAR, and etc.

        """
        logging_default.info("Loading drowsiness detection configs and model configuration")
        
        with open(path, 'r') as f:
            config = json.load(f)

        self.ear_ratio = config["eye_aspect_ratio_threshold"]
        self.ear_consec_frames = config["eye_aspect_ratio_consec_frames"]
        self.mouth_aspect_ratio_threshold = config["mouth_aspect_ration_threshold"]
        self.mouth_aspect_ratio_consec_frames = config["mouth_aspect_ration_consec_frames"]
        self.static_image_mode = config["static_image_mode"]
        self.refine_landmarks = config["refine_landmarks"]
        self.max_number_face_detection = config["max_number_face_detection"]
        self.min_tracking_confidence = config["min_tracking_confidence"]
        self.min_detection_confidence = config["min_detection_confidence"]

        logging_default.info(
            "Loaded config - EAR: %.2f, EAR Frames: %d, MAR: %.2f, MAR Frames: %d",
            self.ear_ratio, self.ear_consec_frames, self.mouth_aspect_ratio_threshold, self.mouth_aspect_ratio_consec_frames
        )
        return


    def detect_landmarks(self, image: np.ndarray) -> list:
        """
        This function is to process an RGB image and returns the face landmarks on each detected face.

        Parameters
        ----------
        image : np.ndarray
            The image frame of which want to get the face landmark

        Return
        ----------
        results :
            A list of special tuple Class in Mediapipe where it will have 
            multi_face_landmarks depends on the maximum face detection configuration
            set in the first place
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)
        return results

    def extract_mouth_landmarks(self, face_landmarks, frame_width = 640, frame_height = 480) -> list[tuple[int, int]]:
        """
        Extract the pixel location of the mouth landmark from the given face landmark,
        based on the choosen mouth landmark position index 

        Parameters
        ----------
        face_landmarks : np.ndarray
            The image frame of which want to get the face landmark
        frame_width : 
            The width of image frame
        frame_width : 
            The height of image frame

        Return
        ----------
        results :
            The list of pixels(x,y) of the mouth landmark
        """
        mouth_pixels = []

        for idx in self.mouth_landmarks:
            landmark = face_landmarks.landmark[idx]
            x = int(landmark.x * frame_width)  
            y = int(landmark.y * frame_height)
            mouth_pixels.append((x,y))
        
        return mouth_pixels
    
    def extract_eye_landmarks(self, face_landmarks, frame_width = 640, frame_height = 480) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
        """
        Extract the pixel location of the left-eye landmark and right-eye landmark from the given face landmark,
        based on the choosen left-eye landmark and right-eye landmark position index 

        Parameters
        ----------
        face_landmarks : np.ndarray
            The image frame of which want to get the face landmark
        frame_width : 
            The width of image frame
        frame_width : 
            The height of image frame

        Return
        ----------
        results :
            The tuple of list of pixels(x,y) of each left-eye landmark and right-eye landmark
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
        
        return (left_eye_pixels, right_eye_pixels)
    
    def estimate_head_pose(self, image : np.ndarray, face_landmarks):
        """
        This function is to Estimate head pose (yaw, pitch, roll) from 
        6 points of face landmarks from Mediapipe by converting the image coordinates
        to the world coordinate using OpenCV SolvePnp.

        <b>Note</b>: In my Opinion, the translation of the camera frame to the world frame coordinate
        is related the with inverse of Projection Matrix on the Camera Model. See this
        [reference](https://www.cs.cmu.edu/~16385/s17/Slides/11.1_Camera_matrix.pdf) and
        this [reference](https://homepages.inf.ed.ac.uk/rbf/CVonline/LOCAL_COPIES/EPSRC_SSAZ/node3.html) 
        
        Code Reference = https://learnopencv.com/head-pose-estimation-using-opencv-and-dlib/
        
        Parameters
        ----------
        image : np.ndarray
            The image frame of which want to get the face landmark

        face : 
            The list of 3D(x,y,z) of an estimate position of face landmarks

        Return
        ----------
        results :
            The angle estimation of the head in form of Roll(φ), Pitch(θ), Yaw(ψ)
        """
        face_3d = []
        face_2d = []
        img_h, img_w, _ = image.shape

        # Extract 3D and 2D landmarks for pose estimation
        for idx in self.pose_landmarks:
            lm = face_landmarks.landmark[idx]
            x, y = int(lm.x * img_w), int(lm.y * img_h)

            # 2D Coordinates
            face_2d.append([x, y])

            # 3D Coordinates (using the Z value)
            face_3d.append([x, y, lm.z])

        face_2d = np.array(face_2d, dtype=np.float64)
        face_3d = np.array(face_3d, dtype=np.float64)

        # Camera matrix
        focal_length = 1 * img_w
        cam_matrix = np.array([[focal_length, 0, img_w / 2],
                               [0, focal_length, img_h / 2],
                               [0, 0, 1]])

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
