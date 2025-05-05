import cv2

def draw_eye_landmarks(image, eye_landmarks, color=(0, 255, 0)):
    for i in range(len(eye_landmarks) - 1):
        pt1 = eye_landmarks[i]
        pt2 = eye_landmarks[i + 1]
        cv2.line(image, pt1, pt2, color, 1)
        cv2.circle(image, pt1, 2, color, -1)
    pt1 = eye_landmarks[-1]
    pt2 = eye_landmarks[0]
    cv2.line(image, pt1, pt2, color, 1)
    cv2.circle(image, pt1, 2, color, -1)

def draw_mouth_landmarks(image, mouth_landmarks, color=(0, 255, 0), center_line_color=(0, 255, 255)):
    if len(mouth_landmarks) >= 7:
        cv2.line(image, mouth_landmarks[2], mouth_landmarks[6], center_line_color, 2)
    for i in range(len(mouth_landmarks) - 1):
        pt1 = mouth_landmarks[i]
        pt2 = mouth_landmarks[i + 1]
        cv2.line(image, pt1, pt2, color, 1)
        cv2.circle(image, pt1, 2, (0, 0, 255), -1)
    pt1 = mouth_landmarks[-1]
    pt2 = mouth_landmarks[0]
    cv2.line(image, pt1, pt2, color, 1)
    cv2.circle(image, pt1, 2, (0, 0, 255), 1)

def draw_hand_landmarks(image, hand_landmarks, color=(0, 255, 255)):
    for hand in hand_landmarks:
        for pt in hand:
            cv2.circle(image, pt, 2, color, -1)

def draw_head_pose_direction(image, face_landmark, x_angle, y_angle, color=(255, 0, 0)):
    p1 = (
        int(face_landmark.landmark[1].x * image.shape[1]),
        int(face_landmark.landmark[1].y * image.shape[0])
    )
    p2 = (int(p1[0] + y_angle * 10), int(p1[1] - x_angle * 10))
    cv2.line(image, p1, p2, color, 3)
