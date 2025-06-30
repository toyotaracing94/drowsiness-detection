import unittest

import cv2

from backend.lib.drowsiness_detection import DrowsinessDetection
from backend.settings.app_config import settings
from backend.settings.detection_config import detection_settings
from backend.settings.model_config import model_settings
from backend.utils.landmark_constants import (
    LEFT_EYE_POINTS,
    OUTER_LIPS_POINTS,
    RIGHT_EYE_POINTS,
)


class DrowsinessTest(unittest.TestCase):
    def setUp(self):
        """
        Setup necessary instances and objects to be used across multiple tests.
        """
        self.drowsiness_detector = DrowsinessDetection(model_settings.face, detection_settings.drowsiness ,inference_engine=settings.PipelineSettings.inference_engine)

    def test_drowsiness_with_closed_eyes(self):
        """
        Test if the system detects drowsiness when the eyes are closed.
        """
        frame = cv2.imread("backend/test/test_resources/drowsy_full_both_eye_closes.jpeg")
        # Detect face landmarks
        face_landmarks = self.drowsiness_detector.detect_face_landmarks(frame)
        
        # Check if faces are detected (multi_face_landmarks is not empty)
        if face_landmarks:
            for face_landmark in face_landmarks:
                # Get the left-eye and right-eye landmark
                left_eye_landmark, right_eye_landmark = self.drowsiness_detector.extract_eye_landmark(face_landmark, LEFT_EYE_POINTS, RIGHT_EYE_POINTS, frame.shape[1], frame.shape[0])
                
                # Calculate the EAR Ratio to check drowsiness
                left_ear = self.drowsiness_detector.calculate_ear(left_eye_landmark)
                right_ear = self.drowsiness_detector.calculate_ear(right_eye_landmark)
                
                # Average the EAR of both eyes
                ear = (left_ear + right_ear) / 2.0

                # Assert drowsiness detected
                self.assertTrue(self.drowsiness_detector.check_ear_below_threshold(ear), f"Should detect drowsiness when eyes are closed. MAR value {ear}, MAR Threshold {self.drowsiness_detector.ear_ratio}")
        else:
            self.fail("No face landmarks detected")

    def test_yawning_with_mouth_open(self):
        """
        Test if the system detects yawning correctly.
        """
        frame = cv2.imread("backend/test/test_resources/driver_yawning.jpg")
        # Detect face landmarks
        face_landmarks = self.drowsiness_detector.detect_face_landmarks(frame)

        # Check if faces are detected (multi_face_landmarks is not empty)
        if face_landmarks:
            for face_landmark in face_landmarks:
                # Get the mouth landmark
                mouth_eye_landmark = self.drowsiness_detector.extract_mouth_landmark(face_landmark, OUTER_LIPS_POINTS, frame.shape[1], frame.shape[0])
                
                # Calculate the MAR Ratio to check yawning
                mar = self.drowsiness_detector.calculate_mar(mouth_eye_landmark)
                
                # Assert drowsiness detected
                self.assertTrue(self.drowsiness_detector.check_mar_exceed_threshold(mar), f"Should detect yawning when mouth are fully open! MAR value {mar}, MAR Threshold {self.drowsiness_detector.mouth_aspect_ratio_threshold}")
        else:
            self.fail("No face landmarks detected")

if __name__ == "__main__":
    unittest.main()