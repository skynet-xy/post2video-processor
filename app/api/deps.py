# dependency injection
from app.core.config import settings
from app.services.reddit_service import RedditService
from app.services.video_service import VideoService


def get_video_service():
    return VideoService(settings.OUTPUT_DIR, settings.VIDEO_TEMPLATES_DIR)

def get_reddit_service():
    return RedditService(settings.REDDIT_CLIENT_ID, settings.REDDIT_CLIENT_SECRET, settings.REDDIT_USER_AGENT)