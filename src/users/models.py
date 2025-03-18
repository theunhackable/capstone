from datetime import datetime
from typing import Literal, Optional, cast

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Boolean, Column, Enum, Integer, String
from werkzeug.security import check_password_hash, generate_password_hash

from src.app import db


class User(db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(Enum("admin", "client", "doctor"), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    address = Column(String(255))
    profile_desc = Column(String(500))
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)  # Hashed password
    status = Column(Enum("available", "not"), default="available")
    blocked = Column(Boolean, default=False)

    def __init__(
        self,
        role,
        first_name,
        last_name,
        address,
        profile_desc,
        email,
        password,
        status="available",
        blocked=False,
    ):
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.profile_desc = profile_desc
        self.email = email
        self.password_hash = self.hash_password(password)
        self.status = status
        self.blocked = blocked

    # Hash and salt the password
    def hash_password(self, password: str) -> str:
        return generate_password_hash(password)

    # Check the hashed password
    def check_password(self, password: str) -> bool:
        return check_password_hash(cast(str, self.password_hash), password)

    # Convert User object to dictionary
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "role": self.role,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "address": self.address,
            "profile_desc": self.profile_desc,
            "email": self.email,
            "status": self.status,
            "blocked": self.blocked,
        }


# Base model for User with common attributes
class UserBase(BaseModel):
    role: Literal["admin", "client", "doctor"]
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    address: Optional[str] = Field(None, max_length=255)
    profile_desc: Optional[str] = Field(None, max_length=500)
    email: EmailStr
    status: Optional[Literal["available", "not"]] = "available"
    blocked: Optional[bool] = False


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=255)
    profile_desc: Optional[str] = Field(None, max_length=500)
    status: Optional[Literal["available", "not"]]
    blocked: Optional[bool]


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True  # Enable ORM mode to work with SQLAlchemy models
