import cv2

# Test untuk mengecek kamera yang terhubung
for i in range(5):  # Coba 5 kamera pertama
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Kamera {i} tersedia")
        cap.release()
    else:
        print(f"Kamera {i} tidak tersedia")
