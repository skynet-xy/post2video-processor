# dependency injection
from app.services.video_service import VideoService
from app.core.config import settings

def get_video_service():
    return VideoService(settings.OUTPUT_DIR)