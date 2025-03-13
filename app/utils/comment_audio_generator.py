import os
import tempfile
from typing import List

from moviepy.editor import AudioFileClip

from app.api.dto.reddit_dto import Comment
from app.utils.text_to_speech import generate_audio_from_text


def generate_comments_with_duration(comments: List[Comment], target_duration, pause_time=1, allow_exceed_duration=True):
    """
    Generate audio for comments that fit within the target duration using a fixed pause time.
    Comments that would cause the total duration to exceed the target are not used.

    Args:
        comments (list): List of Comment
        target_duration (float): Target total duration in seconds
        pause_time (float): Fixed pause time between comments in seconds
        allow_exceed_duration (bool): If True, include all comments even if they exceed target duration

    Returns:
        tuple: (processed_comments, cumulative_duration) - processed comments and their total duration
    """
    # Create a new list to hold comments that fit within the duration
    processed_comments = []

    # Create temp directory for audio files
    temp_audio_dir = os.path.join(tempfile.gettempdir(), "comment_audio")
    os.makedirs(temp_audio_dir, exist_ok=True)

    # Track cumulative duration including pauses
    cumulative_duration = 0

    # Process comments one by one until we hit the duration limit
    for comment in comments:
        # Generate audio with default speaking rate
        audio_file = generate_audio_from_text(text=comment.text, speaking_rate=1.0)

        # Get audio duration
        audio_clip = AudioFileClip(audio_file)
        comment_duration = audio_clip.duration
        audio_clip.close()

        # Calculate total duration if we include this comment
        # Add pause time if this isn't the first comment
        new_total = cumulative_duration + comment_duration
        if processed_comments:
            new_total += pause_time

        if new_total > target_duration and not allow_exceed_duration:
            break

        # Add comment to the processed list with duration and audio info
        comment_copy = comment.model_copy()
        comment_copy.duration = comment_duration
        # comment_copy.audio_path = audio_file
        comment_copy.start_time = cumulative_duration if len(
            processed_comments) == 0 else cumulative_duration + pause_time

        processed_comments.append(comment_copy)

        # Update the cumulative duration
        cumulative_duration = new_total

        if cumulative_duration > target_duration:
            break

    return processed_comments, cumulative_duration
