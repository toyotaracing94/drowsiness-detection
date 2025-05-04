from flask import Flask, Response, render_template
import cv2
import mediapipe as mp
import time
import math

class poseDetector:

    def __init__(self, mode=False, modelComplexity=1, smLm=True, enaSeg=False, smSeg=True, minDetectConfi=0.5,
                 minTrackConfi=0.5):
        self.static_image_mode = mode
        self.model_complexity = modelComplexity
        self.smooth_landmarks = smLm
        self.enable_segmentation = enaSeg
        self.smooth_segmentation = smSeg

        self.min_detection_confidence = minDetectConfi
        self.min_tracking_confidence = minTrackConfi

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(self.static_image_mode, self.model_complexity, self.smooth_landmarks,
                                     self.enable_segmentation, self.smooth_segmentation, self.min_detection_confidence,
                                     self.min_tracking_confidence)

    def findPose(self, img, draw=True):

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
        return img

    def findPosition(self, img, draw=True):
        lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
                    cv2.putText(img, str(id), (cx, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)  # Adjusted y-coordinate
        return lmList



    def calculate_distance(self, point1, point2):
        distance = math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
        return distance


def main():
    cap = cv2.VideoCapture(0)
    pTime = 0
    start_time = time.time()

    # Get the width and height of the frame from the video capture
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    # Define the codec and create a VideoWriter object
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 'mp4v' for .mp4 files, 'XVID' for .avi
    # out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))  # Use the correct resolution

    detector = poseDetector()
    
    # Define the codec and create a VideoWriter object
    #fourcc = cv2.VideoWriter_fourcc(*'HEVC')
    #out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (640, 480))  # Adjust resolution as needed

    while True:
        # if time.time() - start_time > 30:  # Check if 15 seconds have elapsed
        #     break
            
        success, img = cap.read()
        if not success:
            break # If frame not successfully read, break loop

        img = detector.findPose(img)
        lmList = detector.findPosition(img, draw=False)
        
        if len(lmList) > 0:
            for lm in lmList:
                cv2.putText(img, str(lm[0]), (lm[1], lm[2]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        if len(lmList) > 16:  # Ensure enough landmarks are detected
            hand_landmark = lmList[16][1:]  # Hand landmark
            eye_landmark = lmList[8][1:]  # Eye landmark

            # Calculate the distance only if both hand and eye landmarks are detected
            if hand_landmark and eye_landmark:
                distance = detector.calculate_distance(hand_landmark, eye_landmark)
                distance_threshold = 170  # Adjust this threshold as needed

                if distance < distance_threshold:
                    cv2.putText(img, "Making a phone call", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Calculate the position of the text based on the original image size
                h, w, _ = img.shape
                text_position = (20, h - 50)
                # Show the calculated distance
                cv2.putText(img, f"Distance: {distance:.2f}", text_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        # Draw circles around the hand and eye landmarks
        if len(lmList) > 16:  # Ensure enough landmarks are detected
            cv2.circle(img, (lmList[16][1], lmList[16][2]), 10, (0, 255, 0), thickness=-1)  # Hand
        if len(lmList) > 8:
            cv2.circle(img, (lmList[8][1], lmList[8][2]), 10, (0, 0, 255), thickness=-1)  # Eye

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        # pTime = cTime

        cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # out.write(img)
        cv2.imshow("WebCam", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
        # Release everything when finished
    cap.release()
    # out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":  
    main()
