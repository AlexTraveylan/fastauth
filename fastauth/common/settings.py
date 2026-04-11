from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    # Application parameters
    APP_NAME: str = "FastAuth"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Database parameters
    FASTAUTH_POSTGRES_POOLER_CONNECTION_STRING: str = "postgresql+asyncpg://postgres:fastauth@localhost:5432/fastauth"

    # JWT parameters
    JWT_SECRET_KEY: str = "super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Rate limiting parameters
    RATE_LIMIT_LOGIN: str = "5/minute"
    RATE_LIMIT_REGISTER: str = "3/minute"

    # CORS
    ALLOWED_ORIGINS: str = "*"

    # Google OAuth parameters
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None


# Global configuration instance
settings = Settings()
