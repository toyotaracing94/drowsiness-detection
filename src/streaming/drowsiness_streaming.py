import cv2

from src.services.drowsiness_detection_service import DrowsinessDetectionService


def stream_raw_camera_feed(drowsiness_service : DrowsinessDetectionService):
    """
    This function special for the FastAPI backend controller to continuously captures frames from the camera
    and return a stream for real-time display transmission
    """
    while True:
        # Capture the video stream
        ret, frame = drowsiness_service.camera.get_capture()
        frame = cv2.flip(frame, 1)
        if not ret:
            break

        # Encode the frame as JPEG
        success, buffer = cv2.imencode('.jpg', frame)
        if not success:
            continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
def stream_processed_drowsiness_feed(drowsiness_service : DrowsinessDetectionService):
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
        ret, frame = drowsiness_service.camera.get_capture()
        if not ret:
            break
        frame = cv2.flip(frame, 1)

        # Process each frame to check the drowsiness detection process
        processed_image = drowsiness_service.process_frame(frame)

        # Encode the frame as JPEG
        success, buffer = cv2.imencode('.jpg', processed_image)
        if not success:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')