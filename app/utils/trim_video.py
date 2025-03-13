def trim_video_to_fit_comments(video, comments_data):
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
    return video.subclip(0, min(total_duration, video.duration))
