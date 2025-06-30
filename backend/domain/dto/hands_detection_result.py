from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional

import numpy as np


@dataclass
class HandState:
    timestamp: Optional[datetime] = datetime.now()
    hand_landmark: Optional[Any] = None

@dataclass
class HandsDetectionResult:
    hands: List[HandState] = field(default_factory=list)
    debug_frame: Optional[np.ndarray] = None