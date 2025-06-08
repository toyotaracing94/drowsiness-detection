# src/hardware/abstract_buzzer.py
from abc import ABC, abstractmethod


class BaseBuzzer(ABC):
    @abstractmethod
    def beep(self, times: int, duration: int, pause: float, frequency: int = None):
        pass

    @abstractmethod
    def beep_first_stage(self):
        pass

    @abstractmethod
    def beep_second_stage(self):
        pass

    @abstractmethod
    def beep_third_stage(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass
