from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from fastauth.db import TokenRepository, UserRepository, get_async_session
from fastauth.models.schemas import Token, UserLogin, UserRegister, UserResponse
from fastauth.models.user import User
from fastauth.services import auth

router = APIRouter(tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

auth_service = auth.AuthService(
    user_repository=UserRepository(),
    token_repository=TokenRepository(),
)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> User:
    """Dependency to get the current authenticated user."""
    return await auth_service.get_user_from_token(session=session, token=token)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserRegister,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> User:
    """Register a new user."""
    user = await auth_service.create_user(session=session, user_create=user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> Token:
    """Authenticate and login a user."""
    user_login = UserLogin(
        username=form_data.username,
        password=form_data.password,
    )

    user = await auth_service.authenticate_user(session, user_login)
    access_token, refresh_token = await auth_service.create_token_for_user(
        session=session,
        user=user,
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get information about the currently authenticated user."""
    return current_user
