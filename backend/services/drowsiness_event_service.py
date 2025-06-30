import datetime
import os
from typing import List
from uuid import UUID

from sqlmodel import Session, select

from backend.domain.entity.drowsiness_event import DrowsinessEvent
from backend.utils.logging import logging_default


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
        try:
            logging_default.info(f"Creating new DrowsinessEvent: "
                        f"ID: {event.id}, Vehicle: {event.vehicle_identification}, "
                        f"Timestamp: {event.timestamp}, Event Type: {event.event_type}")
            
            if isinstance(event.id, str):
                event.id = UUID(event.id)
            if isinstance(event.timestamp, str):
                event.timestamp = datetime.datetime.fromisoformat(event.timestamp)

            self.session.add(event)
            self.session.commit()
            self.session.refresh(event)
            return event
        except Exception as e:
            logging_default.error(f"Error while creating DrowsinessEvent: {str(e)}")
            raise

    def get_event_by_id(self, event_id : str) -> DrowsinessEvent | None:
        """
        Retrieves a DrowsinessEvent by its ID.

        Args:
            event_id (UUID): The ID of the event to retrieve.

        Returns:
            DrowsinessEvent | None: The event if found, otherwise None.
        """
        try:
            logging_default.info(f"Getting DrowsinessEvent ID: {event_id}")
            event = self.session.get(DrowsinessEvent, UUID(event_id))
            if event:
                logging_default.info(f"Fetched DrowsinessEvent: "
                            f"ID: {event.id}, Vehicle: {event.vehicle_identification}, "
                            f"Timestamp: {event.timestamp}, Event Type: {event.event_type}")
            else:
                logging_default.warning(f"DrowsinessEvent with ID {event_id} not found.")
            return event
        except Exception as e:
            logging_default.error(f"Error while fetching DrowsinessEvent with ID {event_id}: {str(e)}")
            raise
    
    def download_event_image(self, event_id: str) -> tuple[str, str, str]:
        """
        Retrieves the path and metadata of the image for the given event.

        Args:
            event_id (str): The ID of the event.

        Returns:
            tuple: (file_path, content_type, file_name)
        """
        try:
            logging_default.info(f"Download image for DrowsinessEvent ID: {event_id}")
            event = self.get_event_by_id(event_id)
            if not event or not event.image:
                logging_default.warning(f"No DrowsinessEvent found with ID: {event_id}")
                raise FileNotFoundError("Image not found for the event.")

            file_path = event.image
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Image file does not exist at path: {file_path}")

            content_type = "image/png"
            file_name = f"{event.id}_{event.event_type}_ear_{event.ear:.2f}_mar_{event.mar:.2f}.png"
            return file_path, content_type, file_name

        except Exception as e:
            logging_default.error(f"Error while downloading image for event {event_id}: {str(e)}")
            raise

    def get_all_events(self) -> List[DrowsinessEvent]:
        """
        Retrieves all DrowsinessEvent objects, ordered by timestamp (most recent first).

        Returns:
            List[DrowsinessEvent]: A list of all events.
        """
        try:
            logging_default.info("Getting DrowsinessEvent")
            statement = select(DrowsinessEvent).order_by(DrowsinessEvent.timestamp.desc())
            events = self.session.exec(statement).all()
            return events
        except Exception as e:
            logging_default.error(f"Error while fetching all DrowsinessEvent records: {str(e)}")
            raise

    def delete_event(self, event_id : str) -> bool:
        """
        Deletes a DrowsinessEvent by its ID.

        Args:
            event_id (UUID): The ID of the event to delete.

        Returns:
            bool: True if the event was deleted, otherwise False.
        """
        try:
            logging_default.info(f"Received delete_event request with event_id: {event_id}")

            event = self.session.get(DrowsinessEvent, UUID(event_id))
            if event:
                self.session.delete(event)
                self.session.commit()
                logging_default.info(f"DrowsinessEvent deleted successfully: ID: {event.id}")
                return True
            logging_default.warning(f"DrowsinessEvent with ID {event_id} not found for deletion.")
            return False
        except Exception as e:
            logging_default.error(f"Error while deleting DrowsinessEvent with ID {event_id}: {str(e)}")
            raise