from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    message: str


class GoogleUserInfo(BaseModel):
    email: EmailStr
    sub: str
    given_name: str | None = None
    name: str | None = None
    family_name: str | None = None
    email_verified: bool = False
