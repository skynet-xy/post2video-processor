import os

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from app.api.deps import get_video_service
from app.api.dto.video_dto import CommentRequest, ResponseMessage
from app.core.config import settings
from app.services.video_service import VideoService

router = APIRouter(prefix="/video", tags=["Video Operations"])


@router.post("/process-reddit-comments-video/")
async def add_comments_to_video(
        request: CommentRequest,
        background_tasks: BackgroundTasks,
        video_service: VideoService = Depends(get_video_service)
) -> ResponseMessage:
    """Add comments to a video file."""
    if not request.video_name and not request.youtube_url:
        raise HTTPException(status_code=400, detail="Either video_name or youtube_url must be provided")

    if request.youtube_url:
        video_path, _ = await video_service.download_youtube_video(request.youtube_url, height=720)
    else:
        video_path = os.path.join(settings.VIDEO_TEMPLATES_DIR, request.video_name)

    # Validate video path exists
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")

    return await video_service.create_add_comments_to_video_job(
        video_path,
        request.comments,
        background_tasks
    )
