from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional


@dataclass
class HandState:
    timestamp: Optional[datetime] = datetime.now()
    hand_landmark: Optional[Any] = None

@dataclass
class HandsDetectionResult:
    hands: List[HandState] = field(default_factory=list)