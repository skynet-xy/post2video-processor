# app/services/video_service.py
import os
import tempfile
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from typing import Optional, Tuple
import subprocess

class VideoService:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    async def download_video(self, url: str, output_path: str) -> str:
        """Download a video from a URL using yt-dlp."""
        try:
            import yt_dlp

            options = {
                'format': 'best[ext=mp4]',
                'outtmpl': output_path,
                'quiet': True,
            }

            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])

            return output_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to download video: {str(e)}")

    async def trim_video(self, video_path: str, start_time: float, end_time: float) -> Tuple[str, str]:
        """
        Trim video by specifying start and end times.

        Args:
            video_path: Path to the video file
            start_time: Start time in seconds
            end_time: End time in seconds

        Returns:
            Tuple containing the output path and filename
        """
        try:
            # Create output filename and path
            output_filename = f"trimmed_{os.path.basename(video_path)}"
            output_path = os.path.join(self.output_dir, output_filename)

            # Calculate duration
            duration = end_time - start_time

            # Construct the ffmpeg command
            command = [
                'ffmpeg',
                '-i', video_path, # Input file
                '-ss', str(start_time), # Start time
                '-t', str(duration), # Duration
                '-c', 'copy', # Copy codec
                '-y', # Overwrite output file if it exists
                output_path
            ]

            # Run the ffmpeg command
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode != 0:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error trimming video: {result.stderr}"
                )

            return output_path, output_filename

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error trimming video: {str(e)}")

    async def process_trim_request(
            self,
            file: Optional[UploadFile],
            video_url: Optional[str],
            start_time: float,
            end_time: float
    ) -> FileResponse:
        """Process a video trim request from either uploaded file or URL"""
        if not file and not video_url:
            raise HTTPException(status_code=400, detail="Either file or video_url must be provided")

        try:
            # Create a temporary file for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_input:
                temp_input_path = temp_input.name

                # Handle file upload
                if file:
                    contents = await file.read()
                    with open(temp_input_path, 'wb') as f:
                        f.write(contents)
                # Handle URL
                elif video_url:
                    await self.download_video(video_url, temp_input_path)

            # Process the video
            output_path, output_filename = await self.trim_video(temp_input_path, start_time, end_time)

            # Clean up the temp input file
            os.unlink(temp_input_path)

            # Return the trimmed video file
            return FileResponse(
                path=output_path,
                filename=output_filename,
                media_type="video/mp4"
            )

        except Exception as e:
            # Clean up in case of errors
            if 'temp_input_path' in locals() and os.path.exists(temp_input_path):
                os.unlink(temp_input_path)
            raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")