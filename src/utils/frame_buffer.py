from threading import Lock
from typing import Optional

import numpy as np

from src.domain.dto.facial_metrics import FacialMetrics


class FrameBuffer:
    def __init__(self):
        self.raw_frame : np.ndarray = None
        self.processed_frame : np.ndarray = None
        self.facial_metrics: Optional[FacialMetrics] = None
        self.lock = Lock()

    def update_raw(self, frame):
        """Update the raw frame."""
        with self.lock:
            self.raw_frame = frame

    def get_raw(self):
        """Get the raw frame."""
        with self.lock:
            return self.raw_frame

    def update_processed(self, frame):
        """Update the processed frame."""
        with self.lock:
            self.processed_frame = frame

    def get_processed(self):
        """Get the processed frame."""
        with self.lock:
            return self.processed_frame
    
    def update_facial_metrics(self, ear: float = 0.0, mar: float = 0.0, is_drowsy : bool = False, is_calling : bool = False):
        """Update the EAR and MAR values using FacialMetrics class."""
        with self.lock:
            self.facial_metrics = FacialMetrics(ear=ear, mar=mar, is_drowsy=is_drowsy, is_calling=is_calling)

    def get_facial_metrics(self) -> Optional[FacialMetrics]:
        """Get the current FacialMetrics (EAR and MAR)."""
        with self.lock:
            return self.facial_metrics