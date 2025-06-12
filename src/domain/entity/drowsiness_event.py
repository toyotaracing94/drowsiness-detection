from datetime import datetime
from uuid import UUID

from sqlmodel import Column, Field, SQLModel, String
from uuid6 import uuid7


class DrowsinessEvent(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid7, primary_key=True, index=True)
    vehicle_identification: str = Field(..., sa_column=Column(String, nullable=False))
    timestamp: datetime = Field(default_factory=datetime.now)
    image: str = Field(..., sa_column=Column(String, nullable=False))
    ear: float
    mar: float
    event_type: str = Field(..., sa_column=Column(String, nullable=False))
