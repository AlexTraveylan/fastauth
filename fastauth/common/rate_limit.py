from slowapi import Limiter
from slowapi.util import get_remote_address

from fastauth.common.settings import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.RATE_LIMIT_STORAGE_URI,
    enabled=settings.RATE_LIMIT_ENABLED,
)


def login_limit() -> str:
    return settings.RATE_LIMIT_LOGIN


def register_limit() -> str:
    return settings.RATE_LIMIT_REGISTER


def refresh_limit() -> str:
    return settings.RATE_LIMIT_REFRESH


def google_limit() -> str:
    return settings.RATE_LIMIT_GOOGLE
