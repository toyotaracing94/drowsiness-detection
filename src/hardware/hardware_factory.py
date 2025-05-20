import os


def get_camera():
    if os.name == "posix":
        try:
            from src.hardware.camera.rpi_camera import PiCamera
            return PiCamera()
        except ImportError:
            from src.hardware.camera.cv_camera import CVCamera
            return CVCamera()
    else:
        from src.hardware.camera.cv_camera import CVCamera
        return CVCamera()