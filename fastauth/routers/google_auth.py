"""Routes pour l'authentification Google OAuth."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from fastauth.common.settings import settings
from fastauth.db import TokenRepository, UserRepository, get_async_session
from fastauth.models.schemas import Token
from fastauth.services import auth, oauth2

router = APIRouter(tags=["google_auth"])

auth_service = auth.AuthService(
    user_repository=UserRepository(),
    token_repository=TokenRepository(),
)


@router.get("/login")
async def login_via_google(request: Request):
    """Initialize the Google authentication process."""
    redirect_uri = await oauth2.oauth.google.authorize_redirect(
        request,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )
    return redirect_uri


@router.get("/callback")
async def auth_callback_google(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> Token:
    """Handle the Google authentication callback."""
    try:
        user_info = await oauth2.get_google_user_info(request)

        user = await auth_service.create_or_update_oauth2_user(
            session=session,
            provider="google",
            provider_id=user_info.sub,
            email=user_info.email,
            username=f"{user_info.name}.{user_info.family_name}",
        )

        access_token, refresh_token = await auth_service.create_token_for_user(
            session=session,
            user=user,
        )

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'authentification Google: {str(e)}",
        )
