# app/api/routes/video.py
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
from app.services.video_service import VideoService
from app.api.deps import get_video_service

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