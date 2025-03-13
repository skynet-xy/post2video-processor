import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Post 2 Video API"

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

    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

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
