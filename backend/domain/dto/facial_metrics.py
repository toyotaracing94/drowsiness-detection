from pydantic import BaseModel


class FacialMetrics(BaseModel):
    ear : float = 0.0
    mar : float = 0.0
    is_drowsy : bool = False
    is_yawning : bool = False