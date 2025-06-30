from threading import Lock
from typing import Optional

import numpy as np

from backend.domain.dto.drowsiness_event_metrics import DrowsinessEventMetrics
from backend.domain.dto.facial_metrics import FacialMetrics


class FrameBuffer:
    def __init__(self):
        self.raw_frame : np.ndarray = None
        self.processed_frame : np.ndarray = None
        self.debug_frame : np.ndarray = None
        self.facial_metrics: Optional[FacialMetrics] = None
        self.drowsiness_event_metrics : Optional[DrowsinessEventMetrics] = None
        
        self.raw_lock = Lock()
        self.processed_lock = Lock()
        self.debug_lock = Lock()
        self.facial_metrics_lock = Lock()
        self.drowsiness_event_lock = Lock()

    def update_raw(self, frame):
        """Update the raw frame."""
        with self.raw_lock:
            self.raw_frame = frame

    def get_raw(self):
        """Get the raw frame."""
        with self.raw_lock:
            return self.raw_frame

    def update_processed(self, frame):
        """Update the processed frame."""
        with self.processed_lock:
            self.processed_frame = frame

    def get_processed(self):
        """Get the processed frame."""
        with self.processed_lock:
            return self.processed_frame
        
    def update_debug(self, frame):
        """Update the debug frame."""
        with self.debug_lock:
            self.debug_frame = frame

    def get_debug(self):
        """Get the debug frame."""
        with self.debug_lock:
            return self.debug_frame
        
    def update_drowsiness_event_recent(self, drowsiness_event : str, yawning_event : str):
        """Update the recent detected of drowsiness and yawning event"""
        with self.drowsiness_event_lock:
            self.drowsiness_event_metrics = DrowsinessEventMetrics(drowsiness_event=drowsiness_event, yawning_event=yawning_event)
    
    def get_drowsiness_event_recent(self) -> Optional[DrowsinessEventMetrics]:
        """Get the current recent event detected"""
        with self.drowsiness_event_lock:
            return self.drowsiness_event_metrics

    def update_facial_metrics(self, ear: float = 0.0, mar: float = 0.0, is_drowsy : bool = False, is_calling : bool = False):
        """Update the EAR and MAR values using FacialMetrics class."""
        with self.facial_metrics_lock:
            self.facial_metrics = FacialMetrics(ear=ear, mar=mar, is_drowsy=is_drowsy, is_calling=is_calling)

    def get_facial_metrics(self) -> Optional[FacialMetrics]:
        """Get the current FacialMetrics (EAR and MAR)."""
        with self.facial_metrics_lock:
            return self.facial_metrics