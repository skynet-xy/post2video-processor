# app/models/video.py
from typing import List
from typing import Optional, Any

from pydantic import BaseModel

from app.api.dto.reddit_dto import Comment


class CommentRequest(BaseModel):
    youtube_url: str = ''
    video_name: str = ''
    comments: List[Comment]


class ResponseMessage(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
