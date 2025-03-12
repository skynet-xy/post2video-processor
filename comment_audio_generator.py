import os
import tempfile
from moviepy.editor import AudioFileClip
from text_to_speech import generate_audio_from_text


def generate_comments_with_duration(comments, target_duration, pause_time=0.5):
    """
    Generate audio for comments that fit within the target duration using a fixed pause time.
    Comments that would cause the total duration to exceed the target are dropped.

    Args:
        comments (list): List of comment dictionaries with 'username', 'text', etc.
        target_duration (float): Target total duration in seconds
        pause_time (float): Fixed pause time between comments in seconds

    Returns:
        list: The comments that fit within the duration with added duration, start_time and audio_path fields
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
        audio_file = generate_audio_from_text(text=comment["text"], speaking_rate=1.0)

        # Get audio duration
        audio_clip = AudioFileClip(audio_file)
        comment_duration = audio_clip.duration
        audio_clip.close()

        # Calculate total duration if we include this comment
        # Add pause time if this isn't the first comment
        new_total = cumulative_duration + comment_duration
        if processed_comments:
            new_total += pause_time

        # If adding this comment would exceed the target duration, stop here
        if new_total > target_duration:
            # Clean up unused audio file
            if os.path.exists(audio_file):
                os.remove(audio_file)
            break

        # Add comment to the processed list with duration and audio info
        comment_copy = comment.copy()
        comment_copy["duration"] = comment_duration
        comment_copy["audio_path"] = audio_file
        comment_copy["start_time"] = cumulative_duration if len(
            processed_comments) == 0 else cumulative_duration + pause_time

        processed_comments.append(comment_copy)

        # Update the cumulative duration
        cumulative_duration = new_total

    return processed_comments, cumulative_duration


def save_comments_with_duration(comments, target_duration, output_file=None):
    """
    Generate and save comments with audio files that match the target duration.

    Args:
        comments (list): List of comments
        target_duration (float): Target duration in seconds
        output_file (str, optional): Path to save the comments data

    Returns:
        list: Processed comments with duration information
    """
    processed_comments = generate_comments_with_duration(comments, target_duration)

    # Optionally save to file
    if output_file:
        import json
        # Remove non-serializable data before saving
        save_data = []
        for comment in processed_comments:
            comment_data = comment.copy()
            save_data.append(comment_data)

        with open(output_file, 'w') as f:
            json.dump(save_data, f, indent=2)

    return processed_comments
