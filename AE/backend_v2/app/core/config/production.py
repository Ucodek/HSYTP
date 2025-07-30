from app.core.config.base import Settings


class ProductionSettings(Settings):
    # Production-specific settings
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Additional production settings
    CORS_ORIGINS: list = ["https://app.example.com"]

    class Config:
        env_file = ".env.production"
