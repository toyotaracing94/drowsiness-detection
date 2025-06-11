from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

import numpy as np


@dataclass
class PhoneState:
    is_calling: bool = False
    distance: Optional[float] = None
    timestamp: Optional[datetime] = datetime.now()

@dataclass
class PhoneDetectionResult:
    detection: List[PhoneState] = field(default_factory=list)
    processed_frame: Optional[np.ndarray] = None