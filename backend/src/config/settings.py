"""Application settings for technical bootstrap configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Environment-driven runtime settings."""

    app_name: str = os.getenv("APP_NAME", "lager-app-backend")
    app_env: str = os.getenv("APP_ENV", "development")
    db_host: str = os.getenv("POSTGRES_HOST", "postgres")
    db_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    db_name: str = os.getenv("POSTGRES_DB", "lagerapp")
    db_user: str = os.getenv("POSTGRES_USER", "lagerapp")
    db_password: str = os.getenv("POSTGRES_PASSWORD", "lagerapp")
    database_url: str | None = os.getenv("DATABASE_URL")
    db_echo: bool = os.getenv("DB_ECHO", "false").lower() == "true"
    auth_secret_key: str = os.getenv("AUTH_SECRET_KEY", "lager-app-dev-secret")
    auth_access_token_ttl_seconds: int = int(os.getenv("AUTH_ACCESS_TOKEN_TTL_SECONDS", "3600"))
    erp_profile_name: str = os.getenv("ERP_PROFILE_NAME", "default")
    photo_upload_directory: str = os.getenv("PHOTO_UPLOAD_DIRECTORY", "uploads")
    cors_allow_origins_raw: str = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3001")

    @property
    def postgres_dsn(self) -> str:
        """Return database DSN from DATABASE_URL or individual env vars."""
        if self.database_url:
            return self.database_url
        return (
            f"postgresql://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def sqlalchemy_database_url(self) -> str:
        """Return SQLAlchemy-compatible database URL."""
        if self.database_url:
            if self.database_url.startswith("postgresql://"):
                return self.database_url.replace(
                    "postgresql://",
                    "postgresql+psycopg://",
                    1,
                )
            return self.database_url
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def cors_allow_origins(self) -> list[str]:
        """Return allowed frontend origins for browser CORS requests."""
        return [origin.strip() for origin in self.cors_allow_origins_raw.split(",") if origin.strip()]


settings = Settings()
