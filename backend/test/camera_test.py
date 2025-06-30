import os
import time

import cv2

# Conditionally import PiCamera2
if os.name == 'posix':
    try:
        from picamera2 import Picamera2
        PI_CAMERA_AVAILABLE = True
    except ImportError:
        PI_CAMERA_AVAILABLE = False
else:
    PI_CAMERA_AVAILABLE = False

def test_opencv_camera_and_capture(index=0):
    print("Using OpenCV camera at index", index)
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print("Failed to open OpenCV camera.")
        return

    ret, frame = cap.read()
    if ret and frame is not None:
        cv2.imshow("test_capture", frame)
        print("Captured image from OpenCV camera.")
        cv2.waitKey(5000)  # Wait 5 seconds while showing the image
        cv2.destroyAllWindows()
    else:
        print("Failed to capture frame from OpenCV camera.")

    cap.release()
    print("Released OpenCV camera.")

def test_picamera2_and_capture():
    print("Using PiCamera2...")
    if not PI_CAMERA_AVAILABLE:
        print("Picamera2 is not installed or not available on this system.")
        return

    try:
        picam2 = Picamera2()
        picam2.start()
        time.sleep(1)

        frame = picam2.capture_array()
        if frame is not None:
            cv2.imshow("test_capture", frame)
            print("Captured image from PiCamera2.")
            cv2.waitKey(5000)
            cv2.destroyAllWindows()
        else:
            print("Failed to capture frame from PiCamera2.")

        picam2.close()
        print("Closed PiCamera2.")
    except Exception as e:
        print("Failed to use PiCamera2:", e)

if __name__ == "__main__":
    print("Operating system:", os.name)

    if os.name == 'nt':
        test_opencv_camera_and_capture()

    elif os.name == 'posix':
        if PI_CAMERA_AVAILABLE:
            test_picamera2_and_capture()
        else:
            test_opencv_camera_and_capture()
