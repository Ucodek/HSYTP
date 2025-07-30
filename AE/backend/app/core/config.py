import os
from pathlib import Path
from typing import List, Optional

from pydantic import PostgresDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the base directory of the project for finding the .env file
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "Financial Data API"
    APP_DESCRIPTION: str = "API for financial data and portfolio analysis"
    APP_VERSION: str = "0.1.0"

    # API
    API_V1_STR: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "financial_data"

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    # External connection URLs for cloud databases
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    USE_REDIS_CACHE: bool = True

    # Cache TTLs (in seconds)
    CACHE_TTL_DEFAULT: int = 300  # 5 minutes
    CACHE_TTL_INSTRUMENTS: int = 3600  # 1 hour

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"  # Used for JWT
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # New setting for refresh token expiration

    # Rate limiting
    RATE_LIMIT_BASIC: int = 100  # requests per minute
    RATE_LIMIT_PREMIUM: int = 500  # requests per minute

    @model_validator(mode="after")
    def assemble_db_connection(self) -> "Settings":
        """Set the SQLAlchemy database URI from
        individual components or from external URL."""
        if self.DATABASE_URL:
            # Use the provided full URL
            # Make sure it uses the right driver for SQLAlchemy
            url = self.DATABASE_URL
            if url.startswith("postgresql://") and "postgresql+psycopg://" not in url:
                self.SQLALCHEMY_DATABASE_URI = url.replace(
                    "postgresql://", "postgresql+psycopg://"
                )
            else:
                self.SQLALCHEMY_DATABASE_URI = url
        elif not self.SQLALCHEMY_DATABASE_URI:
            # Use the original logic for local development
            self.SQLALCHEMY_DATABASE_URI = PostgresDsn.build(
                scheme="postgresql+psycopg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=int(self.POSTGRES_PORT),
                path=f"{self.POSTGRES_DB or ''}",
            )
        return self

    # Configuration with absolute path to .env
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Initialize settings
settings = Settings()

# Debug output to verify .env loading
print(f"Database connection: {settings.SQLALCHEMY_DATABASE_URI}")
print(f"Database password: {settings.POSTGRES_PASSWORD[:3]}*** (from .env)")
