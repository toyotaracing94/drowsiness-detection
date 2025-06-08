from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.hardware.buzzer.base_buzzer import BaseBuzzer


def buzzer_router(buzzer: BaseBuzzer):
    router = APIRouter()

    class BeepRequest(BaseModel):
        times: int = Field(..., gt=0, description="How many times to beep")
        duration: int = Field(default=1000, gt=0, description="Duration of each beep in milliseconds")
        pause: float = Field(..., ge=0.0, description="Pause between beeps in seconds")
        frequency: int = Field(default=1000, ge=100, description="Frequency of the beep (ignored on some platforms)")

    @router.post("/beep", summary="Trigger a buzzer beep")
    def trigger_beep(req: BeepRequest):
        try:
            buzzer.beep(req.times, req.duration, req.pause, req.frequency)
            return {"status": "success", "message": f"Beeped {req.times} time(s)."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Buzzer failed: {str(e)}")

    return router
