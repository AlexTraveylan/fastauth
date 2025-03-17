from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str
    password: str


class Token(BaseModel):
    """Schema for token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Schema for user data in responses."""

    email: str
    username: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    """Schema for simple message responses."""

    message: str


class GoogleUserInfo(BaseModel):
    """Schema for Google user info."""

    email: EmailStr
    email_verified: bool
    name: str
    family_name: str
    sub: str
