from typing import List
from uuid import UUID

from sqlmodel import Session, select

from src.domain.entity.drowsiness_event import DrowsinessEvent


class DrowsinessEventService:
    """
    Service class for managing DrowsinessEvent objects in the database.
    """

    def __init__(self, session: Session):
        """
        Initializes the service with a database session.

        Args:
            session (Session): The SQLAlchemy session to interact with the database.
        """
        self.session = session

    def create_event(self, event: DrowsinessEvent) -> DrowsinessEvent:
        """
        Creates and saves a new DrowsinessEvent to the database.

        Args:
            event (DrowsinessEvent): The event to create and store.

        Returns:
            DrowsinessEvent: The created event with its generated ID.
        """
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event

    def get_event_by_id(self, event_id : str) -> DrowsinessEvent | None:
        """
        Retrieves a DrowsinessEvent by its ID.

        Args:
            event_id (UUID): The ID of the event to retrieve.

        Returns:
            DrowsinessEvent | None: The event if found, otherwise None.
        """
        return self.session.get(DrowsinessEvent, UUID(event_id))

    def get_all_events(self) -> List[DrowsinessEvent]:
        """
        Retrieves all DrowsinessEvent objects, ordered by timestamp (most recent first).

        Returns:
            List[DrowsinessEvent]: A list of all events.
        """
        statement = select(DrowsinessEvent).order_by(DrowsinessEvent.timestamp.desc())
        return self.session.exec(statement).all()

    def delete_event(self, event_id : str) -> bool:
        """
        Deletes a DrowsinessEvent by its ID.

        Args:
            event_id (UUID): The ID of the event to delete.

        Returns:
            bool: True if the event was deleted, otherwise False.
        """
        event = self.session.get(DrowsinessEvent, UUID(event_id))
        if event:
            self.session.delete(event)
            self.session.commit()
            return True
        return False
