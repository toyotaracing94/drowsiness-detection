from time import sleep

from gpiozero import Buzzer, Device
from gpiozero.pins.lgpio import LGPIOFactory

from backend.hardware.buzzer.base_buzzer import BaseBuzzer
from backend.utils.logging import logging_default

# Set the pin factory for Raspberry Pi 5 compatibility
Device.pin_factory = LGPIOFactory()

class RaspberryBuzzer(BaseBuzzer):
    def __init__(self, pin: int = 23):
        self.pin = pin
        self.buzzer = Buzzer(self.pin)
        logging_default.info("Setting up Buzzer on Raspberry Pi 5 using lgpio")

    def beep(self, times: int, duration: int, pause: float, frequency: int = None):
        for _ in range(times):
            self.buzzer.on()
            sleep(duration / 1000.0)
            self.buzzer.off()
            sleep(pause)

    def beep_first_stage(self):
        self.beep(1, 1000, 1)

    def beep_second_stage(self):
        self.beep(1, 1000, 0.5)

    def beep_third_stage(self):
        self.beep(1, 1000, 0.1)

    def cleanup(self):
        self.buzzer.off()
