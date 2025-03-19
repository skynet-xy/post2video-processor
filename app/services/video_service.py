import asyncio
import json
import logging
import os
import random
import uuid
from typing import List, Tuple, Dict, Any

import yt_dlp as youtube_dl
from fastapi import HTTPException, BackgroundTasks
from moviepy.editor import VideoFileClip
from sqlalchemy import text

from app.api.dto.video_dto import Comment, ResponseMessage
from app.db.session import get_db
from app.utils.comment_audio_generator import generate_comments_with_duration
from app.utils.reddit_comment_overlay import add_comments_to_video, write_videofile
from app.utils.trim_video import trim_video_to_fit_comments

logger = logging.getLogger(__name__)


class VideoService:
    def __init__(self, output_dir, video_templates_dir):
        self.output_dir = output_dir
        self.video_templates_dir = video_templates_dir
        os.makedirs(output_dir, exist_ok=True)

    async def create_add_comments_to_video_job(
            self,
            video_path: str,
            comments: List[Comment],
            background_tasks: BackgroundTasks = None
    ) -> ResponseMessage:
        """
        Create a job to add comments to a video and process it in the background.

        Args:
            video_path: Path to the video file
            comments: List of Comment objects with text and timing info
            background_tasks: BackgroundTasks object for running tasks asynchronously

        Returns:
            ResponseMessage indicating success/failure
        """
        try:
            # Generate a unique job code
            job_code = str(uuid.uuid4())

            # Extract video name from path
            video_name = os.path.basename(video_path)

            # Serialize comments to JSON
            comments_json = [comment.model_dump() for comment in comments]

            # Get database session
            async with get_db() as db:
                db_session = db()

                # Create job record
                query = """
                INSERT INTO job_add_reddit_comment_overlay
                (job_code, status, video_name, comments)
                VALUES (:job_code, :status, :video_name, :comments)
                """

                await db_session.execute(
                    text(query),
                    {
                        "job_code": job_code,
                        "status": "pending",
                        "video_name": video_name,
                        "comments": json.dumps(comments_json)
                    }
                )

                await db_session.commit()

            # Start the background task to process the job
            if background_tasks:
                background_tasks.add_task(self.process_video_job, job_code)
            else:
                # Start processing in the background without using BackgroundTasks
                asyncio.create_task(self.process_video_job(job_code))

            return ResponseMessage(
                success=True,
                message=f"Job created successfully with code: {job_code}",
                data={"job_code": job_code}
            )

        except Exception as e:
            logger.error(f"Failed to create video comment job for video '{video_path}': {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error creating video comment job: {str(e)}"
            )

    async def process_video_job(self, job_code: str):
        """
        Process a video job in the background.

        Args:
            job_code: The unique identifier of the job
        """
        try:
            # Get job details from database
            async with get_db() as db:
                db_session = db()
                query = """
                SELECT video_name, comments 
                FROM job_add_reddit_comment_overlay
                WHERE job_code = :job_code AND status = 'pending'
                """

                result = await db_session.execute(text(query), {"job_code": job_code})
                job = result.fetchone()

                if not job:
                    logger.error(f"Job {job_code} not found or not pending")
                    return

                video_name, comments_data = job

                # Update status to processing
                await db_session.execute(
                    text("UPDATE job_add_reddit_comment_overlay SET status = 'processing' WHERE job_code = :job_code"),
                    {"job_code": job_code}
                )
                await db_session.commit()

            # Get the video path
            video_path = os.path.join(self.video_templates_dir, video_name)
            comments = [Comment(**comment) for comment in comments_data]

            # Process the video
            video = VideoFileClip(video_path)
            target_duration = 60.0
            processed_comments, _ = generate_comments_with_duration(comments, target_duration,
                                                                    allow_exceed_duration=True)
            video = add_comments_to_video(video, processed_comments)
            video = trim_video_to_fit_comments(video, processed_comments)
            output_path = write_videofile(video)
            video.close()

            # Update job status to completed
            async with get_db() as db:
                db_session = db()
                await db_session.execute(
                    text("""
                    UPDATE job_add_reddit_comment_overlay 
                    SET status = 'completed', output_path = :output_path 
                    WHERE job_code = :job_code
                    """),
                    {"job_code": job_code, "output_path": output_path}
                )
                await db_session.commit()

            logger.info(f"Job {job_code} processed successfully")

        except Exception as e:
            logger.error(f"Error processing job {job_code}: {str(e)}", exc_info=True)
            # Update job status to failed
            async with get_db() as db:
                db_session = db()
                await db_session.execute(
                    text("""
                    UPDATE job_add_reddit_comment_overlay 
                    SET status = 'failed', error_message = :error 
                    WHERE job_code = :job_code
                    """),
                    {"job_code": job_code, "error": str(e)}
                )
                await db_session.commit()

    async def download_youtube_video(self, url: str, height=720, output_path=None, max_retries=3) -> Tuple[
        str, Dict[str, Any]]:
        if not output_path:
            output_path = self.output_dir

        dl_format = f'bestvideo[height={height}]'
        resolution_tag = str(height) + "p"
        ydl_opts = {
            'format': dl_format,
            'outtmpl': os.path.join(output_path, f'%(id)s-{resolution_tag}-%(title,sanitize)s.%(ext)s'),
            'noplaylist': True,
            'restrictfilenames': True,
            'trim_file_name': len(output_path) + 64,
            'overwrites': False,
            'external_downloader': 'aria2c',  # Use aria2c for faster downloads
            'external_downloader_args': ['-x', '16', '-k', '1M']  # 16 connections, 1M chunk size
        }

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
                    await asyncio.sleep(sleep_time)
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
