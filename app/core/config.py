import os
from dataclasses import field
from pathlib import Path

from pydantic_settings import BaseSettings


def _default_cors_settings() -> list[str]:
    return ["*"]

class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Post 2 Video API"

    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = field(default_factory=_default_cors_settings)
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: list[str] = field(default_factory=_default_cors_settings)
    ALLOW_HEADERS: list[str] = field(default_factory=_default_cors_settings)

    # Base directory is the project root
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    # Generated directory
    GENERATED_DIR: Path = BASE_DIR / "generated"
    OUTPUT_DIR: Path = GENERATED_DIR / "output"
    CACHE_DIR: Path = GENERATED_DIR / "cache"

    # Assets directory
    ASSETS_DIR: Path = BASE_DIR / "assets"
    FONTS_DIR: Path = ASSETS_DIR / "fonts"
    DEFAULT_AVATAR: Path = ASSETS_DIR / "defaults/default_avatar.png"
    VIDEO_TEMPLATES_DIR: Path = ASSETS_DIR / "video_templates"

    # Reddit settings
    REDDIT_CLIENT_ID: str = "ZdHLafxpZo6OtKIIn0uPOA"
    REDDIT_CLIENT_SECRET: str = "PZRwrx8xwktG1-LZIGrpYZGl2oqNpg"
    REDDIT_USER_AGENT: str = "fr.allaboutfrance:v1.0 (by /u/One-Accountant2011)"

    # Database settings
    DB_USER: str = "app"
    DB_PASSWORD: str = "1"
    DB_HOST: str = "postgres"
    DB_PORT: str = "5432"
    DB_NAME: str = "app"

    class Config:
        case_sensitive = True
        env_file = ".env"


# Create settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.CACHE_DIR, exist_ok=True)
os.makedirs(settings.FONTS_DIR, exist_ok=True)
os.makedirs(settings.VIDEO_TEMPLATES_DIR, exist_ok=True)
