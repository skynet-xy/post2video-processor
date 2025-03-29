import os

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import text

from app.api.deps import get_video_service
from app.api.dto.video_dto import CommentRequest, ResponseMessage, JobStatusResponse, LanguagesResponse, Language
from app.core.config import settings
from app.db.session import get_db
from app.services.video_service import VideoService

router = APIRouter(prefix="/video", tags=["Video Operations"])


@router.post("/process-reddit-comments-video/")
async def add_comments_to_video(
        request: CommentRequest,
        background_tasks: BackgroundTasks,
        video_service: VideoService = Depends(get_video_service)
) -> ResponseMessage:
    """Add comments to a video file."""
    # if not request.video_name and not request.youtube_url:
    #     raise HTTPException(status_code=400, detail="Either video_name or youtube_url must be provided")
    #
    # if request.youtube_url:
    #     video_path, _ = await video_service.download_youtube_video(request.youtube_url, height=720)
    # else:
    #     video_path = os.path.join(settings.VIDEO_TEMPLATES_DIR, request.video_name)

    video_path = os.path.join(settings.VIDEO_TEMPLATES_DIR, request.video_name)

    # Validate video path exists
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")

    return await video_service.create_add_comments_to_video_job(
        video_path=video_path,
        comments=request.comments,
        background_tasks=background_tasks,
        voice_gender=request.voice_gender,
        lang=request.lang,
        vid_len=request.vid_len,
        ratio=request.ratio,
        theme=request.theme,
        title=request.title
    )

@router.get("/get_output_video/{job_code}", response_model=ResponseMessage)
async def get_output_video(job_code: str) -> ResponseMessage:
    """Get the output video path for a specific job."""
    try:
        async with get_db() as db:
            db_session = db()
            query = """
            SELECT output_path 
            FROM job_add_reddit_comment_overlay
            WHERE job_code = :job_code
            """
            result = await db_session.execute(text(query), {"job_code": job_code})
            job = result.fetchone()

            if not job or not job[0]:
                return ResponseMessage(
                    success=False,
                    message=f"No output video found for job code: {job_code}",
                    data=None
                )

            return ResponseMessage(
                success=True,
                message=f"Output video found",
                data={
                    "job_code": job_code,
                    "output_path": f"post2video.kybiu.com/static/output/{job[0].split("/")[-1]}"
                }
            )
    except Exception as e:
        return ResponseMessage(
            success=False,
            message=f"Error retrieving output video path: {str(e)}",
            data=None
        )
@router.get("/status/{job_code}")
async def get_job_status(job_code: str, video_service: VideoService = Depends(get_video_service)) -> JobStatusResponse:
    """Get the status of a video processing job."""
    return await video_service.get_job_status(job_code)


@router.get("/languages/", response_model=LanguagesResponse)
async def get_supported_languages() -> LanguagesResponse:
    """Get all supported languages for text-to-speech."""
    languages = [
        {"code": lang.value, "name": lang.name}
        for lang in Language
    ]
    return LanguagesResponse(languages=languages)