# app/models/video.py
from enum import Enum
from typing import Optional, Any, List, Literal, Dict

from pydantic import BaseModel, Field

from app.api.dto.reddit_dto import Comment


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

class Language(str, Enum):
    US = "en-US"
    FR = "fr-FR"
    VN = "vi-VN"

class CommentRequest(BaseModel):
    # youtube_url: str = Field(default='', description="URL of YouTube video to download")
    video_name: str = Field(default='x3.mp4', description="Name of template video to use")
    comments: List[Comment] = Field(description="List of comments to overlay on the video")
    voice_gender: Optional[str] = Field(
        default="male",
        description="Voice to use for text-to-speech. Options: male, female"
    )
    lang: Optional[str] = Field(
        default="en-US",
        description="Language for text-to-speech. Options: en-US, fr-FR, vi-VN"
    )
    theme: Optional[str] = Field(default="dark", description="Theme for the comment overlay. Options: dark, light")
    vid_len: Optional[Literal[30, 60, 90]] = Field(
        default=90,
        description="Target video length in seconds. Options: 90, 60, 30"
    )
    title: Optional[str] = Field(default=None, description="Title for the video")
    ratio: Optional[str] = Field(default="16:9", description="Aspect ratio of the video. Options: 16:9, 9:16")


class ResponseMessage(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class JobStatusResponse(BaseModel):
    job_code: str
    success: bool
    message: str
    status: str = 'error'
    percentage: int = 0

class LanguagesResponse(BaseModel):
    languages: List[Dict[str, str]]