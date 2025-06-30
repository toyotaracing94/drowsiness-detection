import winsound
from time import sleep

from backend.hardware.buzzer.base_buzzer import BaseBuzzer
from backend.utils.logging import logging_default


class WindowsBuzzer(BaseBuzzer):
    def __init__(self):
        self.setup()

    def setup(self) -> None:
        # In Windows, there are no special requirement whatsoever
        # We can directly use the `winsound` package provided by Python
        logging_default.info("Setting up Buzzer in Windows")
        logging_default.info("Triggering the first beep.")

        # Just gonna sound this to make sure everythings ok
        winsound.Beep(2000, 200)
        winsound.Beep(2000, 200)
    

    def beep(self, times : int, duration : int, pause : int, frequency: int = 1000):
        """
        Beeps the buzzer in a periodic way

        '''
            t0 ____ x _____ ..... tn
        '''

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
            winsound.Beep(frequency, duration)
            sleep(pause)

    def beep_first_stage(self):
        """
        Stage 1: light drowsiness alert — slow beeps.
        """
        self.beep(1, 1000, 1)

    def beep_second_stage(self):
        """
        Stage 2: light drowsiness alert — medium beeps.
        """
        self.beep(1, 1000, 0.5)

    def beep_third_stage(self):
        """
        Stage 3: light drowsiness alert — fast beeps.
        """
        self.beep(1, 1000, 0.1)

    def cleanup(self):
        pass

    

    




