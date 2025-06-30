import threading

from backend.hardware.buzzer.base_buzzer import BaseBuzzer


class BuzzerService:
    def __init__(self, buzzer: BaseBuzzer):
        self.buzzer = buzzer
        self.keep_beeping = False
        self.buzzer_function = None
        self.buzzer_thread = None

    def beep_buzzer(self, times : int, duration : int, pause : float, frequency : int):
        """
        This function triggers the buzzer to beep a specified number of times, each with a defined 
        duration, frequency, and pause interval between beeps.
        """
        self.buzzer.beep(times, duration, pause, frequency)

    def start_buzzer(self, buzzer_function: callable):
        """
        This function starts the buzzer function in a new thread, allowing the buzzer
        to run concurrently with the rest of the application without blocking the main thread.
        
        If there is already an active buzzer thread running, it will check if the 
        requested buzzer function is different from the currently active function. 
        If it is, the new function will replace the old one. Otherwise, the function will 
        not restart the thread.

        Parameters
        ----------
        buzzer_function : function
            A function that handles the buzzer behavior (such as calling `beep()` 
            or any other logic for controlling the buzzer). The function will be executed 
            repeatedly in the background thread.

        Notes
        -----
        - The buzzer function is expected to run continuously or in a loop until the
          `stop_buzzer()` method is called.
        - The `start_buzzer()` method prevents multiple threads from being created for
          the same buzzer function. If a thread is already running with the same function,
          it won't create a new thread.
        """
        if self.buzzer_thread and self.buzzer_thread.is_alive():
            if self.buzzer_function != buzzer_function:
                self.buzzer_function = buzzer_function
            return

        self.keep_beeping = True
        self.buzzer_function = buzzer_function
        self.buzzer_thread = threading.Thread(target=self._buzzer_loop, daemon=True)
        self.buzzer_thread.start()

    def stop_buzzer(self):
        """
        This function stops the buzzer function by setting the `keep_beeping` flag to `False`
        and clearing the `buzzer_function` and `drowsiness_stage`. So the actuall function that
        was running the "pseudo-function" of the beep can be putted down without clearing the Thread
        """
        self.keep_beeping = False
        self.buzzer_function = None
        self.buzzer.cleanup()

    def test_buzzer(self):
        """
        This function is just gonna run the first stage of the buzzer to quick test wether
        the buzzer is functional or not 
        """
        self.buzzer.beep_first_stage()

    def _buzzer_loop(self):
        """
        This is the background loop that continuously executes the `buzzer_function` 
        while `keep_beeping` is `True` and a valid `buzzer_function` is set. The function
        is run repeatedly until `stop_buzzer()` is called, which sets `keep_beeping` to `False`.
        """
        while self.keep_beeping and self.buzzer_function:
            self.buzzer_function()
