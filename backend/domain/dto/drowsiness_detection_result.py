from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional

import numpy as np


@dataclass
class FaceDrowsinessState:
    face_id: int = 1
    is_drowsy: bool = False
    is_yawning: bool = False
    ear: Optional[float] = None
    mar: Optional[float] = None
    x_angle: Optional[float] = None
    y_angle: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    face_landmark: Optional[Any] = None

@dataclass
class DrowsinessDetectionResult:
    faces: List[FaceDrowsinessState] = field(default_factory=list)
    drowsiness_event: Optional[str] = None
    yawning_event: Optional[str] = None
    debug_frame: Optional[np.ndarray] = None