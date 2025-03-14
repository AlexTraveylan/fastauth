from authlib.integrations.starlette_client import OAuth
from fastapi import Request

from fastauth.common.settings import settings
from fastauth.models.schemas import GoogleUserInfo

oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
    },
)


async def get_google_user_info(request: Request) -> GoogleUserInfo:
    """Get user info from Google."""
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    return GoogleUserInfo(**user_info)
