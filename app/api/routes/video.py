# app/api/routes/video.py
import os

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_video_service
from app.api.dto.reddit_comment import CommentRequest, ResponseMessage
from app.core.config import settings
from app.services.video_service import VideoService

router = APIRouter(prefix="/video", tags=["Video Operations"])


@router.post("/add-reddit-comments/")
async def add_comments_to_video(
        request: CommentRequest,
        video_service: VideoService = Depends(get_video_service)
) -> ResponseMessage:
    """Add comments to a video file."""
    # Construct full path using video_name and directory from settings
    video_path = os.path.join(settings.VIDEO_TEMPLATES_DIR, request.video_name)

    # Validate video path exists
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")

    return await video_service.add_comments_to_video(
        video_path,
        request.comments
    )
