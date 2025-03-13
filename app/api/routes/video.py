# app/api/routes/video.py
import os
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException

from app.api.deps import get_video_service
from app.api.dto.reddit_comment import CommentRequest, ResponseMessage
from app.services.video_service import VideoService

router = APIRouter(prefix="/video", tags=["Video Operations"])


@router.post("/trim/")
async def trim_video(
        file: Optional[UploadFile] = File(None),
        video_url: Optional[str] = Form(None),
        start_time: float = Form(...),
        end_time: float = Form(...),
        video_service: VideoService = Depends(get_video_service)
):
    """Trim a video by specifying start and end times."""
    return await video_service.process_trim_request(file, video_url, start_time, end_time)


@router.post("/add-comments/")
async def add_comments_to_video(
        request: CommentRequest,
        video_service: VideoService = Depends(get_video_service)
) -> ResponseMessage:
    """Add comments to a video file."""
    # Validate video path exists
    if not os.path.exists(request.video_path):
        raise HTTPException(status_code=404, detail="Video file not found")

    return await video_service.add_comments_to_video(
        request.video_path,
        request.comments
    )
