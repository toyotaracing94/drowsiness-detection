from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from backend.domain.dto.base_response import StandardResponse
from backend.domain.entity.drowsiness_event import DrowsinessEvent
from backend.services.dependencies import get_drowsiness_event_service
from backend.services.drowsiness_event_service import DrowsinessEventService

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

@router.get(
    "/download/{event_id}",
    description="Download the drowsiness event by Event ID",
    response_model=StandardResponse
)
async def download_image_event(event_id : str, service: DrowsinessEventService = Depends(get_drowsiness_event_service)):
    try:
        file_path, content_type, file_name = service.download_event_image(event_id)
        headers = {'Access-Control-Expose-Headers': 'Content-Disposition'}

        return FileResponse(
            path=file_path,
            media_type=content_type,
            filename=file_name,
            headers=headers
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the event: {str(e)}"
        )

@router.post(
    "/",
    description="Create a new drowsiness event.",
    response_model=DrowsinessEvent
)
def create_event(event: DrowsinessEvent, service: DrowsinessEventService = Depends(get_drowsiness_event_service)):
    try:
        # Creating the event via the service
        created_event = service.create_event(event)
        return created_event
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the event: {str(e)}"
        )

@router.delete(
    "/{event_id}",
    description="Delete a drowsiness event by ID.",
    response_model=dict
)
def delete_event(event_id: str, service: DrowsinessEventService = Depends(get_drowsiness_event_service)):
    try:
        success = service.delete_event(event_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Drowsiness event not found"
            )
        return {"message": "Drowsiness event deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the event: {str(e)}"
        )