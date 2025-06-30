# src/hardware/abstract_camera.py
from abc import ABC, abstractmethod

import numpy as np


class BaseCamera(ABC):
    @abstractmethod
    def get_capture(self) -> tuple[bool, np.ndarray]:
        """
        Returns a tuple of (ret, frame) just like OpenCV,
        where `ret` is a boolean and `frame` is a numpy ndarray (or None).
        """
        pass

    @abstractmethod
    def release(self):
        """
        Optional clean-up method.
        """
        pass
