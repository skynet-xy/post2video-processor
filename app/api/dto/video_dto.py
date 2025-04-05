# app/models/video.py
from typing import Optional, Any, List, Literal

from pydantic import BaseModel, Field

from app.api.dto.reddit_dto import Comment
from app.enum.voice import Gender, Language


class CommentRequest(BaseModel):
    # youtube_url: str = Field(default='', description="URL of YouTube video to download")
    video_name: str = Field(default='AsetdKZN11o-720p-minecraft-Free_vertical.webm', description="Name of template video to use")
    comments: List[Comment] = Field(description="List of comments to overlay on the video")
    voice_gender: Optional[Gender] = Field(
        default=Gender.MALE,
        description="Voice to use for text-to-speech. Options: male, female"
    )
    lang: Optional[Language] = Field(
        default=Language.English,
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


class LanguageModelResponse(BaseModel):
    code: str
    name: str


class LanguagesResponse(BaseModel):
    languages: List[LanguageModelResponse]


class VoiceModel(BaseModel):
    name: str
    code: str
    language: Language
    gender: Gender


class VoicesResponse(BaseModel):
    voices: List[VoiceModel]
