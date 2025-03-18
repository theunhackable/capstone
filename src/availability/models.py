from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.app import db


class Availability(db.Model):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doctor_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date_time = Column(DateTime, nullable=False)

    def __init__(self, doctor_id, date_time):
        self.doctor_id = doctor_id
        self.date_time = date_time

    def to_dict(self):
        date_time_val = getattr(self, "date_time")
        data = {
            "id": self.id,
            "doctor_id": self.doctor_id,
            "date_time": self.date_time.isoformat() if date_time_val else None,
        }

        return data


class AvailabilityBase(BaseModel):
    doctor_id: int = Field(..., description="ID of the doctor")
    date_time: datetime = Field(
        ..., description="Date and time of the doctor's availability"
    )


class AvailabilityCreate(AvailabilityBase):
    pass


class AvailabilityUpdate(BaseModel):
    date_time: Optional[datetime] = Field(None, description="Updated date and time")
