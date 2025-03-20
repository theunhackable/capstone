from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String

from src.app import db


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    doctor_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date_time = Column(DateTime, nullable=False)
    status = Column(
        Enum("pending", "confirmed", "on-going", "completed", "canceled", "up-coming"),
        default="up-coming",
    )
    client_requirements = Column(String(255))

    def __init__(
        self, user_id, doctor_id, date_time, client_requirements, status="up-coming"
    ):
        self.user_id = user_id
        self.doctor_id = doctor_id
        self.date_time = date_time
        self.status = status
        self.client_requirements = client_requirements

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "doctor_id": self.doctor_id,
            "date_time": self.date_time.isoformat(),
            "status": self.status,
            "client_requirements": self.client_requirements,
        }


class AppointmentBase(BaseModel):
    user_id: int = Field(..., gt=0, description="ID of the client (must be positive)")
    doctor_id: int = Field(..., gt=0, description="ID of the doctor (must be positive)")
    date_time: datetime = Field(
        ..., description="Date and time of the appointment (ISO 8601 format)"
    )
    status: Literal["up-coming", "on-going", "completed", "canceled"] = Field(
        "up-coming", description="Status of the appointment"
    )
    client_requirements: Optional[str] = Field(
        None,
        max_length=500,
        description="Special requirements from the client (max 500 characters)",
    )


# ✅ Model for creating an appointment
class AppointmentCreate(AppointmentBase):
    pass


# ✅ Model for updating an appointment status
class AppointmentUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Update status of the appointment")
