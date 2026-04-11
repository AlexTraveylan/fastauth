from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel

from fastauth.common.exceptions import DatabaseException
from fastauth.common.settings import settings


def _build_async_uri(raw_uri: str) -> str:
    if raw_uri.startswith("postgresql+asyncpg://"):
        return raw_uri

    if raw_uri.startswith("postgresql://"):
        return raw_uri.replace("postgresql://", "postgresql+asyncpg://", 1)

    return raw_uri


def get_async_engine() -> AsyncEngine:
    return create_async_engine(
        _build_async_uri(settings.FASTAUTH_POSTGRES_POOLER_CONNECTION_STRING),
        echo=settings.DEBUG,
        future=True,
        connect_args={
            "ssl": "require",
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0,
        },
    )


async def init_db(engine: Annotated[AsyncEngine, Depends(get_async_engine)]) -> None:
    async with engine.begin() as async_conn:
        await async_conn.run_sync(SQLModel.metadata.create_all)


async def get_async_session(
    engine: Annotated[AsyncEngine, Depends(get_async_engine)],
) -> AsyncGenerator[AsyncSession, None]:
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
