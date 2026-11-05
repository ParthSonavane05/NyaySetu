"""Application configuration — loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/nyaysetu"

    # Crypto
    SECRET_KEY: str = "CHANGE_ME_32_BYTES_base64url_key="  # Fernet key

    # JWT (RS256) — set via env in production
    JWT_PRIVATE_KEY: str = ""
    JWT_PUBLIC_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    LOG_LEVEL: str = "INFO"
    APP_ENV: str = "development"


settings = Settings()

