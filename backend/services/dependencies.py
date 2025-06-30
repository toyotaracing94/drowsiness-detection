from fastapi import Depends
from sqlmodel import Session

from backend.infrastructure.session import get_session
from backend.services.drowsiness_event_service import DrowsinessEventService


def get_drowsiness_event_service(session: Session = Depends(get_session)) -> DrowsinessEventService:
    return DrowsinessEventService(session)