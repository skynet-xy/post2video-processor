import os
import textwrap

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, AudioFileClip

from text_to_speech import generate_audio_from_text


class RedditCommentOverlay:
    def __init__(self, video_path):
        """Initialize with the path to the video file."""
        self.video = VideoFileClip(video_path)
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        self.font_dir = os.path.join(assets_dir, "fonts")
        self.default_avatar = os.path.join(assets_dir, "assets", "default_avatar.png")
        self.audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "tmp_audio")

        # Ensure directories exist
        os.makedirs(self.font_dir, exist_ok=True)
        os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"), exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)

    def _create_reddit_comment(self, username, comment_text, avatar_path=None, width=500):
        """
        Create a Reddit-style comment image

        Args:
            username (str): Username to display
            comment_text (str): The comment content
            avatar_path (str, optional): Path to avatar image. Uses default if None.
            width (int): Width of the comment image

        Returns:
            PIL.Image: The generated comment image
        """
        # Set up fonts
        try:
            username_font = ImageFont.truetype(os.path.join(self.font_dir, "arial_bold.ttf"), 16)
            comment_font = ImageFont.truetype(os.path.join(self.font_dir, "arial.ttf"), 14)
        except IOError:
            username_font = ImageFont.load_default()
            comment_font = ImageFont.load_default()

        # Load avatar image
        avatar_size = 40
        if avatar_path and os.path.exists(avatar_path):
            avatar = Image.open(avatar_path)
        else:
            # Create a default avatar if none is provided
            avatar = Image.new('RGB', (avatar_size, avatar_size), color=(200, 200, 200))
            if os.path.exists(self.default_avatar):
                avatar = Image.open(self.default_avatar)

        avatar = avatar.resize((avatar_size, avatar_size))

        # Create circular mask for avatar
        mask = Image.new('L', avatar.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
        avatar.putalpha(mask)

        # Wrap comment text to fit width
        padding = 20
        text_width = width - avatar_size - 3 * padding
        wrapped_text = textwrap.fill(comment_text, width=int(text_width / 7))

        # Calculate the height based on wrapped text
        lines = wrapped_text.count('\n') + 1
        line_height = comment_font.getbbox("Ay")[3] * 1.5
        text_height = int(lines * line_height)

        # Create the image with dark gray background
        height = max(avatar_size + 2 * padding, text_height + padding * 2) + 20
        comment_img = Image.new('RGBA', (width, height), color=(26, 26, 27, 220))
        draw = ImageDraw.Draw(comment_img)

        # Add avatar
        comment_img.paste(avatar, (padding, padding), avatar)

        # Add username
        username_position = (avatar_size + padding * 2, padding)
        draw.text(username_position, username, font=username_font, fill=(58, 160, 255))

        # Add comment text
        comment_position = (avatar_size + padding * 2, padding + 25)
        draw.text(comment_position, wrapped_text, font=comment_font, fill=(215, 218, 220))

        return comment_img

    def generate_comment_audio(self, comment):
        """Generate audio for a comment using text-to-speech.

        Args:
            comment (dict): Comment data including 'text'

        Returns:
            tuple: (audio_clip, audio_path)
        """

        # Generate the audio file
        audio_path = generate_audio_from_text(
            text=comment['text'],
            speaking_rate=1.0
        )

        # Create AudioFileClip
        audio_clip = AudioFileClip(audio_path)

        return audio_clip, audio_path

    def add_comments_to_video(self, video, comments_data):
        """
        Add multiple comments with audio to the video

        Args:
            video (VideoFileClip): The original video
            comments_data (list): List of dictionaries containing comment data

        Returns:
            CompositeVideoClip: The final video with comments added
        """
        video_clips = [video]
        audio_clips = []

        # Get original audio if it exists
        if video.audio:
            audio_clips.append(video.audio)

        for comment in comments_data:
            # Create comment image
            comment_img = self._create_reddit_comment(
                username=comment['username'],
                comment_text=comment['text'],
                avatar_path=comment.get('avatar'),
                width=int(video.w * 0.8)  # Make comment 80% of video width
            )

            # Convert PIL image to numpy array
            comment_array = np.array(comment_img)

            # Create image clip
            img_clip = ImageClip(comment_array)

            # Position comment at the bottom of the video
            position_x = (video.w - img_clip.w) // 2  # Center horizontally
            position_y = (video.h - img_clip.h) // 2  # Center vertically

            # Set duration and position
            img_clip = (img_clip
                        .set_position((position_x, position_y))
                        .set_start(comment['start_time'])
                        .set_duration(comment['duration']))

            video_clips.append(img_clip)

            # Generate and add audio for this comment
            audio_clip, _ = self.generate_comment_audio(comment)
            audio_clip = audio_clip.set_start(comment['start_time'])
            audio_clips.append(audio_clip)

        # Create composite video
        final_video = CompositeVideoClip(video_clips)

        # Combine all audio clips
        if audio_clips:
            from moviepy.editor import CompositeAudioClip
            final_audio = CompositeAudioClip(audio_clips)
            final_video = final_video.set_audio(final_audio)

        return final_video

    def write_videofile(self, video, output_path, codec='libx264'):
        """
        Write the video to a file and clean up temporary files

        Args:
            video (CompositeVideoClip): The video to write
            output_path (str): Path where to save the output video
            codec (str): Video codec to use

        Returns:
            str: Path to the output video
        """
        # Create cache directory if it doesn't exist
        cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
        os.makedirs(cache_dir, exist_ok=True)

        # Create path for temporary audio file in cache directory
        temp_audio_path = os.path.join(cache_dir, f"{os.path.basename(output_path)}TEMP_MPY_wvf_snd.mp3")

        # Use the temp_audiofile parameter to specify where the temp file should go
        video.write_videofile(output_path, codec=codec, temp_audiofile=temp_audio_path)

        # Clean up temporary audio files
        self._clean_temp_audio()

        return output_path

    def _clean_temp_audio(self):
        """Clean up temporary audio files"""
        import shutil
        if os.path.exists(self.audio_dir):
            shutil.rmtree(self.audio_dir)
            os.makedirs(self.audio_dir, exist_ok=True)

    def close(self):
        """Close video file and release resources."""
        self.video.close()
        self._clean_temp_audio()

    def trim_video_to_fit_comments(self, video, comments_data):
        """
        Trim the video to fit exactly the duration of the comments
        Args:
            video (VideoClip): The original video
            comments_data (list): List of dictionaries containing comment data with timing info

        Returns:
            VideoClip: The trimmed video
        """
        if not comments_data:
            return video

        # Calculate the total duration needed for all comments
        last_comment = max(comments_data, key=lambda x: x['start_time'] + x['duration'])
        total_duration = last_comment['start_time'] + last_comment['duration']

        # Simply trim the video to the required duration
        print(f"Trimming video to {total_duration} seconds")
        return video.subclip(0, min(total_duration, self.video.duration))
