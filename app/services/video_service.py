# app/services/video_service.py
import os
from typing import List

import yt_dlp as youtube_dl
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
            return ResponseMessage(
                success=True,
                message="Successfully added video to queue",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error adding comments to video: {str(e)}"
            )

    async def download_youtube_video(self, url: str, highres=False, output_path=None):
        if not output_path:
            output_path = self.output_dir

        resolution_tag = 'highres' if highres else 'standard'
        format = 'bestvideo[height>=720]+bestaudio[ext=m4a]/best[height>=720]' if highres else 'best',

        ydl_opts = {
            'format': format,
            'outtmpl': os.path.join(output_path, f'%(title,sanitize)s-{resolution_tag}-%(id)s.%(ext)s'),
            'noplaylist': True,
            'restrictfilenames': True,
            'trim_file_name': len(output_path) + 64,
            'overwrites': False,
        }

        # Add external downloader only for high-res videos
        if highres:
            ydl_opts.update({
                'external_downloader': 'aria2c',
                'external_downloader_args': ['-x', '16', '-k', '1M']
            })

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = ydl.prepare_filename(info_dict)
            return video_title, info_dict
