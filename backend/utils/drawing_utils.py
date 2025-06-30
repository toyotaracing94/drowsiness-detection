from datetime import datetime

import cv2
import numpy as np


def draw_landmarks(image : np.ndarray, landmarks, connections, color_lines=(0, 255, 0), color_points=(0, 255, 0), size=1):
    """
    Draws lines between specified pairs of normalized landmarks.

    Parameters:
        image (ndarray): The image to draw on.
        landmarks (list of (x, y, z)): Normalized landmark coordinates.
        connections (list of (start_idx, end_idx)): List of index pairs to connect.
        color_lines (tuple): BGR color for drawing lines.
        color_points (tuple): BGR color for drawing each point circle.
        size (int): Line thickness.
    """
    height, width = image.shape[:2]

    for start_idx, end_idx in connections:
        x0, y0, _ = landmarks[start_idx]
        x1, y1, _ = landmarks[end_idx]

        pt1 = int(x0 * width), int(y0 * height)
        pt2 = int(x1 * width), int(y1 * height)

        cv2.line(image, pt1, pt2, color_lines, thickness=size)
        cv2.circle(image, pt2, size + 1, color_points, -1)

def draw_face_bounding_box(frame : np.ndarray, face_landmark, face_index):
    """
    Draws an bounding box based on the face landmark that was given

    Parameters:
        frame (ndarray): Image on which to draw.
        face_landmark (list): List of face landmark coordinates [(x, y, z)].
        face_index (int): Index which to draw
        color (tuple): Color of the arrow (default red).

    return:
        tuple of int
            Coordinates of the bounding box in the format (x_min, y_min, x_max, y_max).
    """
    h, w = frame.shape[:2]
    coords = [(int(lm[0] * w), int(lm[1] * h)) for lm in face_landmark]

    x_coords = [p[0] for p in coords]
    y_coords = [p[1] for p in coords]

    x_min, y_min = max(min(x_coords) - 10, 0), max(min(y_coords) - 10, 0)
    x_max, y_max = min(max(x_coords) + 10, w), min(max(y_coords) + 10, h)

    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
    cv2.putText(frame, f"Face #{face_index}", (x_min, y_min - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return x_min, y_min, x_max, y_max

def draw_head_pose_direction(image : np.ndarray, face_landmark, x_angle, y_angle, color=(0, 0, 255)):
    """
    Draws an arrow indicating head pose direction based on face landmarks and rotation angles.

    Parameters:
        image (ndarray): Image on which to draw.
        face_landmark (list): List of face landmark coordinates [(x, y, z)].
        x_angle (float): Pitch angle (up/down).
        y_angle (float): Yaw angle (left/right).
        color (tuple): Color of the arrow (default red).
    """
    # Starting point: center of the face (e.g., nose tip or landmark index 1)
    p1 = (
        int(face_landmark[1][0] * image.shape[1]),
        int(face_landmark[1][1] * image.shape[0])
    )
    
    # Ending point determined by the rotation angles
    p2 = (
        int(p1[0] + y_angle * 3),
        int(p1[1] - x_angle * 3)
    )
    
    # Draw the arrowed line
    cv2.arrowedLine(image, p1, p2, color, thickness=2, tipLength=0.3)

def draw_fps(image : np.ndarray, fps_text : str, font_scale : int = 0.7, color=(0, 255, 255), thickness : int = 2, padding : int = 10):
    # Get the text size
    (text_width, text_height), baseline = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
    # Coordinates for top-right corner with padding
    x = image.shape[1] - text_width - padding
    y = text_height + padding
    # Draw rectangle background for text (optional for better readability)
    cv2.rectangle(image, (x - 5, y - text_height - 5), (x + text_width + 5, y + 5), (0, 0, 0), -1)
    # Draw the FPS text on the image
    cv2.putText(image, fps_text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

def draw_timestamp(frame : np.ndarray, position=(10, 30), font_scale=0.6, thickness=2, fmt="%Y-%m-%d %H:%M:%S"):
    """
    Draws a timestamp on the given video frame, automatically choosing text color based on frame brightness.

    Parameters:
    ----------
    frame : np.ndarray
        The video frame on which the timestamp will be drawn.

    position : tuple, optional
        Coordinates (x, y) for the bottom-left corner of the timestamp text. Default is (10, 30).

    font_scale : float, optional
        Font scale for the text. Default is 0.7.

    thickness : int, optional
        Thickness of the text stroke. Default is 2.

    fmt : str, optional
        Format string for the timestamp (uses `datetime.strftime`). Default is "%Y-%m-%d %H:%M:%S".

    Returns:
    -------
    np.ndarray
        The frame with the timestamp drawn on it.
    """
    # Estimate brightness by converting to grayscale and taking mean pixel value
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)

    # Choose text color: black for bright frames, white for dark ones
    color = (0, 0, 0) if brightness > 127 else (255, 255, 255)

    # Draw timestamp
    timestamp = datetime.now().strftime(fmt)
    cv2.putText(frame, timestamp, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
    return frame