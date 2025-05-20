import Rpi.GPIO as GPIO
from time import sleep
from src.utils.logging import logging_default


class RaspberyBuzzer:
    def __init__(self, pin):
        self.pin = pin
        self.setup()

    def setup(self):
        logging_default.info("Setting up Buzzer in Raspberry Pi")
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        logging_default.info("Triggering the first beep.")

        # Also gonna souund this
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)

    def beep(self, times: int, duration : int, pause : int, frequency: int):
        """
        Beeps the buzzer in a periodic way

        x means the beep happen, and ____ is the pause
        For now, wether In windows or linux Raspberry Pi, 
        frequency will be hardcoded as there is no meaning to have the ability

        Parameters
        ----------
        times : int
            How many number of beeps will happen in a sequence
        duration : float
            Time buzzer will stays ON in each beep (in miliseconds)
        pause : float
            Pause between each beeps, this will decide wether it is slow or fast temp. In second
        """
        for _ in range(times):
            GPIO.output(self.pin, GPIO.HIGH)
            sleep(duration / 1000.0)
            GPIO.output(self.pin, GPIO.LOW)
            sleep(pause)
    
    def beep_first_stage(self):
        """
        Stage 1: light drowsiness alert — slow beeps.
        """
        self.beep(1, 1000, 1)

    def beep_second_stage(self):
        """
        Stage 2: medium drowsiness alert — medium beeps.
        """
        self.beep(1, 1000, 0.5)

    def beep_third_stage(self):
        """
        Stage 3: severe drowsiness alert — fast beeps.
        """
        self.beep(1, 1000, 0.1)

    def cleanup(self):
        """
        Turns off the buzzer and cleans up the GPIO state.
        """
        GPIO.output(self.buzzer_pin, GPIO.LOW)
        GPIO.cleanup()