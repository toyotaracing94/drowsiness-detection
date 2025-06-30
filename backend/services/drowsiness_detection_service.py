import datetime
import time

import cv2
import numpy as np
from uuid6 import uuid7

from backend.domain.dto.drowsiness_detection_result import DrowsinessDetectionResult
from backend.domain.entity.drowsiness_event import DrowsinessEvent
from backend.lib.drowsiness_detection import DrowsinessDetection
from backend.lib.socket_trigger import SocketTrigger
from backend.services.buzzer_service import BuzzerService
from backend.services.drowsiness_event_service import DrowsinessEventService
from backend.settings.app_config import settings
from backend.settings.detection_config import detection_settings
from backend.settings.model_config import model_settings
from backend.utils.drawing_utils import (
    draw_face_bounding_box,
    draw_head_pose_direction,
    draw_landmarks,
)
from backend.utils.landmark_constants import (
    INNER_LIPS_CONNECTIONS,
    LEFT_EYE_CONNECTIONS,
    LEFT_EYEBROW_CONNECTIONS,
    OUTER_LIPS_CONNECTIONS,
    RIGHT_EYE_CONNECTIONS,
    RIGHT_EYEBROW_CONNECTIONS,
)
from backend.utils.logging import logging_default


class DrowsinessDetectionService:
    def __init__(self, buzzer_service : BuzzerService, socket_trigger : SocketTrigger, drowsiness_event_service: DrowsinessEventService):
        logging_default.info("Initiated Drowsiness Services")

        self.buzzer_service = buzzer_service
        self.socket_trigger = socket_trigger
        self.drowsiness_detector = DrowsinessDetection(model_settings.face, detection_settings.drowsiness ,inference_engine=settings.PipelineSettings.inference_engine)
        self.drowsiness_event_service = drowsiness_event_service

        self.drowsiness_start_time = None
        self.yawning_start_time = None

        self.drowsiness_notification_flag_sent = False
        self.yawning_notification_flag_sent = False

    def process_frame(self, frame : np.ndarray) -> DrowsinessDetectionResult:
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
        detection_result = self.drowsiness_detector.detects(frame)
        
        if detection_result.faces:
            # I'll just only buzzer the first face detected index for easier buzzer
            face_state = detection_result.faces[0]
        
            # Handle drowsiness logic
            if face_state.is_drowsy:
                if self.drowsiness_start_time is None:
                    self.drowsiness_start_time = time.time()

                duration = time.time() - self.drowsiness_start_time

                if 2 <= duration < 5:
                    self.buzzer_service.start_buzzer(self.buzzer_service.buzzer.beep_first_stage)
                elif 5 <= duration < 10:
                    self.buzzer_service.start_buzzer(self.buzzer_service.buzzer.beep_second_stage)
                elif duration >= 10:
                    self.buzzer_service.start_buzzer(self.buzzer_service.buzzer.beep_third_stage)

                if not self.drowsiness_notification_flag_sent:
                    image_uuid = uuid7()
                    self.socket_trigger.save_image(frame, image_uuid, 'DROWSINESS', '', 'UPLOAD_IMAGE')
                    event = DrowsinessEvent(
                        id=image_uuid,
                        vehicle_identification=settings.ApiSettings.vehicle_id,
                        image=f"{settings.ApiSettings.static_dir}/{settings.ApiSettings.image_event_dir}/{image_uuid}.jpg",
                        ear=face_state.ear,
                        mar=face_state.mar,
                        event_type="DROWSINESS",
                        timestamp=datetime.datetime.now()
                    )
                    self.drowsiness_event_service.create_event(event)
                    self.drowsiness_notification_flag_sent = True
                    detection_result.drowsiness_event = str(image_uuid)
            else:
                if self.drowsiness_start_time is not None:
                    duration = time.time() - self.drowsiness_start_time
                    logging_default.info(f"Driver regained alertness after {duration:.2f} seconds of drowsiness.")

                self.drowsiness_start_time = None
                self.drowsiness_notification_flag_sent = False
                self.buzzer_service.stop_buzzer()

            # Handle yawning logic
            if face_state.is_yawning:
                if not self.yawning_notification_flag_sent:
                    image_uuid = uuid7()
                    logging_default.info("Driver appears to be yawning. Triggering notification.")
                    self.socket_trigger.save_image(frame, image_uuid, 'YAWNING', '', 'UPLOAD_IMAGE')
                    event = DrowsinessEvent(
                        id=image_uuid,
                        vehicle_identification=settings.ApiSettings.vehicle_id,
                        image=f"{settings.ApiSettings.static_dir}/{settings.ApiSettings.image_event_dir}/{image_uuid}.jpg",
                        ear=face_state.ear,
                        mar=face_state.mar,
                        event_type="YAWNING",
                        timestamp=datetime.datetime.now()
                    )
                    self.drowsiness_event_service.create_event(event)
                    self.yawning_notification_flag_sent = True
                    detection_result.yawning_event = str(image_uuid)
            else:
                self.yawning_notification_flag_sent = False

        # Draw the annotate in the frame to save them into the result so in task orchestrator can get them
        detection_result.debug_frame = self.draw(frame, detection_result, detection_settings.drowsiness.apply_masking)

        return detection_result
    
    def draw(self, frame : np.ndarray, result : DrowsinessDetectionResult, draw_masking : bool) -> np.ndarray:
        """
        Draws visual annotations on the processed video frame for detected faces, including 
        bounding boxes, facial landmarks, and detection results such as drowsiness, yawning, 
        and head pose direction.

        Parameters
        ----------
        frame : np.ndarray
            The image frame (typically from a video stream) on which the annotations will be drawn.

        result : DrowsinessDetectionResult
            An object containing the results of face detection and drowsiness analysis. It includes
            information about each detected face, such as landmarks, drowsiness state, yawning state,
            and head pose angles.

        Returns
        -------
        np.ndarray
            The annotated image frame with visual indicators for each detected face.
        """
        annotated_frame = frame.copy()

        # Draw masking
        if draw_masking:
            height, width = annotated_frame.shape[:2]
            bottom_left = (0, height - 1)
            bottom_right = (width - 1, height - 1)
            top_middle = (width // 2, 0)

            # Draw the masking and the points
            triangle_cnt = np.array([bottom_left, bottom_right, top_middle], dtype=np.int32)
            cv2.polylines(annotated_frame, [triangle_cnt], isClosed=True, color=(0, 255, 0), thickness=2)
            cv2.circle(annotated_frame, top_middle, radius=6, color=(0, 0, 255), thickness=-1)
            overlay = annotated_frame.copy()
            cv2.fillPoly(overlay, [triangle_cnt], color=(0, 0, 0))
            alpha = 0.5
            annotated_frame = cv2.addWeighted(overlay, alpha, annotated_frame, 1 - alpha, 0)

        for face in result.faces:
            landmark = face.face_landmark
            if not landmark:
                continue 

            # Draw bounding box (you must have your own method for this)
            _, y_min, x_max, _ = draw_face_bounding_box(annotated_frame, landmark, face.face_id)

            # Draw drowsiness status
            if face.is_drowsy:
                cv2.putText(annotated_frame, "Drowsy!", (x_max + 10, y_min + 45),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Draw yawning status
            if face.is_yawning:
                cv2.putText(annotated_frame, "Yawning!", (x_max + 10, y_min + 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

            # Drawing Landmarks
            draw_landmarks(annotated_frame, landmark, LEFT_EYE_CONNECTIONS)
            draw_landmarks(annotated_frame, landmark, LEFT_EYEBROW_CONNECTIONS)
            draw_landmarks(annotated_frame, landmark, RIGHT_EYE_CONNECTIONS)
            draw_landmarks(annotated_frame, landmark, RIGHT_EYEBROW_CONNECTIONS)
            draw_landmarks(annotated_frame, landmark, OUTER_LIPS_CONNECTIONS)
            draw_landmarks(annotated_frame, landmark, INNER_LIPS_CONNECTIONS)

            # Draw Head pose direction
            draw_head_pose_direction(annotated_frame, landmark, face.x_angle, face.y_angle)
            direction_text = "Looking Forward"
            if face.y_angle < -10: direction_text = "Looking Left"
            elif face.y_angle > 10: direction_text = "Looking Right"
            elif face.x_angle < -10: direction_text = "Looking Down"
            elif face.x_angle > 10: direction_text = "Looking Up"
            direction_text = direction_text

            cv2.putText(annotated_frame, direction_text, (x_max + 10, y_min + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return annotated_frame
