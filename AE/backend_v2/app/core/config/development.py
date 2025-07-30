from app.core.config.base import Settings


class DevelopmentSettings(Settings):
    # Development-specific settings
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

    # Override this to use a local database for development
    POSTGRES_SERVER: str = "localhost"

    class Config:
        env_file = ".env.development"
