import threading
import time

import cv2
import numpy as np

from src.hardware.buzzer.base_buzzer import BaseBuzzer
from src.lib.drowsiness_detection import DrowsinessDetection
from src.lib.socket_trigger import SocketTrigger
from src.utils.drawing_utils import (
    draw_head_pose_direction,
    draw_landmarks,
)
from src.utils.landmark_constants import (
    HEAD_POSE_POINTS,
    INNER_LIPS_CONNECTIONS,
    LEFT_EYE_CONNECTIONS,
    LEFT_EYE_POINTS,
    LEFT_EYEBROW_CONNECTIONS,
    OUTER_LIPS_CONNECTIONS,
    OUTER_LIPS_POINTS,
    RIGHT_EYE_CONNECTIONS,
    RIGHT_EYE_POINTS,
    RIGHT_EYEBROW_CONNECTIONS,
)
from src.utils.logging import logging_default


class DrowsinessDetectionService:
    def __init__(self, buzzer : BaseBuzzer, socket_trigger : SocketTrigger):
        logging_default.info("Initiated Drowsiness Services")

        self.buzzer = buzzer
        self.socket_trigger = socket_trigger
        self.drowsiness_detector = DrowsinessDetection("config/drowsiness_detection_settings.json")

        self.drowsiness_start_time = None
        self.yawning_start_time = None

        self.buzzer_thread = None
        self.buzzer_function = None
        self.keep_beeping = False

        self.drowsiness_notification_flag_sent = False
        self.yawning_notification_flag_sent = False

    def start_buzzer(self, buzzer_function : callable):
        """
        This function starts the buzzer function in a new thread, allowing the buzzer
        to run concurrently with the rest of the application without blocking the main thread.
        
        If there is already an active buzzer thread running, it will check if the 
        requested buzzer function is different from the currently active function. 
        If it is, the new function will replace the old one. Otherwise, the function will 
        not restart the thread.

        Parameters
        ----------
        buzzer_function : function
            A function that handles the buzzer behavior (such as calling `beep()` 
            or any other logic for controlling the buzzer). The function will be executed 
            repeatedly in the background thread.

        Notes
        -----
        - The buzzer function is expected to run continuously or in a loop until the
          `stop_buzzer()` method is called.
        - The `start_buzzer()` method prevents multiple threads from being created for
          the same buzzer function. If a thread is already running with the same function,
          it won't create a new thread.
        """
        if self.buzzer_thread and self.buzzer_thread.is_alive():
            if self.buzzer_function != buzzer_function:
                self.buzzer_function = buzzer_function
            return

        self.keep_beeping = True
        self.buzzer_function = buzzer_function
        self.buzzer_thread = threading.Thread(target=self.buzzer_loop, daemon=True)
        self.buzzer_thread.start()

    def stop_buzzer(self):
        """
        This function stops the buzzer function by setting the `keep_beeping` flag to `False`
        and clearing the `buzzer_function` and `drowsiness_stage`. So the actuall function that
        was running the "pseudo-function" of the beep can be putted down without clearing the Thread
        """
        self.keep_beeping = False
        self.buzzer_function = None
        self.drowsiness_stage = None
        self.buzzer.cleanup()
    
    def buzzer_loop(self):
        """
        This is the background loop that continuously executes the `buzzer_function` 
        while `keep_beeping` is `True` and a valid `buzzer_function` is set. The function
        is run repeatedly until `stop_buzzer()` is called, which sets `keep_beeping` to `False`.
        """
        while self.keep_beeping and self.buzzer_function:
            self.buzzer_function()

    def process_frame(self, frame : np.ndarray, processed_frame : np.ndarray) -> np.ndarray:
        """
        This function is to process the frame and run models to achieve the
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
        processed_frame : np.ndarray
            The image frame of which we want the draw happens

        Return
        ----------
        processed_frame
            An Image that has been process by the model, with landmark's draw has been
            draw directly to the image
        """
        # Get the landmarks for the face
        face_landmarks = self.drowsiness_detector.detect_face_landmarks(frame)

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
                    cv2.putText(processed_frame, "Drowsy!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    if self.drowsiness_start_time is None:
                        self.drowsiness_start_time = time.time()

                    # Calculate the time passes
                    duration = time.time() - self.drowsiness_start_time

                    # Start  running the buzzer in the background
                    if 2 <= duration < 5:
                        self.start_buzzer(self.buzzer.beep_first_stage)
                    elif 5 <= duration < 10:
                        self.start_buzzer(self.buzzer.beep_second_stage)
                    elif duration >= 10:
                        self.start_buzzer(self.buzzer.beep_third_stage)

                    # Send the notification
                    if not self.drowsiness_notification_flag_sent:
                        self.socket_trigger.save_image(processed_frame, 'DROWSINESS', '', 'UPLOAD_IMAGE')
                        self.drowsiness_notification_flag_sent = True

                else:
                    if self.drowsiness_start_time is not None:
                        duration = time.time() - self.drowsiness_start_time
                        logging_default.info(f"Driver regained alertness after {duration:.2f} seconds of drowsiness.")
                    
                    self.drowsiness_start_time = None
                    self.drowsiness_notification_flag_sent = False
                    self.stop_buzzer()

                # Check for yawning
                if self.drowsiness_detector.check_yawning(mar):
                    cv2.putText(processed_frame, "Yawning!", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

                    if not self.drowsiness_notification_flag_sent:
                        logging_default.info("Driver appears to be yawning. Triggering notification.")
                        self.socket_trigger.save_image(processed_frame, 'DROWSINESS', '', 'UPLOAD_IMAGE')
                        self.yawning_notification_flag_sent = True
                else:
                    # Reset for the notification flag
                    self.yawning_notification_flag_sent = False

                # Draw the result of the eye drowsiness detection
                if left_eye: 
                    draw_landmarks(processed_frame, face_landmark, LEFT_EYE_CONNECTIONS)
                    draw_landmarks(processed_frame, face_landmark, LEFT_EYEBROW_CONNECTIONS)

                if right_eye:
                    draw_landmarks(processed_frame, face_landmark, RIGHT_EYE_CONNECTIONS)
                    draw_landmarks(processed_frame, face_landmark, RIGHT_EYEBROW_CONNECTIONS)

                if mouth: 
                    draw_landmarks(processed_frame, face_landmark, OUTER_LIPS_CONNECTIONS)
                    draw_landmarks(processed_frame, face_landmark, INNER_LIPS_CONNECTIONS)

                # Draw the direction of head pose
                draw_head_pose_direction(processed_frame, face_landmark, x_angle, y_angle)
                cv2.putText(processed_frame, direction_text, (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        return processed_frame