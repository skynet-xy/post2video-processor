# app/models/video.py
from typing import List
from typing import Optional, Any

from pydantic import BaseModel


class Comment(BaseModel):
    text: str
    time_start: float  # When comment appears (seconds)
    time_end: float  # When comment disappears (seconds)
    # position_x: int = 10  # X position (px from left)
    # position_y: int = 10  # Y position (px from top)
    # font_size: int = 24   # Font size
    # color: str = "white"  # Text color


class CommentRequest(BaseModel):
    video_path: str
    comments: List[Comment]


class ResponseMessage(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
