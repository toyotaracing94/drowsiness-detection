from typing import List

from fastapi import APIRouter, Depends

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
    return service.get_all_events()

@router.get(
    "/{event_id}",
    description="Retrieve a drowsiness event by ID.",
    response_model=DrowsinessEvent
)
def get_event(event_id: str, service: DrowsinessEventService = Depends(get_drowsiness_event_service)):
    return service.get_event_by_id(event_id)