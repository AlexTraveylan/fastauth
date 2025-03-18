"""Configuration de l'application FastAuth."""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration class for the FastAuth application.

    This class uses Pydantic to load and validate the environment variables
    necessary for the application to function.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # Application parameters
    APP_NAME: str = "FastAuth"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    # Database parameters
    DATABASE_URL: str = "postgresql+asyncpg://postgres:fastauth@localhost:5432/fastauth"

    # JWT parameters
    JWT_SECRET_KEY: str = "super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google OAuth parameters
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None


# Global configuration instance
settings = Settings()
