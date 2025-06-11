from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

import numpy as np


@dataclass
class HandState:
    timestamp: Optional[datetime] = datetime.now()

@dataclass
class HandsDetectionResult:
    hands: List[HandState] = field(default_factory=list)
    processed_frame: Optional[np.ndarray] = None