from fastapi import APIRouter, HTTPException

from backend.domain.dto.base_response import StandardResponse
from backend.domain.dto.buzzer_dto import BeepRequest
from backend.hardware.buzzer.base_buzzer import BaseBuzzer


def buzzer_router(buzzer: BaseBuzzer):
    router = APIRouter()

    @router.post(
        "/beep", 
        summary="Trigger a buzzer beep", 
        response_model=StandardResponse,
        description="""
        Triggers the buzzer to beep a specified number of times, each with a defined 
        duration, frequency, and pause interval between beeps.
        """
    )
    def trigger_beep(req: BeepRequest):
        try:
            buzzer.beep(req.times, req.duration, req.pause, req.frequency)
            return StandardResponse(
                status="success",
                message=f"Beeped {req.times} time(s)."
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Buzzer failed: {str(e)}")

    return router
