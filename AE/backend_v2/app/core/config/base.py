import json
import os
from typing import List, Optional, Union

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from the appropriate .env file
environment = os.getenv("ENVIRONMENT", "development")
env_file = f".env.{environment}" if os.path.exists(f".env.{environment}") else ".env"
load_dotenv(env_file)


class Settings(BaseSettings):
    """Application settings."""

    # Application Info
    PROJECT_NAME: str = "HSYTP API"
    PROJECT_DESCRIPTION: str = "High-performance API for financial data and AI models"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # API Settings
    API_PREFIX: str = "/api"
    API_V1_PREFIX: str = "/api/v1"

    # CORS Settings
    CORS_ORIGINS: List[AnyHttpUrl] = []

    # Log Settings
    LOG_LEVEL: str = "INFO"

    # Security Settings
    SECRET_KEY: str = "development-secret-key-replace-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "hsytp"
    POSTGRES_PORT: int = 5432

    # Redis Settings
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: int = 6379

    # Rate Limiting
    RATE_LIMIT_DEFAULT: int = 100  # Requests per minute for anonymous users
    RATE_LIMIT_USER: int = 300  # Requests per minute for regular users
    RATE_LIMIT_ADMIN: int = 1000  # Requests per minute for admin users

    # Monitoring Settings
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = False
    OTLP_ENDPOINT: Optional[str] = None

    # Testing flag
    TESTING: bool = False

    # Model configuration
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parse CORS origins from string to list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str):
            return json.loads(v)
        return v

    # Property to get database URL
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components."""
        if self.TESTING:
            return os.getenv("DATABASE_URL", "sqlite:///./test.db")

        # Construct PostgreSQL connection string
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


# Load and create settings instance
settings = Settings()
