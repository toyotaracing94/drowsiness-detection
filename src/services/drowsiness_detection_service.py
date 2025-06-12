import datetime
import threading
import time

import numpy as np
from uuid6 import uuid7

from src.domain.dto.drowsiness_detection_result import DrowsinessDetectionResult
from src.domain.entity.drowsiness_event import DrowsinessEvent
from src.hardware.buzzer.base_buzzer import BaseBuzzer
from src.lib.drowsiness_detection import DrowsinessDetection
from src.lib.socket_trigger import SocketTrigger
from src.services.drowsiness_event_service import DrowsinessEventService
from src.utils.logging import logging_default



class DrowsinessDetectionService:
    def __init__(self, buzzer : BaseBuzzer, socket_trigger : SocketTrigger, drowsiness_event_service: DrowsinessEventService, inference_engine : str = None):
        logging_default.info("Initiated Drowsiness Services")

        self.buzzer = buzzer
        self.socket_trigger = socket_trigger
        self.drowsiness_detector = DrowsinessDetection("config/drowsiness_detection_settings.json", inference_engine=inference_engine)
        self.drowsiness_event_service = drowsiness_event_service

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
                    self.start_buzzer(self.buzzer.beep_first_stage)
                elif 5 <= duration < 10:
                    self.start_buzzer(self.buzzer.beep_second_stage)
                elif duration >= 10:
                    self.start_buzzer(self.buzzer.beep_third_stage)

                if not self.drowsiness_notification_flag_sent:
                    self.socket_trigger.save_image(frame, 'DROWSINESS', '', 'UPLOAD_IMAGE')
                    event = DrowsinessEvent(
                        vehicle_identification="ABC123",
                        image="yes",
                        ear=face_state.ear,
                        mar=face_state.mar,
                        event_type="DROWSINESS",
                        timestamp=datetime.datetime.now()
                    )
                    self.drowsiness_event_service.create_event(event)
                    self.drowsiness_notification_flag_sent = True
            else:
                if self.drowsiness_start_time is not None:
                    duration = time.time() - self.drowsiness_start_time
                    logging_default.info(f"Driver regained alertness after {duration:.2f} seconds of drowsiness.")

                self.drowsiness_start_time = None
                self.drowsiness_notification_flag_sent = False
                self.stop_buzzer()

            # Handle yawning logic
            if face_state.is_yawning:
                if not self.yawning_notification_flag_sent:
                    logging_default.info("Driver appears to be yawning. Triggering notification.")
                    self.socket_trigger.save_image(frame, 'DROWSINESS', '', 'UPLOAD_IMAGE')
                    self.yawning_notification_flag_sent = True
            else:
                self.yawning_notification_flag_sent = False

        return detection_result        