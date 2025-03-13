import os
import random
import time
from typing import List, Tuple, Dict, Any

import yt_dlp as youtube_dl
from fastapi import HTTPException
from moviepy.editor import VideoFileClip

from app.api.dto.video_dto import Comment, ResponseMessage
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

    async def download_youtube_video(self, url: str, highres=False, output_path=None, max_retries=3) -> Tuple[
        str, Dict[str, Any]]:
        if not output_path:
            output_path = self.output_dir

        resolution_tag = 'highres' if highres else 'standard'
        format = 'bestvideo[height>=720]+bestaudio[ext=m4a]/best[height>=720]' if highres else 'best'

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

        retry_count = 0
        last_exception = None

        while retry_count <= max_retries:
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(url, download=True)
                    video_title = ydl.prepare_filename(info_dict)
                    return video_title, info_dict

            except youtube_dl.utils.HTTPError as e:
                if '403' in str(e):
                    retry_count += 1
                    if retry_count > max_retries:
                        last_exception = e
                        break

                    # Exponential backoff with jitter
                    sleep_time = (2 ** retry_count) + random.uniform(0, 1)
                    print(
                        f"Received 403 error from YouTube. Retrying in {sleep_time:.2f} seconds (attempt {retry_count}/{max_retries})")
                    time.sleep(sleep_time)
                else:
                    # Re-raise if it's not a 403 error
                    raise
            except Exception as e:
                # Re-raise any other exception
                raise

        # If we exhausted all retries
        if last_exception:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to download YouTube video after {max_retries} retries: {str(last_exception)}"
            )
