from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel

from fastauth.common.settings import settings


def get_async_engine() -> AsyncEngine:
    """Get the async engine for the database."""
    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
    )


async def init_db() -> None:
    """Initialize the database with the defined models."""
    async_engine = get_async_engine()

    async with async_engine.begin() as async_conn:
        await async_conn.run_sync(SQLModel.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async session."""
    async_session = async_sessionmaker(
        bind=get_async_engine(),
        autoflush=False,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session
