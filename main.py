import cv2
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from src.lib.drowsiness_detection import DrowsinessDetection
from src.lib.pose_detection import PoseDetection
from src.utils.logging import logging_default

capture = cv2.VideoCapture(0)
drowsiness_detector = DrowsinessDetection("config/drowsiness_detection_settings.json")
pose_detector = PoseDetection("config/pose_detection_settings.json")

app = FastAPI()

def main():
    while True:
        # Capture the video stream
        # TODO: make the camera selection an automatic one. If its on windows development, capture using
        # the webcam, if use the Raspberry Pi (in case here using Raspi Camera), use that
        ret, frame = capture.read()
        frame = cv2.flip(frame, 1) 
        image = frame.copy()
        if not ret:
            break
        
        # Get the Multi-Face Mesh Landmarks (486 points)
        face_landmarks = drowsiness_detector.detect_landmarks(frame)
        # Find hand landmarks
        hand_results = pose_detector.detect_hand_landmarks(image)
        # Get the body-pose
        body_pose = pose_detector.detect_body_pose(frame)

        # Phone usage from pose
        is_calling, dist = pose_detector.detect_phone_usage(
            body_pose,
            frame_width=frame.shape[1],
            frame_height=frame.shape[0]
        )

        if is_calling:
            cv2.putText(image, "Making a phone call", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        if dist is not None:
            cv2.putText(image, f"Distance: {dist:.2f}", (20, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)


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

                # Check for yawning
                if drowsiness_detector.check_yawning(mar):
                    cv2.putText(image, "Yawning!", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

                # Draw the result of the detection
                if left_eye_landmark and right_eye_landmark:
                    for pt in left_eye_landmark:
                        cv2.circle(image, pt, 1, (0, 255, 0), -1)
                    for pt in right_eye_landmark:
                        cv2.circle(image, pt, 1, (0, 255, 0), -1)

                # Draw the mouth
                if mouth_eye_landmark:
                    for pt in mouth_eye_landmark:
                        cv2.circle(image, pt, 1, (255, 0, 0), -1)

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

@app.get(
    "/video",
    summary="Live Video Stream",
    description="Returns a live video stream (MJPEG) captured from the webcam. "
                "Note: Swagger UI does not support streaming, so use the `/` route in a browser to view the stream."
)
def video_feed():
    return StreamingResponse(main(), media_type="multipart/x-mixed-replace; boundary=frame")