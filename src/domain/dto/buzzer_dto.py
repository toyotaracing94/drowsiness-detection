from pydantic import BaseModel, Field


class BeepRequest(BaseModel):
    times: int = Field(..., gt=0, description="How many times to beep")
    duration: int = Field(default=1000, gt=0, description="Duration of each beep in milliseconds")
    pause: float = Field(..., ge=0.0, description="Pause between beeps in seconds")
    frequency: int = Field(default=1000, ge=100, description="Frequency of the beep")