from faker import Faker
from httpx import AsyncClient

fake = Faker()

API_PREFIX = "/api/v1/auth"


async def register_and_login(client: AsyncClient) -> dict:
    username = fake.user_name()
    password = fake.password(length=12)
    email = fake.email()

    await client.post(
        f"{API_PREFIX}/register",
        json={"email": email, "username": username, "password": password},
    )

    login_response = await client.post(
        f"{API_PREFIX}/login",
        data={"username": username, "password": password},
    )

    tokens = login_response.json()
    return {
        "username": username,
        "password": password,
        "email": email,
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
    }


class TestRegister:
    async def test_register_success(self, client: AsyncClient) -> None:
        # Given
        payload = {
            "email": fake.email(),
            "username": fake.user_name(),
            "password": fake.password(length=12),
        }

        # When
        response = await client.post(f"{API_PREFIX}/register", json=payload)

        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == payload["email"]
        assert data["username"] == payload["username"]

    async def test_register_duplicate_email(self, client: AsyncClient) -> None:
        # Given
        email = fake.email()
        base_payload = {"email": email, "username": fake.user_name(), "password": fake.password(length=12)}
        await client.post(f"{API_PREFIX}/register", json=base_payload)

        # When
        duplicate_payload = {"email": email, "username": fake.user_name(), "password": fake.password(length=12)}
        response = await client.post(f"{API_PREFIX}/register", json=duplicate_payload)

        # Then
        assert response.status_code == 409

    async def test_register_duplicate_username(self, client: AsyncClient) -> None:
        # Given
        username = fake.user_name()
        base_payload = {"email": fake.email(), "username": username, "password": fake.password(length=12)}
        await client.post(f"{API_PREFIX}/register", json=base_payload)

        # When
        duplicate_payload = {"email": fake.email(), "username": username, "password": fake.password(length=12)}
        response = await client.post(f"{API_PREFIX}/register", json=duplicate_payload)

        # Then
        assert response.status_code == 409

    async def test_register_invalid_email(self, client: AsyncClient) -> None:
        # Given
        payload = {"email": "not-an-email", "username": fake.user_name(), "password": fake.password(length=12)}

        # When
        response = await client.post(f"{API_PREFIX}/register", json=payload)

        # Then
        assert response.status_code == 422

    async def test_register_password_too_short(self, client: AsyncClient) -> None:
        # Given
        payload = {"email": fake.email(), "username": fake.user_name(), "password": "short"}

        # When
        response = await client.post(f"{API_PREFIX}/register", json=payload)

        # Then
        assert response.status_code == 422

    async def test_register_username_too_short(self, client: AsyncClient) -> None:
        # Given
        payload = {"email": fake.email(), "username": "ab", "password": fake.password(length=12)}

        # When
        response = await client.post(f"{API_PREFIX}/register", json=payload)

        # Then
        assert response.status_code == 422


class TestLogin:
    async def test_login_success(self, client: AsyncClient) -> None:
        # Given
        username = fake.user_name()
        password = fake.password(length=12)
        await client.post(
            f"{API_PREFIX}/register",
            json={"email": fake.email(), "username": username, "password": password},
        )

        # When
        response = await client.post(
            f"{API_PREFIX}/login",
            data={"username": username, "password": password},
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient) -> None:
        # Given
        username = fake.user_name()
        await client.post(
            f"{API_PREFIX}/register",
            json={"email": fake.email(), "username": username, "password": fake.password(length=12)},
        )

        # When
        response = await client.post(
            f"{API_PREFIX}/login",
            data={"username": username, "password": "wrongpassword"},
        )

        # Then
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient) -> None:
        # Given
        # When
        response = await client.post(
            f"{API_PREFIX}/login",
            data={"username": fake.user_name(), "password": fake.password(length=12)},
        )

        # Then
        assert response.status_code == 401


class TestMe:
    async def test_me_with_valid_token(self, client: AsyncClient) -> None:
        # Given
        user_data = await register_and_login(client)

        # When
        response = await client.get(
            f"{API_PREFIX}/me",
            headers={"Authorization": f"Bearer {user_data['access_token']}"},
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]

    async def test_me_with_invalid_token(self, client: AsyncClient) -> None:
        # Given
        # When
        response = await client.get(
            f"{API_PREFIX}/me",
            headers={"Authorization": "Bearer invalid-token"},
        )

        # Then
        assert response.status_code == 401

    async def test_me_without_token(self, client: AsyncClient) -> None:
        # Given
        # When
        response = await client.get(f"{API_PREFIX}/me")

        # Then
        assert response.status_code == 401

    async def test_me_with_revoked_token(self, client: AsyncClient) -> None:
        # Given
        user_data = await register_and_login(client)
        await client.post(
            f"{API_PREFIX}/logout",
            headers={"Authorization": f"Bearer {user_data['access_token']}"},
        )

        # When
        response = await client.get(
            f"{API_PREFIX}/me",
            headers={"Authorization": f"Bearer {user_data['access_token']}"},
        )

        # Then
        assert response.status_code == 401


