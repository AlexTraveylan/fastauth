from datetime import UTC, datetime
from enum import Enum

from sqlmodel import Column, DateTime, Field, SQLModel


class TokenType(str, Enum):
    """Token type."""

    ACCESS = "access"
    REFRESH = "refresh"


class Token(SQLModel, table=True):
    """Data model for authentication tokens.

    This model represents the JWT tokens stored for session management
    and the refresh token mechanism.
    """

    __tablename__ = "tokens"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(index=True)
    token_type: TokenType
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    revoked: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )

    # Relation with the user
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
