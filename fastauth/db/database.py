from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from fastauth.config.settings import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Initialize the database with the defined models."""
    async with engine.begin() as conn:
        # SQLModel.metadata.drop_all(conn)  # Uncomment to reset the database
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    """Create a database session for FastAPI dependencies."""
    async with async_session() as session:
        yield session
