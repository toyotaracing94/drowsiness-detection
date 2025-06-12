from pydantic import BaseModel


class FacialMetrics(BaseModel):
    ear : float
    mar : float