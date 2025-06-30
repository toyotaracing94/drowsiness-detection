from fastapi import APIRouter, HTTPException

from backend.domain.dto.base_response import StandardResponse
from backend.domain.dto.buzzer_dto import BeepRequest
from backend.services.buzzer_service import BuzzerService


def buzzer_router(buzzer_service: BuzzerService):
    router = APIRouter()

    @router.get(
        "/test", 
        summary="Test a buzzer beep", 
        response_model=StandardResponse,
        description="""
        Quick test to check whether the buzzer is actually functional or not 
        """
    )
    async def trigger_beep_test():
        try:
            buzzer_service.test_buzzer()
            return StandardResponse(
                status="success",
                message="Beeped"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Buzzer failed: {str(e)}")

    @router.post(
        "/beep", 
        summary="Trigger a buzzer beep", 
        response_model=StandardResponse,
        description="""
        Triggers the buzzer to beep a specified number of times, each with a defined 
        duration, frequency, and pause interval between beeps.
        """
    )
    async def trigger_beep(req: BeepRequest):
        try:
            buzzer_service.beep_buzzer(req.times, req.duration, req.pause, req.frequency)
            return StandardResponse(
                status="success",
                message=f"Beeped {req.times} time(s)."
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Buzzer failed: {str(e)}")

    return router
