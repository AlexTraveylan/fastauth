from collections.abc import AsyncGenerator

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine

from fastauth.common.exceptions import DatabaseException
from fastauth.db.database import get_async_engine, get_async_session
from fastauth.main import app

API_PREFIX = "/api/v1/auth"


@pytest.fixture
async def raw_client(engine: AsyncEngine) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_async_engine] = lambda: engine
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
    app.dependency_overrides.clear()


class TestGetAsyncSession:
    async def test_http_exceptions_propagate_unwrapped(self, engine: AsyncEngine) -> None:
        # Given
        session_generator = get_async_session(engine)
        await anext(session_generator)

        # When / Then
        with pytest.raises(HTTPException):
            await session_generator.athrow(HTTPException(status_code=401))

    async def test_sqlalchemy_errors_become_database_exceptions(self, engine: AsyncEngine) -> None:
        # Given
        session_generator = get_async_session(engine)
        await anext(session_generator)

        # When / Then
        with pytest.raises(DatabaseException):
            await session_generator.athrow(SQLAlchemyError("boom"))


class TestSessionDependencyThroughApp:
    async def test_refresh_with_invalid_token_returns_401(self, raw_client: AsyncClient) -> None:
        # Given
        headers = {"Authorization": "Bearer invalid-token"}

        # When
        response = await raw_client.get(f"{API_PREFIX}/refresh", headers=headers)

        # Then
        assert response.status_code == 401

    async def test_me_with_invalid_token_returns_401(self, raw_client: AsyncClient) -> None:
        # Given
        headers = {"Authorization": "Bearer invalid-token"}

        # When
        response = await raw_client.get(f"{API_PREFIX}/me", headers=headers)

        # Then
        assert response.status_code == 401
