import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, cast

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel.ext.asyncio.session import AsyncSession

from fastauth.common.settings import settings
from fastauth.db import TokenRepository, UserRepository
from fastauth.models.schemas import UserLogin, UserRegister
from fastauth.models.token import Token, TokenType
from fastauth.models.user import User


class AuthService:
    """Service for authentication and authorization."""

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    auth_fail_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentification failed",
    )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    refresh_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not refresh token",
    )

    def __init__(
        self,
        user_repository: UserRepository,
        token_repository: TokenRepository,
    ) -> None:
        self.user_repository = user_repository
        self.token_repository = token_repository

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        return cast(bool, self.pwd_context.verify(plain_password, hashed_password))

    def _get_password_hash(self, password: str) -> str:
        """Hash a password for secure storage."""
        return cast(str, self.pwd_context.hash(password))

    async def create_user(
        self,
        session: AsyncSession,
        user_create: UserRegister,
    ) -> User:
        """Create a new user with the given credentials."""
        hashed_password = self._get_password_hash(user_create.password)

        user = User(
            email=user_create.email,
            username=user_create.username,
            hashed_password=hashed_password,
        )

        return await self.user_repository.create(session=session, item=user)

    async def authenticate_user(
        self,
        session: AsyncSession,
        user_login: UserLogin,
    ) -> User:
        """Authenticate a user with their credentials and return the user object."""
        user = await self.user_repository.get_or_none(
            session=session,
            username=user_login.username,
        )

        if user is None:
            raise self.auth_fail_exception

        if not self._verify_password(user_login.password, user.hashed_password):
            raise self.auth_fail_exception

        return user

    @staticmethod
    def _create_token(
        data: dict[str, Any],
        expires_delta: timedelta,
    ) -> str:
        """Create a new JWT token with the given data and expiration time."""
        to_encode = data.copy()
        expire = datetime.now(UTC) + expires_delta
        to_encode.update({"exp": expire})

        return jwt.encode(  # type: ignore
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    async def create_token_for_user(
        self,
        session: AsyncSession,
        user: User,
    ) -> tuple[str, str]:
        """Create a new JWT token for the given user."""
        access_token_expires = timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token_data = {"sub": str(user.id), "type": "access"}
        access_token = self._create_token(access_token_data, access_token_expires)

        refresh_token_expires = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token_data = {"sub": str(user.id), "type": "refresh"}
        refresh_token = self._create_token(refresh_token_data, refresh_token_expires)

        access_token_db = Token(
            token=access_token,
            token_type=TokenType.ACCESS,
            expires_at=datetime.now(UTC) + access_token_expires,
            user_id=user.id,
        )

        refresh_token_db = Token(
            token=refresh_token,
            token_type=TokenType.REFRESH,
            expires_at=datetime.now(UTC) + refresh_token_expires,
            user_id=user.id,
        )

        await self.token_repository.create(session=session, item=access_token_db)
        await self.token_repository.create(session=session, item=refresh_token_db)

        return access_token, refresh_token

    async def get_user_from_token(
        self,
        session: AsyncSession,
        token: str,
    ) -> User:
        """Get the current user from the token."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )

            user_id: int = int(payload.get("sub"))
            token_type: str = payload.get("type")

            if user_id is None or token_type != "access":
                raise self.credentials_exception

            token_db = await self.token_repository.get_or_none(
                session=session,
                token=token,
                user_id=user_id,
            )

            if token_db is None or token_db.is_expired is True:
                raise self.credentials_exception

            user = await self.user_repository.get_or_none(session=session, id=user_id)

            if user is None:
                raise self.credentials_exception

            return user

        except JWTError:
            raise self.credentials_exception

    async def create_or_update_oauth2_user(
        self,
        session: AsyncSession,
        provider: str,
        provider_id: str,
        email: str,
        username: str,
    ) -> User:
        """Create or update an authenticated user via OAuth."""
        user = await self.user_repository.get_or_none(
            session=session,
            oauth_provider=provider,
            oauth_id=provider_id,
        )

        if user is None:
            user = await self.user_repository.get_or_none(
                session=session,
                email=email,
            )

        if user is not None and user.id is not None:
            await self.user_repository.update(
                session=session,
                id_=user.id,
                oauth_provider=provider,
                oauth_id=provider_id,
            )
            return user

        random_password = uuid.uuid4().hex
        hashed_password = self._get_password_hash(random_password)

        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            oauth_provider=provider,
            oauth_id=provider_id,
        )

        return await self.user_repository.create(session=session, item=user)

    async def refresh_token(
        self,
        session: AsyncSession,
        refresh_token: str,
    ) -> Token:
        """Refresh a token."""
        refresh_token_db = await self.token_repository.get_or_none(
            session=session,
            token=refresh_token,
            token_type=TokenType.REFRESH,
        )

        if refresh_token_db is None or refresh_token_db.is_expired is True:
            raise self.refresh_token_exception

        user = await self.user_repository.get_or_none(
            session=session, id=refresh_token_db.user_id
        )

        if user is None:
            raise self.refresh_token_exception

        access_token_expires = timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

        access_token_data = {"sub": str(user.id), "type": "access"}
        access_token = self._create_token(access_token_data, access_token_expires)

        access_token_db = Token(
            token=access_token,
            token_type=TokenType.ACCESS,
            expires_at=datetime.now(UTC) + access_token_expires,
            user_id=user.id,
        )

        return await self.token_repository.create(session=session, item=access_token_db)

    async def clean_expired_tokens(
        self,
        session: AsyncSession,
    ) -> None:
        """Clean expired tokens."""
        await self.token_repository.delete_expired(session=session)
