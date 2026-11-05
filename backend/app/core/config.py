"""Application configuration via Pydantic Settings."""

from __future__ import annotations

import enum
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, enum.Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Environment ──
    nyaysetu_env: Environment = Environment.LOCAL

    # ── Database ──
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_echo: bool = False

    # ── Redis ──
    redis_url: str = "redis://localhost:6379/0"

    # ── S3 / MinIO ──
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str
    s3_secret_key: str
    s3_bucket_name: str = "nyaysetu-documents"
    s3_region: str = "us-east-1"

    # ── Security ──
    secret_key: str
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    # ── Rate Limiting ──
    rate_limit_per_minute: int = 60

    @field_validator("secret_key")
    @classmethod
    def _secret_key_not_default(cls, v: str) -> str:
        if v == "change-me-in-production-use-64-char-hex":
            import warnings

            warnings.warn(
                "SECRET_KEY is set to default value. Change it in production!",
                stacklevel=2,
            )
        return v

    @field_validator("database_url")
    @classmethod
    def _db_url_must_be_async(cls, v: str) -> str:
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL must use the postgresql+asyncpg:// scheme")
        return v

    @property
    def is_production(self) -> bool:
        return self.nyaysetu_env == Environment.PRODUCTION

    @property
    def is_local(self) -> bool:
        return self.nyaysetu_env == Environment.LOCAL


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
