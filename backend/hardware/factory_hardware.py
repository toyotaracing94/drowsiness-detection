import os


def get_camera():
    if os.name == "posix":
        from src.hardware.camera.rpi_camera import RPiCamera
        return RPiCamera()
    from backend.hardware.camera.cv_camera import CVCamera
    return CVCamera()

def get_buzzer():
    if os.name == "posix":
        from src.hardware.buzzer.rpi_buzzer import RaspberryBuzzer
        return RaspberryBuzzer()
    from backend.hardware.buzzer.windows_buzzer import WindowsBuzzer
    return WindowsBuzzer()