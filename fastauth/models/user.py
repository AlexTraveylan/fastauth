from __future__ import annotations

from datetime import UTC, datetime

from sqlmodel import Column, DateTime, Field, SQLModel


class User(SQLModel, table=True):
    """Data model for system users.

    This model represents the necessary information for authentication
    and user management in the FastAuth system.
    """

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )

    # OAuth fields (optional)
    oauth_provider: str | None = None
    oauth_id: str | None = None
