import time

import cv2
import numpy as np

from src.hardware.camera import Camera
from src.lib.drowsiness_detection import DrowsinessDetection
from src.lib.hands_detection import HandsDetection
from src.lib.phone_detection import PhoneDetection
from src.lib.socket_trigger import SocketTrigger
from src.utils.drawing_utils import (
    draw_landmarks,
    draw_fps,
    draw_head_pose_direction,
)

from src.utils.landmark_constants import (
    LEFT_EYE_CONNECTION,
    RIGHT_EYE_CONNECTION,
    LEFT_EYEBROW_CONNECTION,
    RIGHT_EYEBROW_CONNECTION,
    OUTER_LIPS_CONNECTION,
    INNER_LIPS_CONNECTION,
    OUTER_FACE_CONNECTION,

    LEFT_EYE_POINTS,
    RIGHT_EYE_POINTS,
    OUTER_LIPS_POINTS,
    HEAD_POSE_POINTS
)

class DrowsinessDetectionService:
    def __init__(self):
        self.camera = Camera()
        self.socket_trigger = SocketTrigger("config/api_settings.json")
        self.drowsiness_detector = DrowsinessDetection("config/drowsiness_detection_settings.json")
        # self.phone_detection = PhoneDetection("config/pose_detection_settings.json")
        # self.hand_detector = HandsDetection("config/pose_detection_settings.json")
        self.prev_time = time.time()

    def process_frame(self, frame : np.ndarray):
        """
        This function is to process the frame and run multiple models to achieve the
        drowsiness detection. This class service will also hold the logic to count
        how time passed for the result of the model based on the `intent-wrapper` of the model

        Note
        ----------
        So the way it works is like this
        
        Workflow:  
            Controller --> Service --> Intent Use Case Wrapper --> Model [frame requested for processing]
            Controller <-- Service <-- Intent Use Case Wrapper <-- Model [results returned]

        Parameters
        ----------
        frame : np.ndarray
            The image frame of which want to get drowsiness detection service result

        Return
        ----------
        image
            An Image that has been process by the model, with landmark's draw has been
            draw directly to the image
        """
        image = frame.copy()

        # Get the landmarks for the face, body and hands
        face_landmarks = self.drowsiness_detector.detect_face_landmarks(frame)
        # hand_results = self.hand_detector.detect_hand_landmarks(frame)
        # body_pose = self.phone_detection.detect_body_pose(frame)

        # Phone usage detection feature get from pose information
        # is_calling, distance = self.phone_detection.detect_phone_usage(
        #     body_pose, frame.shape[1], frame.shape[0]
        # )

        # if is_calling:
        #     cv2.putText(image, "Making a phone call", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # if distance is not None:
        #     cv2.putText(image, f"Distance: {distance:.2f}", (20, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        # Drowsiness and pose detection
        if face_landmarks:
            for face_landmark in face_landmarks:
                x_angle, y_angle, _ = self.drowsiness_detector.estimate_head_pose(frame, face_landmark,HEAD_POSE_POINTS)

                direction_text = "Looking Forward"
                if y_angle < -10: direction_text = "Looking Left"
                elif y_angle > 10: direction_text = "Looking Right"
                elif x_angle < -10: direction_text = "Looking Down"
                elif x_angle > 10: direction_text = "Looking Up"

                # Get the left-eye and right-eye landmark and mouth landmark
                left_eye, right_eye = self.drowsiness_detector.extract_eye_landmark(face_landmark, LEFT_EYE_POINTS, RIGHT_EYE_POINTS, frame.shape[1], frame.shape[0])
                mouth = self.drowsiness_detector.extract_mouth_landmark(face_landmark, OUTER_LIPS_POINTS, frame.shape[1], frame.shape[0])

                # Calculate the EAR Ratio and MAR ratio to check drowsiness
                ear = (self.drowsiness_detector.calculate_ear(left_eye) + self.drowsiness_detector.calculate_ear(right_eye)) / 2.0
                mar = self.drowsiness_detector.calculate_mar(mouth)

                # Check for drowsines
                if self.drowsiness_detector.check_drowsiness(ear):
                    cv2.putText(image, "Drowsy!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    self.socket_trigger.save_image(image, 'DROWSINESS', '', 'UPLOAD_IMAGE')

                # Check for yawning
                if self.drowsiness_detector.check_yawning(mar):
                    cv2.putText(image, "Yawning!", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

                    # TODO : Find a mechanism to like a right timing to send those drowsiness event to the server
                    # Just think about it. Let's say in one timeframe or like just say for arguments
                    # it's 10 seconds. In that 10 second there will be like multiple frames (mark with this *)
                    # There's no way we want in every frame to send data to that, server will be overwhelmed
                    # Let's say this below ...
                    # <START DROWSINESS TRIGGER> * * * * * * *  ...  * <SOMEHOW DRIVER WAKES UP>
                    # at what event (*) should we send this into server?
                    # For now I'll just add this, always set send_to_server to false for now

                    self.socket_trigger.save_image(image, 'DROWSINESS', '', 'UPLOAD_IMAGE')

                # Draw the result of the eye drowsiness detection
                if left_eye: 
                    draw_landmarks(image, face_landmark, LEFT_EYE_CONNECTION)
                    draw_landmarks(image, face_landmark, LEFT_EYEBROW_CONNECTION, connected=False)

                if right_eye:
                    draw_landmarks(image, face_landmark, RIGHT_EYE_CONNECTION)
                    draw_landmarks(image, face_landmark, RIGHT_EYEBROW_CONNECTION, connected=False)

                if mouth: 
                    draw_landmarks(image, face_landmark, OUTER_LIPS_CONNECTION)
                    draw_landmarks(image, face_landmark, INNER_LIPS_CONNECTION)

                # Draw the direction of head pose
                draw_head_pose_direction(image, face_landmark, x_angle, y_angle)
                cv2.putText(image, direction_text, (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # if hand_results:
        #     hand_landmarks = self.hand_detector.extract_hand_landmark(hand_results, image.shape[1], image.shape[0])
        #     draw_hand_landmarks(image, hand_landmarks)

        # FPS calculation
        current_time = time.time()
        fps = 1 / (current_time - self.prev_time)
        self.prev_time = current_time
        draw_fps(image, f"FPS : {fps:.2f}")

        return image