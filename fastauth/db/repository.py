from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import delete, select

from fastauth.models import Token, User


class Repository[T]:
    """Repository pattern for database operations.

    Exemple for User, when user is a SQLModel:
    >>> class UserRepository(Repository[User]):
    >>>     __model__ = User
    """

    __model__: type[T]

    @staticmethod
    async def create(session: AsyncSession, item: T) -> T:
        """Create an item in the database."""
        session.add(item)
        await session.flush()

        return item

    async def update(self, session: AsyncSession, id_: int, **kwargs) -> T:
        """Update an item in the database."""
        bd_item = await session.get_one(self.__model__, id_)

        for key, value in kwargs.items():
            setattr(bd_item, key, value)

        await session.flush()
        await session.refresh(bd_item)

        return bd_item

    async def get_or_none(self, session: AsyncSession, **kwargs) -> T | None:
        """Get an item from the database or return None if it doesn't exist."""
        filter_kwargs = [
            getattr(self.__model__, key) == value for key, value in kwargs.items()
        ]

        statement = select(self.__model__).where(*filter_kwargs)

        response = await session.execute(statement)

        return response.scalars().first()

    async def get_all(self, session: AsyncSession) -> Sequence[T]:
        """Get all items from the database."""
        response = await session.execute(select(self.__model__))
        return response.scalars().all()

    async def delete(self, session: AsyncSession, id_: int) -> bool:
        """Delete an item from the database."""
        try:
            item = await session.get_one(self.__model__, id_)
        except NoResultFound:
            return False

        await session.delete(item)

        return True


class UserRepository(Repository[User]):
    """Repository for user model."""

    __model__ = User


class TokenRepository(Repository[Token]):
    """Repository for token model."""

    __model__ = Token

    async def delete_expired(self, session: AsyncSession) -> None:
        """Delete expired tokens."""
        statement = delete(Token).where(Token.expires_at < datetime.now(UTC))  # type: ignore
        await session.execute(statement)
