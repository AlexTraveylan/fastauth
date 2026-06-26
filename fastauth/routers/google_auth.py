"""Routes pour l'authentification Google OAuth."""

from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from fastauth.common.settings import settings
from fastauth.db import TokenRepository, UserRepository, get_async_session
from fastauth.services import auth, oauth2

router = APIRouter(tags=["google_auth"])

auth_service = auth.AuthService(
    user_repository=UserRepository(),
    token_repository=TokenRepository(),
)


def _frontend_redirect(fragment: dict[str, str]) -> RedirectResponse:
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/callback#{urlencode(fragment)}")


@router.get("/login")
async def login_via_google(request: Request):
    """Initialize the Google authentication process."""
    return await oauth2.oauth.google.authorize_redirect(
        request,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )


@router.get("/callback")
async def auth_callback_google(
    request: Request,
    session: AsyncSession = Depends(get_async_session),
) -> RedirectResponse:
    """Handle the Google authentication callback."""
    try:
        user_info = await oauth2.get_google_user_info(request)

        user = await auth_service.create_or_update_oauth2_user(
            session=session,
            provider="google",
            provider_id=user_info.sub,
            email=user_info.email,
            username=user_info.given_name or user_info.email,
        )

        access_token, refresh_token = await auth_service.create_token_for_user(
            session=session,
            user=user,
        )

        return _frontend_redirect(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            },
        )

    except Exception as e:  # noqa: BLE001
        return _frontend_redirect({"error": str(e)})
