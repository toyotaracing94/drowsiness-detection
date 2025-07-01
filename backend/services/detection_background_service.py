import threading

from backend.hardware.camera.base_camera import BaseCamera
from backend.services.drowsiness_detection_service import DrowsinessDetectionService
from backend.services.hand_detection_service import HandsDetectionService
from backend.services.phone_detection_service import PhoneDetectionService
from backend.tasks.detection_task import DetectionTask
from backend.utils.frame_buffer import FrameBuffer
from backend.utils.logging import logging_default


class DetectionBackgroundService:
    """
    A service that manages the background execution of the detection task 
    in a separate thread. It coordinates real-time monitoring of driver behavior,
    including drowsiness, phone usage, and hand gestures, using camera input 
    and machine learning models.

    This class serves as a controller that handles starting, pausing, resuming, 
    and stopping the detection loop.

    Parameters
    ----------
    detection_task : DetectionTask
        The task object that contains the core detection loop to be executed.
    drowsiness_service : DrowsinessDetectionService
        Service for detecting signs of driver drowsiness.
    phone_detection_service : PhoneDetectionService
        Service for detecting phone usage while driving.
    hand_service : HandsDetectionService
        Service for detecting hand presence, position, or gestures.
    camera : BaseCamera
        Camera interface used to capture video frames in real-time.
    frame_buffer : FrameBuffer
        Buffer that holds the latest raw and processed frames for use by other components.
    """

    def __init__(
        self,
        detection_task: DetectionTask,
        drowsiness_service: DrowsinessDetectionService,
        phone_detection_service: PhoneDetectionService,
        hand_service: HandsDetectionService,
        camera: BaseCamera,
        frame_buffer: FrameBuffer
    ):
        self.detection_task = detection_task
        self.drowsiness_service = drowsiness_service
        self.phone_detection_service = phone_detection_service
        self.hand_service = hand_service
        self.camera = camera
        self.frame_buffer = frame_buffer

        self.thread = None
        self.is_running = False

    def start(self) -> bool:
        """
        Starts the detection loop in a background thread.

        If a detection thread is already running, this method does nothing.
        The thread runs the `detection_loop` method of the `DetectionTask`,
        passing all required services and components.
        """
        try:
            if self.thread and self.thread.is_alive():
                logging_default.warning("Attempted to start detection, but thread is already running.")
                return False
            
            self.is_running = True
            self.thread = threading.Thread(
                target=self.detection_task.detection_loop,
                args=(
                    self.drowsiness_service,
                    self.phone_detection_service,
                    self.hand_service,
                    self.camera,
                    self.frame_buffer,
                    self
                ),
                daemon=True  # Ensure the thread exits when the main program exits
            )
            self.thread.start()
            logging_default.info("Started detection thread.")
            return True
        except Exception:
            return False

    def restart(self) -> bool:
        """
        Restarts the detection background thread by stopping any existing thread
        and then starting a new one.
        """
        try:
            # Signal the thread to stop
            logging_default.info("Restarting detection thread")
            self.is_running = False

            # Check whether old thread is active, if it's true
            # kill the thread, and make the new thread
            if self.thread and self.thread.is_alive():
                logging_default.info("Waiting for existing thread to finish.")
                self.thread.join(timeout=1)

            self.thread = None
            # Now start a new detection thread
            return self.start()
        except Exception:
            return False
        
    def pause(self) -> bool:
        """
        Pauses the detection loop.

        Sets the `is_running` flag to False. It is up to the detection loop
        to periodically check this flag and pause processing accordingly.
        """
        self.is_running = False
        self.drowsiness_service.buzzer_service.stop_buzzer()
        logging_default.info("Detection paused.")
        return not self.is_running

    def resume(self) -> bool:
        """
        Resumes the detection loop if it has been paused.

        Sets the `is_running` flag to True. The detection loop should use
        this flag to determine whether to continue processing.
        """
        self.is_running = True
        logging_default.info("Detection resumed.")
        return self.is_running

    def stop(self):
        """
        Stops the detection loop and attempts to join the thread.

        Sets the `is_running` flag to False and waits for the thread to finish.
        A timeout is used to prevent indefinite blocking.
        """
        try:
            logging_default.info("Stopping detection thread.")
            self.is_running = False
            if self.thread:
                self.thread.join(timeout=5)
                logging_default.info("Detection thread joined successfully.")
            self.thread = None
            return True
        except Exception:
            return False

    def is_active(self) -> bool:
        """
        Checks whether the detection loop is currently running in a thread.

        Returns
        -------
        bool
            True if the background thread is alive and the detection is active; 
            False otherwise.
        """
        active = self.thread is not None and self.thread.is_alive()
        logging_default.debug(f"Detection thread active: {active}")
        return active