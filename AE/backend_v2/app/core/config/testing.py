from app.core.config.base import Settings


class TestingSettings(Settings):
    # Testing-specific settings
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    TESTING: bool = True

    # Use a separate test database
    POSTGRES_DB: str = "test_db"
    POSTGRES_SERVER: str = "localhost"

    # Override authentication for easier testing
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env.testing"
