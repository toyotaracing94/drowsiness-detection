from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from src.domain.entity.drowsiness_event import DrowsinessEvent
from src.services.dependencies import get_drowsiness_event_service
from src.services.drowsiness_event_service import DrowsinessEventService

router = APIRouter()

@router.get(
    "/",
    description="Retrieve all drowsiness events, sorted by timestamp.",
    response_model=List[DrowsinessEvent]
    )
def list_events(service: DrowsinessEventService = Depends(get_drowsiness_event_service)):
    try:
        events = service.get_all_events()  # Assuming the service method is async
        return events
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the events: {str(e)}"
        )
    
@router.get(
    "/{event_id}",
    description="Retrieve a drowsiness event by ID.",
    response_model=DrowsinessEvent
)
def get_event(event_id: str, service: DrowsinessEventService = Depends(get_drowsiness_event_service)):
    try:
        event = service.get_event_by_id(event_id)
        if event is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Drowsiness event not found"
            )
        return event
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the event: {str(e)}"
        )