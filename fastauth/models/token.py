from datetime import UTC, datetime
from enum import Enum
from uuid import UUID

from sqlmodel import Column, DateTime, Field, SQLModel


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class Token(SQLModel, table=True):
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
    user_id: UUID = Field(foreign_key="users.id", ondelete="CASCADE")

    @property
    def is_expired(self) -> bool:
        expires = self.expires_at if self.expires_at.tzinfo else self.expires_at.replace(tzinfo=UTC)
        return expires < datetime.now(UTC)
