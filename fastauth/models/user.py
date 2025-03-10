from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from fastauth.db.repository import Repository

if TYPE_CHECKING:
    from fastauth.models.token import Token


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
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # OAuth fields (optional)
    oauth_provider: str | None = None
    oauth_id: str | None = None

    # Relation with the tokens
    tokens: list["Token"] = Relationship(back_populates="user")


class UserRepository(Repository[User]):
    """Repository for user model."""

    __model__ = User
