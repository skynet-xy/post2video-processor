# dependency injection
from app.core.config import settings
from app.services.video_service import VideoService


def get_video_service():
    return VideoService(settings.OUTPUT_DIR)
