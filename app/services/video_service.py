# app/services/video_service.py
import os
from typing import List

from fastapi import HTTPException
from moviepy.editor import VideoFileClip

from app.api.dto.reddit_comment import Comment, ResponseMessage
from app.utils.reddit_comment_overlay import add_comments_to_video, write_videofile
from app.utils.trim_video import trim_video_to_fit_comments
from create_video import generate_comments


class VideoService:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    async def add_comments_to_video(self, video_path: str, comments: List[Comment]) -> ResponseMessage:
        """
        Add comments to a video file.

        Args:
            video_path: Path to the video file
            comments: List of Comment objects with text and timing info

        Returns:
            FileResponse with the processed video
        """
        try:
            video = VideoFileClip(video_path)
            processed_comments = generate_comments()
            video = add_comments_to_video(video, processed_comments)
            video = trim_video_to_fit_comments(video, processed_comments)
            output_path = write_videofile(video)
            print(f"Video successfully created at: {output_path}")

            # Clean up resources
            video.close()


        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error adding comments to video: {str(e)}"
            )
