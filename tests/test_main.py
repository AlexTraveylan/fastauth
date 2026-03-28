from httpx import AsyncClient


class TestRoot:
    async def test_root_returns_running_message(self, client: AsyncClient) -> None:
        # Given
        # When
        response = await client.get("/")

        # Then
        assert response.status_code == 200
        assert response.json() == {"message": "Server is running"}
