from gpiozero import Buzzer
from gpiozero.pins.native import NativeFactory
from time import sleep
from src.utils.logging import logging_default

import gpiozero
gpiozero.Device.pin_factory = NativeFactory()

class RaspberryBuzzer:
    def __init__(self, pin: int = 23):
        self.pin = pin
        self.buzzer = Buzzer(self.pin)
        logging_default.info("Setting up Buzzer in Raspberry Pi")

    def beep(self, times: int, duration: int, pause: float, frequency: int = None):
        """
        Beeps the buzzer in a periodic way.
        Parameters
        ----------
        times : int
            Number of beeps
        duration : int
            Beep duration in milliseconds
        pause : float
            Pause between beeps in seconds
        frequency : int
            Unused (gpiozero Buzzer is digital on/off)
        """
        for _ in range(times):
            self.buzzer.on()
            sleep(duration / 1000.0)
            self.buzzer.off()
            sleep(pause)

    def beep_first_stage(self):
        """Stage 1: light drowsiness alert — slow beeps."""
        self.beep(1, 1000, 1)

    def beep_second_stage(self):
        """Stage 2: medium drowsiness alert — medium beeps."""
        self.beep(1, 1000, 0.5)

    def beep_third_stage(self):
        """Stage 3: severe drowsiness alert — fast beeps."""
        self.beep(1, 1000, 0.1)

    def cleanup(self):
        """Turns off the buzzer and releases GPIO resources."""
        self.buzzer.off()
