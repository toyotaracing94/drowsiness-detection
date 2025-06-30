import time

import cv2

from backend.utils.frame_buffer import FrameBuffer


def stream_raw_camera_feed(frame_buffer : FrameBuffer):
    """
    This function special for the FastAPI backend controller to continuously captures frames from the camera
    and return a stream for real-time display transmission
    """
    while True:
        frame = frame_buffer.get_raw()
        if frame is None:
            time.sleep(0.03)
            continue

        success, buffer = cv2.imencode('.jpg', frame)
        if not success:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        time.sleep(0.03)
        
def stream_processed_drowsiness_feed(frame_buffer : FrameBuffer):
    """
    This function special for the FastAPI backend controller to continuously captures frames from the camera, processes them for drowsiness detection, 
    and generates back a video stream with annotated landmarks and detection results.

    This function performs the following operations on each frame:
    1. Captures a video frame from the camera.
    2. Detects multi-face landmarks using a drowsiness detection model.
    3. Detects hand landmarks and body pose.
    4. Identifies if the user is making a phone call based on body pose.
    5. Estimates head pose (yaw, pitch, roll) and draws corresponding annotations.
    6. Checks for drowsiness and yawning based on eye aspect ratio (EAR) and mouth aspect ratio (MAR).
    7. Draws annotations for detected landmarks (eyes, mouth, hands).
    8. Encodes the processed frame as a JPEG image for streaming.

    The resulting frames are yielded as a stream for real-time display or transmission.
    """
    while True:
        # Capture the video stream
        frame = frame_buffer.get_processed()
        if frame is None:
            time.sleep(0.03)
            continue

        success, buffer = cv2.imencode('.jpg', frame)
        if not success:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        time.sleep(0.03)

def stream_debug_camera_feed(frame_buffer : FrameBuffer):
    """
    This function special for the FastAPI backend controller to continuously captures frames from the camera
    and return a stream for real-time display transmission
    """
    while True:
        frame = frame_buffer.get_debug()
        if frame is None:
            time.sleep(0.03)
            continue

        success, buffer = cv2.imencode('.jpg', frame)
        if not success:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

        time.sleep(0.03)