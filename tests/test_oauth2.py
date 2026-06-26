from faker import Faker
from sqlmodel.ext.asyncio.session import AsyncSession

from fastauth.db import TokenRepository, UserRepository
from fastauth.models.schemas import GoogleUserInfo
from fastauth.models.user import User
from fastauth.services.auth import AuthService

fake = Faker()

auth_service = AuthService(user_repository=UserRepository(), token_repository=TokenRepository())


class TestGoogleUserInfo:
    def test_accepts_minimal_payload_without_names(self) -> None:
        # Given
        email = fake.email()
        sub = fake.uuid4()

        # When
        info = GoogleUserInfo(email=email, sub=sub)

        # Then
        assert info.given_name is None
        assert info.family_name is None
        assert info.name is None
        assert info.email_verified is False

    def test_keeps_given_name_when_provided(self) -> None:
        # Given
        given_name = fake.first_name()

        # When
        info = GoogleUserInfo(email=fake.email(), sub=fake.uuid4(), given_name=given_name)

        # Then
        assert info.given_name == given_name


class TestUniqueUsername:
    async def test_returns_base_when_free(self, session: AsyncSession) -> None:
        # Given
        base = fake.first_name()

        # When
        username = await auth_service._generate_unique_username(session=session, base=base)

        # Then
        assert username == base

    async def test_adds_random_suffix_on_collision(self, session: AsyncSession) -> None:
        # Given
        base = fake.first_name()
        await auth_service.create_or_update_oauth2_user(
            session=session,
            provider="google",
            provider_id=fake.uuid4(),
            email=fake.email(),
            username=base,
        )

        # When
        username = await auth_service._generate_unique_username(session=session, base=base)

        # Then
        assert username != base
        assert username.startswith(f"{base}-")


class TestCreateOrUpdateOAuth2User:
    async def test_new_user_with_taken_username_gets_suffix(self, session: AsyncSession) -> None:
        # Given
        base = fake.first_name()
        await auth_service.create_or_update_oauth2_user(
            session=session,
            provider="google",
            provider_id=fake.uuid4(),
            email=fake.email(),
            username=base,
        )

        # When
        user = await auth_service.create_or_update_oauth2_user(
            session=session,
            provider="google",
            provider_id=fake.uuid4(),
            email=fake.email(),
            username=base,
        )

        # Then
        assert user.username != base
        assert user.username.startswith(f"{base}-")

    async def test_links_oauth_to_existing_email_user(self, session: AsyncSession) -> None:
        # Given
        email = fake.email()
        provider_id = fake.uuid4()
        existing = User(
            email=email,
            username=fake.user_name(),
            hashed_password=auth_service._get_password_hash(fake.password()),
        )
        await UserRepository().create(session=session, item=existing)

        # When
        user = await auth_service.create_or_update_oauth2_user(
            session=session,
            provider="google",
            provider_id=provider_id,
            email=email,
            username=fake.first_name(),
        )

        # Then
        assert user.id == existing.id
        assert user.oauth_provider == "google"
        assert user.oauth_id == provider_id
