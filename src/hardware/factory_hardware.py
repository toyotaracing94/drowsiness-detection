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

def get_buzzer():
    if os.name == "posix":
        from src.hardware.buzzer.rpi_buzzer import RaspberyBuzzer
        return RaspberyBuzzer()
    else:
        from src.hardware.buzzer.windows_buzzer import WindowsBuzzer
        return WindowsBuzzer()