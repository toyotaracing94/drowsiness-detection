import cv2

from src.lib.drowsiness_detection import DrowsinessDetection
from src.utils.logging import logging_default

def main():
    capture = cv2.VideoCapture(0)
    drowsiness_detector = DrowsinessDetection("config/detection_settings.json")
    
    while True:
        # Capture the video stream
        # TODO: make the camera selection an automatic one. If its on windows development, capture using
        # the webcam, if use the Raspberry Pi (in case here using Raspi Camera), use that
        ret, frame = capture.read()
        image = frame.copy()
        if not ret:
            break
        
        # Get the Multi-Face Mesh Landmarks (486 points)
        face_landmarks = drowsiness_detector.detect_landmarks(image)

        if face_landmarks.multi_face_landmarks:
            for face_landmarks in face_landmarks.multi_face_landmarks:
        
                # Get the left-eye and right-eye landmark
                left_eye_landmark, right_eye_landmark = drowsiness_detector.extract_eye_landmarks(face_landmarks)

                # Get the mouth landmark
                mouth_eye_landmark = drowsiness_detector.extract_mouth_landmarks(face_landmarks)

                # Calculate the EAR Ratio to check drowsiness
                ear = drowsiness_detector.calculate_ear(left_eye_landmark, right_eye_landmark)

                # Calculate the MAR Ratio to check yawness lol
                mar = drowsiness_detector.calculate_mar(mouth_eye_landmark)

                # Check for drowsiness
                if drowsiness_detector.check_drowsiness(ear):
                    cv2.putText(image, "Drowsy!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # Check for yawness
                if drowsiness_detector.check_yawning(mar):
                    cv2.putText(image, "Yawning!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

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

        # Display the result
        side_by_side = cv2.hconcat([frame, image])
        cv2.imshow('Side by Side', side_by_side)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()