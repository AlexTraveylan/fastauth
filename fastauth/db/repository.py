from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import delete, select, update

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
        session.add(item)
        await session.flush()

        return item

    async def update(self, session: AsyncSession, id_: int, **kwargs) -> T:
        bd_item = await session.get_one(self.__model__, id_)

        for key, value in kwargs.items():
            setattr(bd_item, key, value)

        await session.flush()
        await session.refresh(bd_item)

        return bd_item

    async def get_or_none(self, session: AsyncSession, **kwargs) -> T | None:
        filter_kwargs = [getattr(self.__model__, key) == value for key, value in kwargs.items()]

        statement = select(self.__model__).where(*filter_kwargs)

        response = await session.execute(statement)

        return response.scalars().first()

    async def get_all(self, session: AsyncSession) -> Sequence[T]:
        response = await session.execute(select(self.__model__))
        return response.scalars().all()

    async def delete(self, session: AsyncSession, id_: int) -> bool:
        try:
            item = await session.get_one(self.__model__, id_)
        except NoResultFound:
            return False

        await session.delete(item)

        return True


class UserRepository(Repository[User]):
    __model__ = User


class TokenRepository(Repository[Token]):
    __model__ = Token

    async def delete_expired(self, session: AsyncSession) -> None:
        statement = delete(Token).where(Token.expires_at < datetime.now(UTC))  # type: ignore
        await session.execute(statement)

    async def revoke_all_for_user(self, session: AsyncSession, user_id: int) -> None:
        statement = (
            update(Token)
            .where(Token.user_id == user_id, Token.revoked == False)  # type: ignore[arg-type] # noqa: E712
            .values(revoked=True)
        )
        await session.execute(statement)
