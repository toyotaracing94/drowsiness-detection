import cv2
from src.hardware.camera import Camera
from src.lib.drowsiness_detection import DrowsinessDetection
from src.lib.pose_detection import PoseDetection
from src.lib.socket_trigger import SocketTrigger

# Initailize the hardware and the lib services
camera = Camera()
socket_trigger = SocketTrigger("config/api_settings.json")
drowsiness_detector = DrowsinessDetection("config/drowsiness_detection_settings.json")
pose_detector = PoseDetection("config/pose_detection_settings.json")

def generate_original_capture_stream():
    """
    This function special for the FastAPI backend controller to continuously captures frames from the camera
    and return a stream for real-time display transmission
    """
    while True:
        # Capture the video stream
        ret, frame = camera.get_capture()
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

def generate_drowsiness_stream():
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
        ret, frame = camera.get_capture()
        frame = cv2.flip(frame, 1) 

        # Copy the frame to be passed around and keep the original one
        image = frame.copy()
        if not ret:
            break
        
        # Get the Multi-Face Mesh Landmarks (486 points)
        face_landmarks = drowsiness_detector.detect_landmarks(frame)
        # Find hand landmarks
        hand_results = pose_detector.detect_hand_landmarks(frame)
        # Get the body-pose
        body_pose = pose_detector.detect_body_pose(frame)

        # Phone usage feature get from pose information
        is_calling, dist = pose_detector.detect_phone_usage(
            body_pose,
            frame_width=frame.shape[1],
            frame_height=frame.shape[0]
        )

        if is_calling:
            cv2.putText(image, "Making a phone call", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        if dist is not None:
            cv2.putText(image, f"Distance: {dist:.2f}", (20, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        # Detect the drowsiness and the head pose estimation from the face landmarks information
        if face_landmarks.multi_face_landmarks:
            for face_landmarks in face_landmarks.multi_face_landmarks:
                # Get the head pose (yaw, pitch, roll)
                x_angle, y_angle, z_angle = drowsiness_detector.estimate_head_pose(frame, face_landmarks)

                # Draw the head pose direction
                head_pose_text = "Looking Forward"
                if y_angle < -10:
                    head_pose_text = "Looking Left"
                elif y_angle > 10:
                    head_pose_text = "Looking Right"
                elif x_angle < -10:
                    head_pose_text = "Looking Down"
                elif x_angle > 10:
                    head_pose_text = "Looking Up"

                # Draw the direction of head pose
                p1 = (int(face_landmarks.landmark[1].x * frame.shape[1]), int(face_landmarks.landmark[1].y * frame.shape[0]))
                p2 = (int(p1[0] + y_angle * 10), int(p1[1] - x_angle * 10))
                cv2.line(image, p1, p2, (255, 0, 0), 3)

                # Add the head pose text to the frame
                cv2.putText(image, head_pose_text, (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # Get the left-eye and right-eye landmark
                left_eye_landmark, right_eye_landmark = drowsiness_detector.extract_eye_landmarks(face_landmarks, frame.shape[1], frame.shape[0])

                # Get the mouth landmark
                mouth_eye_landmark = drowsiness_detector.extract_mouth_landmarks(face_landmarks,frame.shape[1], frame.shape[0])

                # Calculate the EAR Ratio to check drowsiness
                left_ear = drowsiness_detector.calculate_ear(left_eye_landmark)
                right_ear = drowsiness_detector.calculate_ear(right_eye_landmark) 
                # Average the EAR of both eyes
                ear = (left_ear + right_ear) / 2.0

                # Calculate the MAR Ratio to check yawning
                mar = drowsiness_detector.calculate_mar(mouth_eye_landmark)

                # Check for drowsiness
                if drowsiness_detector.check_drowsiness(ear):
                    cv2.putText(image, "Drowsy!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    # TODO : Find a mechanism to like a right timing to send those drowsiness event to the server
                    # Just think about it. Let's say in one timeframe or like just say for arguments
                    # it's 10 seconds. In that 10 second there will be like multiple frames (mark with this *)
                    # There's no way we want in every frame to send data to that, server will be overwhelmed
                    # Let's say this below ...
                    # <START DROWSINESS TRIGGER> * * * * * * *  ...  * <SOMEHOW DRIVER WAKES UP>
                    # at what event (*) should we send this into server?
                    # For now I'll just add this, always set send_to_server to false for now

                    socket_trigger.save_image(image, 'DROWSINESS', '', 'UPLOAD_IMAGE')

                # Check for yawning
                if drowsiness_detector.check_yawning(mar):
                    cv2.putText(image, "Yawning!", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

                # Draw the result of the eye drowsiness detection
                if left_eye_landmark and right_eye_landmark:
                    # Draw connected circles for left eye
                    for i in range(len(left_eye_landmark) - 1):
                        pt1 = left_eye_landmark[i]
                        pt2 = left_eye_landmark[i + 1]
                        
                        # Draw a line between consecutive points in green
                        cv2.line(image, pt1, pt2, (0, 255, 0), 1)
                        # Draw circles at the points in green
                        cv2.circle(image, pt1, 2, (0, 255, 0), -1)
                    
                    # To close the left eye loop, connect the last point to the first in green
                    pt1 = left_eye_landmark[-1]
                    pt2 = left_eye_landmark[0]
                    cv2.line(image, pt1, pt2, (0, 255, 0), 1)
                    cv2.circle(image, pt1, 2, (0, 255, 0), -1)

                    # Draw connected circles for right eye
                    for i in range(len(right_eye_landmark) - 1):
                        pt1 = right_eye_landmark[i]
                        pt2 = right_eye_landmark[i + 1]
                        
                        # Draw a line between consecutive points in green
                        cv2.line(image, pt1, pt2, (0, 255, 0), 1)
                        # Draw circles at the points in green
                        cv2.circle(image, pt1, 2, (0, 255, 0), -1)
                    
                    # To close the left eye loop, connect the last point to the first in green
                    pt1 = right_eye_landmark[-1]
                    pt2 = right_eye_landmark[0]
                    cv2.line(image, pt1, pt2, (0, 255, 0), 1)
                    cv2.circle(image, pt1, 2, (0, 255, 0), -1)

                # Draw the mouth
                if mouth_eye_landmark:
                    # Drawing the line between the middle top and bottom of the lips
                    cv2.line(image, mouth_eye_landmark[2], mouth_eye_landmark[6], (0, 255, 255), 2)

                    for i in range(len(mouth_eye_landmark) - 1):
                        pt1 = mouth_eye_landmark[i]
                        pt2 = mouth_eye_landmark[i + 1]
                        
                        # Draw a line between consecutive points
                        cv2.line(image, pt1, pt2, (0, 255, 0), 1)
                        # Draw circles at the points
                        cv2.circle(image, pt1, 2, (0, 0, 255), -1)

                    pt1 = mouth_eye_landmark[-1]
                    pt2 = mouth_eye_landmark[0]
                    cv2.line(image, pt1, pt2, (0, 255, 0), 1)
                    cv2.circle(image, pt1, 2, (0, 0, 255), 1)


        # Draw hand landmarks
        if hand_results.multi_hand_landmarks:
            hand_landmarks = pose_detector.extract_hand_landmarks(hand_results, image.shape[1], image.shape[0])
            for hand in hand_landmarks:
                for pt in hand:
                    cv2.circle(image, pt, 2, (0, 255, 255), -1)  # Yellow circle for hand landmarks
                        
        # Encode the frame as JPEG
        success, buffer = cv2.imencode('.jpg', image)
        if not success:
            continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
