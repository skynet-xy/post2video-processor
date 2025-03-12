import os
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Post 2 Video API"

    # Base directory is the project root
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    # Output directory for processed videos
    OUTPUT_DIR: Path = BASE_DIR / "output"

    # Assets directory
    ASSETS_DIR: Path = BASE_DIR / "assets"

    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    class Config:
        case_sensitive = True
        env_file = ".env"

# Create settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.ASSETS_DIR, exist_ok=True)