class TestRefresh:
    async def test_refresh_success_with_rotation(self, client: AsyncClient) -> None:
        # Given
        user_data = await register_and_login(client)

        # When
        response = await client.get(
            f"{API_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {user_data['refresh_token']}"},
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["access_token"] != user_data["access_token"]
        assert data["refresh_token"] != user_data["refresh_token"]

    async def test_old_refresh_token_invalid_after_rotation(self, client: AsyncClient) -> None:
        # Given
        user_data = await register_and_login(client)
        await client.get(
            f"{API_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {user_data['refresh_token']}"},
        )

        # When
        response = await client.get(
            f"{API_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {user_data['refresh_token']}"},
        )

        # Then
        assert response.status_code == 401

    async def test_refresh_with_revoked_token(self, client: AsyncClient) -> None:
        # Given
        user_data = await register_and_login(client)
        await client.post(
            f"{API_PREFIX}/logout",
            headers={"Authorization": f"Bearer {user_data['access_token']}"},
        )

        # When
        response = await client.get(
            f"{API_PREFIX}/refresh",
            headers={"Authorization": f"Bearer {user_data['refresh_token']}"},
        )

        # Then
        assert response.status_code == 401

    async def test_refresh_with_invalid_token(self, client: AsyncClient) -> None:
        # Given
        # When
        response = await client.get(
            f"{API_PREFIX}/refresh",
            headers={"Authorization": "Bearer invalid-token"},
        )

        # Then
        assert response.status_code == 401


class TestLogout:
    async def test_logout_success(self, client: AsyncClient) -> None:
        # Given
        user_data = await register_and_login(client)

        # When
        response = await client.post(
            f"{API_PREFIX}/logout",
            headers={"Authorization": f"Bearer {user_data['access_token']}"},
        )

        # Then
        assert response.status_code == 200
        assert response.json() == {"message": "Successfully logged out"}

    async def test_double_logout_returns_401(self, client: AsyncClient) -> None:
        # Given
        user_data = await register_and_login(client)
        await client.post(
            f"{API_PREFIX}/logout",
            headers={"Authorization": f"Bearer {user_data['access_token']}"},
        )

        # When
        response = await client.post(
            f"{API_PREFIX}/logout",
            headers={"Authorization": f"Bearer {user_data['access_token']}"},
        )

        # Then
        assert response.status_code == 401

    async def test_logout_with_invalid_token(self, client: AsyncClient) -> None:
        # Given
        # When
        response = await client.post(
            f"{API_PREFIX}/logout",
            headers={"Authorization": "Bearer invalid-token"},
        )

        # Then
        assert response.status_code == 401


class TestClean:
    async def test_clean_without_auth_returns_401(self, client: AsyncClient) -> None:
        # Given
        # When
        response = await client.get(f"{API_PREFIX}/clean")

        # Then
        assert response.status_code == 401

    async def test_clean_with_auth_returns_200(self, client: AsyncClient) -> None:
        # Given
        user_data = await register_and_login(client)

        # When
        response = await client.get(
            f"{API_PREFIX}/clean",
            headers={"Authorization": f"Bearer {user_data['access_token']}"},
        )

        # Then
        assert response.status_code == 200


class TestRateLimit:
    async def test_login_rate_limit(self, client: AsyncClient) -> None:
        # Given
        username = fake.user_name()
        password = fake.password(length=12)
        await client.post(
            f"{API_PREFIX}/register",
            json={"email": fake.email(), "username": username, "password": password},
        )

        # When
        responses = []
        for _ in range(6):
            response = await client.post(
                f"{API_PREFIX}/login",
                data={"username": username, "password": password},
            )
            responses.append(response)

        # Then
        assert responses[-1].status_code == 429

    async def test_register_rate_limit(self, client: AsyncClient) -> None:
        # Given
        # When
        responses = []
        for _ in range(4):
            response = await client.post(
                f"{API_PREFIX}/register",
                json={
                    "email": fake.email(),
                    "username": fake.user_name(),
                    "password": fake.password(length=12),
                },
            )
            responses.append(response)

        # Then
        assert responses[-1].status_code == 429
