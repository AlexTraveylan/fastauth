from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel

from fastauth.common.exceptions import DatabaseException
from fastauth.common.settings import settings


def _get_async_engine() -> AsyncEngine:
    """Get the async engine for the database."""
    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
    )


async def init_db(engine: Annotated[AsyncEngine, Depends(_get_async_engine)]) -> None:
    """Initialize the database with the defined models."""
    async with engine.begin() as async_conn:
        await async_conn.run_sync(SQLModel.metadata.create_all)


async def get_async_session(
    engine: Annotated[AsyncEngine, Depends(_get_async_engine)],
) -> AsyncGenerator[AsyncSession, None]:
    """Yield an async session."""
    async_session = async_sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise DatabaseException("An error occurred during the session") from e
        finally:
            await session.close()
