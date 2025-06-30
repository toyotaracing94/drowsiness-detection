from typing import Optional

from pydantic import BaseModel


class DrowsinessEventMetrics(BaseModel):
    drowsiness_event: Optional[str] = None
    yawning_event: Optional[str] = None