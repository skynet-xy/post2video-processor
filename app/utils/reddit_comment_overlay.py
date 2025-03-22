import os
import textwrap
import uuid
from datetime import datetime
from typing import List

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

from app.api.dto.reddit_dto import Comment
from app.core.config import settings
from app.utils.text_to_speech import generate_comment_audio


def _create_reddit_comment(username, comment_text, avatar_path=None, width=500, font_dir=None, default_avatar=None):
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
    if font_dir is None:
        font_dir = settings.FONTS_DIR

    if default_avatar is None:
        default_avatar = settings.DEFAULT_AVATAR

    try:
        username_font = ImageFont.truetype(os.path.join(font_dir, "arial_bold.ttf"), 16)
        comment_font = ImageFont.truetype(os.path.join(font_dir, "arial.ttf"), 14)
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
        if os.path.exists(default_avatar):
            avatar = Image.open(default_avatar)

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


def _create_reddit_title(title_text, width=800, avatar_path=None, default_avatar=None):
    """
    Create a Reddit post title card that looks similar to but distinct from comments

    Args:
        title_text (str): The title of the Reddit post
        width (int): Width of the comment image
        avatar_path (str, optional): Path to avatar image
        default_avatar (str, optional): Path to default avatar if none provided

    Returns:
        PIL.Image: Image containing the rendered title card
    """

    font_dir = settings.FONTS_DIR
    # Set up fonts - make title font larger than comment font
    title_font = ImageFont.truetype(os.path.join(font_dir, "arial_bold.ttf"), 22)
    font = ImageFont.truetype(os.path.join(font_dir, "arial.ttf"), 14)


    # Avatar setup (same as comment function)
    avatar_size = 40
    if avatar_path and os.path.exists(avatar_path):
        avatar = Image.open(avatar_path)
    else:
        # Create a default avatar if none is provided
        avatar = Image.new('RGB', (avatar_size, avatar_size), color=(200, 200, 200))
        if default_avatar and os.path.exists(default_avatar):
            avatar = Image.open(default_avatar)

    avatar = avatar.resize((avatar_size, avatar_size))

    # Create circular mask for avatar
    mask = Image.new('L', avatar.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
    avatar.putalpha(mask)

    # Wrap title text to fit width
    padding = 20
    text_width = width - avatar_size - 3 * padding
    wrapped_text = textwrap.fill(title_text, width=int(text_width / 7))

    # Calculate the height based on wrapped text
    lines = wrapped_text.count('\n') + 1
    line_height = title_font.getbbox("Ay")[3] * 1.5
    text_height = int(lines * line_height)

    # Create the image with slightly different background (orangish-red for Reddit title)
    height = max(avatar_size + 2 * padding, text_height + padding * 2) + 30  # Make title card slightly taller
    title_img = Image.new('RGBA', (width, height), color=(36, 36, 38, 230))  # Darker background for title
    draw = ImageDraw.Draw(title_img)

    # Add a reddit post indicator bar on the left
    draw.rectangle([(0, 0), (6, height)], fill=(255, 69, 0))  # Reddit orange

    # Add avatar
    title_img.paste(avatar, (padding, padding), avatar)

    # Add "POST TITLE" indicator
    indicator_position = (avatar_size + padding * 2, padding)
    draw.text(indicator_position, "POST TITLE", font=font, fill=(255, 69, 0))

    # Add title text
    title_position = (avatar_size + padding * 2, padding + 25)
    draw.text(title_position, wrapped_text, font=title_font, fill=(240, 240, 245))

    return title_img


def add_comments_to_video(video, comments_data: List[Comment], lang, voice):
    """
    Add multiple comments with audio to the video

    Args:
        video (VideoFileClip): The original video
        comments_data (list): List of Comment
        lang (str): language code (e.g., 'en-US')
        voice (str): voice name (e.g., 'en-US-Standard-D')

    Returns:
        CompositeVideoClip: The final video with comments added
    """
    video_clips = [video]
    audio_clips = []

    # Get original audio if it exists
    if video.audio:
        audio_clips.append(video.audio)

    for comment in comments_data:
        # Check if this is a title or regular comment
        if hasattr(comment, 'is_title') and comment.is_title:
            # Create title card
            comment_img = _create_reddit_title(
                title_text=comment.text,
                avatar_path=comment.avatar,
                width=int(video.w * 0.8)  # Make title 80% of video width
            )
        else:
            # Create regular comment image
            comment_img = _create_reddit_comment(
                username=comment.username,
                comment_text=comment.text,
                avatar_path=comment.avatar,
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
                    .set_start(comment.start_time)
                    .set_duration(comment.duration))

        video_clips.append(img_clip)

        # Generate and add audio for this comment
        audio_clip, _ = generate_comment_audio(comment, lang, voice)
        audio_clip = audio_clip.set_start(comment.start_time)
        audio_clips.append(audio_clip)

    # Create composite video
    final_video = CompositeVideoClip(video_clips)

    # Combine all audio clips
    if audio_clips:
        from moviepy.editor import CompositeAudioClip
        final_audio = CompositeAudioClip(audio_clips)
        final_video = final_video.set_audio(final_audio)

    return final_video


def write_videofile(video, output_dir= None, codec='libx264', cache_dir=None):
    """
    Write the video to a file with a unique filename in the specified directory

    Args:
        video (CompositeVideoClip): The video to write
        output_dir (str): Directory where to save the output video
        codec (str): Video codec to use
        cache_dir (str, optional): Directory for temporary cache files

    Returns:
        str: Path to the output video
    """

    if cache_dir is None:
        cache_dir = settings.CACHE_DIR

    if output_dir is None:
        output_dir = settings.OUTPUT_DIR

    # Create directories if they don't exist
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # Generate unique filename with timestamp and UUID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"video_{timestamp}_{unique_id}.mp4"
    output_path = os.path.join(output_dir, filename)

    # Create path for temporary audio file in cache directory
    temp_audio_path = os.path.join(cache_dir, f"{filename}_TEMP_MPY_wvf_snd.mp3")

    # Use the temp_audiofile parameter to specify where the temp file should go
    video.write_videofile(output_path, codec=codec, temp_audiofile=temp_audio_path)

    # Clean up temporary audio file
    if os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)

    return output_path
