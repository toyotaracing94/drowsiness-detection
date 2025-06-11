from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

import numpy as np


@dataclass
class FaceDrowsinessState:
    face_id : int = 1
    is_drowsy: bool = False
    is_yawning: bool = False
    ear: Optional[float] = None
    mar: Optional[float] = None
    timestamp: Optional[datetime] = datetime.now()

@dataclass
class DrowsinessDetectionResult:
    faces: List[FaceDrowsinessState] = field(default_factory=list)
    processed_frame: Optional[np.ndarray] = None