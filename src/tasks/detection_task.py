import time

import cv2

from src.domain.dto.drowsiness_detection_result import DrowsinessDetectionResult
from src.domain.dto.hands_detection_result import HandsDetectionResult
from src.domain.dto.phone_detection_result import PhoneDetectionResult
from src.hardware.camera.base_camera import BaseCamera
from src.services.drowsiness_detection_service import DrowsinessDetectionService
from src.services.hand_detection_service import HandsDetectionService
from src.services.phone_detection_service import PhoneDetectionService
from src.settings.app_config import PipelineSettings
from src.utils.drawing_utils import (
    draw_face_bounding_box,
    draw_fps,
    draw_head_pose_direction,
    draw_landmarks,
)
from src.utils.frame_buffer import FrameBuffer
from src.utils.landmark_constants import (
    BODY_POSE_FACE_CONNECTIONS,
    HAND_CONNECTIONS,
    INNER_LIPS_CONNECTIONS,
    LEFT_EYE_CONNECTIONS,
    LEFT_EYEBROW_CONNECTIONS,
    OUTER_LIPS_CONNECTIONS,
    RIGHT_EYE_CONNECTIONS,
    RIGHT_EYEBROW_CONNECTIONS,
)
from src.utils.logging import logging_default


class DetectionTask:
    def __init__(self, pipeline_config : PipelineSettings):
        self.load_configuration(pipeline_config)

    def load_configuration(self, config : PipelineSettings):
        self.drowsiness_model_run = config.drowsiness_model_run
        self.phone_detection_model_run = config.phone_detection_model_run
        self.hands_detection_model_run = config.hands_detection_model_run

        logging_default.info(
            "Loaded config - drowsiness_model_run: {drowsiness_model_run}, phone_detection_model_run: {phone_detection_model_run}, hands_detection_model_run: {hands_detection_model_run}",
            drowsiness_model_run=self.drowsiness_model_run,
            phone_detection_model_run=self.phone_detection_model_run,
            hands_detection_model_run=self.hands_detection_model_run
        )

    def detection_loop(self, drowsiness_service : DrowsinessDetectionService, 
                   phone_detection_service : PhoneDetectionService,
                   hand_detection_service : HandsDetectionService,
                   camera : BaseCamera, frame_buffer : FrameBuffer):
        """
        This function serves as the main inference of the loop of the machine learning models.

        Parameters
        ----------
        drowsiness_service (DrowsinessDetectionService):
            The service responsible for detecting driver drowsiness and triggering alerts.
        phone_detection_service (PhoneDetectionService):
            The service used to detect if the driver is using a phone while driving.
        hand_detection_service (HandsDetectionService):
            The service used to detect hand presence or gestures.
        camera (BaseCamera):
            The camera interface used to capture frames from the video stream.
        frame_buffer (FrameBuffer):
            Shared object for storing the latest raw and processed frames 
            for access by other components (e.g., HTTP endpoints).
        
        Notes
        ----------
        - This method is intended to be run in a background thread.
        - Detection modules are only invoked if enabled in the config (pipeline_settings.json).
        - To prevent CPU overload, the loop includes a short sleep (~10ms) between iterations.
        """
    
        self.prev_time = time.time()

        while True:
            ret, original_frame = camera.get_capture()
            if not ret:
                time.sleep(0.01)
                continue
            
            original_frame = cv2.flip(original_frame, 1)
            processed_frame = original_frame.copy()

            # Save the frame to the shared global instance
            frame_buffer.update_raw(original_frame)

            # Run them into detection service
            drowsiness_detection_result = None
            phone_detection_result = None
            hands_detection_result = None

            if self.drowsiness_model_run:
                drowsiness_detection_result = drowsiness_service.process_frame(original_frame)
            if self.phone_detection_model_run:
                phone_detection_result = phone_detection_service.process_frame(original_frame)
            if self.hands_detection_model_run:
                hands_detection_result = hand_detection_service.process_frame(original_frame)

            # Draw the result
            if drowsiness_detection_result:
                processed_frame = self.draw_drowsiness_result(processed_frame, drowsiness_detection_result)
            if phone_detection_result:
                processed_frame = self.draw_phone_detection_result(processed_frame, phone_detection_result)
            if hands_detection_result:
                processed_frame = self.draw_hands_detection_result(processed_frame, hands_detection_result)

            # Draw the FPS
            # FPS calculation
            current_time = time.time()
            fps = 1 / (current_time - self.prev_time)
            self.prev_time = current_time
            draw_fps(processed_frame, f"FPS : {fps:.2f}")

            # Save the processed 
            frame_buffer.update_processed(processed_frame)

            # Exposing facial metrics to websocket communication
            if drowsiness_detection_result.faces:
                face = drowsiness_detection_result.faces[0]
                frame_buffer.update_facial_metrics(face.ear, face.mar, face.is_drowsy, face.is_yawning)
            else:
                frame_buffer.update_facial_metrics(0, 0, False, False)

            # Exposing recent detected event to websocket communication
            if drowsiness_detection_result:
                frame_buffer.update_drowsiness_event_recent(drowsiness_detection_result.drowsiness_event, drowsiness_detection_result.yawning_event)

            time.sleep(0.01)

    def draw_drowsiness_result(self, processed_frame, result : DrowsinessDetectionResult):
        for face in result.faces:
            landmark = face.face_landmark
            if not landmark:
                continue  # skip faces with no landmarks

            # Draw bounding box (you must have your own method for this)
            _, y_min, x_max, _ = draw_face_bounding_box(processed_frame, landmark, face.face_id)

            # Draw drowsiness status
            if face.is_drowsy:
                cv2.putText(processed_frame, "Drowsy!", (x_max + 10, y_min + 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Draw yawning status
            if face.is_yawning:
                cv2.putText(processed_frame, "Yawning!", (x_max + 10, y_min + 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

            # Drawing Landmarks
            draw_landmarks(processed_frame, landmark, LEFT_EYE_CONNECTIONS)
            draw_landmarks(processed_frame, landmark, LEFT_EYEBROW_CONNECTIONS)
            draw_landmarks(processed_frame, landmark, RIGHT_EYE_CONNECTIONS)
            draw_landmarks(processed_frame, landmark, RIGHT_EYEBROW_CONNECTIONS)
            draw_landmarks(processed_frame, landmark, OUTER_LIPS_CONNECTIONS)
            draw_landmarks(processed_frame, landmark, INNER_LIPS_CONNECTIONS)

            # Head pose direction
            draw_head_pose_direction(processed_frame, landmark, face.x_angle, face.y_angle)
            cv2.putText(processed_frame, face.direction_text, (x_max + 10, y_min + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        return processed_frame

    def draw_phone_detection_result(self, processed_frame, result : PhoneDetectionResult):
        for phone_state in result.detection:
            if phone_state.is_calling:
                cv2.putText(processed_frame, "Making a phone call", (50, 150), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if phone_state.distance is not None:
                cv2.putText(processed_frame, f"Distance: {phone_state.distance:.2f}", 
                            (20, processed_frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

            if phone_state.body_landmark is not None:
                draw_landmarks(processed_frame, phone_state.body_landmark, BODY_POSE_FACE_CONNECTIONS, 
                            color_lines=(255, 0, 0), color_points=(0, 0, 255))
        return processed_frame

    def draw_hands_detection_result(self, processed_frame, result : HandsDetectionResult):
        for hand_state in result.hands:
            if hand_state.hand_landmark is not None:
                draw_landmarks(processed_frame, hand_state.hand_landmark, HAND_CONNECTIONS, color_points=(0, 0, 0))
        return processed_frame