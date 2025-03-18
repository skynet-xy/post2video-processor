import os
from pathlib import Path

from moviepy.editor import VideoFileClip

from app.api.dto.reddit_dto import Comment
from app.core.config import settings
from app.utils.comment_audio_generator import generate_comments_with_duration
from app.utils.reddit_comment_overlay import add_comments_to_video, write_videofile
from app.utils.trim_video import trim_video_to_fit_comments


def convert_dict_comments_to_objects(comment_dicts):
    """Convert a list of comment dictionaries to Comment objects"""
    return [Comment(**comment_dict) for comment_dict in comment_dicts]


def get_first_video_in_directory(directory="./assets/video_templates"):
    # Create directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
        return None

    # List all files and filter for common video extensions
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    video_files = [f for f in os.listdir(directory)
                   if os.path.isfile(os.path.join(directory, f)) and
                   os.path.splitext(f)[1].lower() in video_extensions]

    if not video_files:
        print(f"No video files found in {directory}")
        return None

    # Return the first video file found
    return os.path.join(directory, video_files[0])


# In the generate_comments function
def generate_comments():
    # Define comments to overlay on the video
    comment_dicts = [
        {
            "username": "JohnDoe123",
            "text": "This video is hilarious! I can't stop watching it over and over again.",
            "avatar": "assets/avatar1.png",  # Optional, uses default if not provided
        },
        {
            "username": "VideoFan42",
            "text": "I think this deserves to go viral! So clever and well made.",
            "avatar": "assets/avatar2.png",
        },
        {
            "username": "TechExpert", "text": "The way you edited this is amazing. What software did you use?",
            "avatar": "assets/avatar2.png",
        },
        {
            "username": "MovieBuff89", "text": "Incredible! This is one of the best videos I've seen in a while.",
            "avatar": "assets/avatar2.png",
        },
        {
            "username": "GamerPro", "text": "Wow, the editing here is on another level. Great job!",
            "avatar": "assets/avatar2.png",
        },
        {
            "username": "NatureLover", "text": "Such a beautiful video. The scenes and music are perfect together.",
            "avatar": "assets/avatar2.png",
        },
        {
            "username": "MusicManiac", "text": "The soundtrack you chose fits perfectly with the visuals. Love it!",
            "avatar": "assets/avatar2.png",
        },
        {
            "username": "AdventureSeeker", "text": "This video makes me want to go on an adventure! So inspiring.",
            "avatar": "assets/avatar2.png",
        },
        {
            "username": "FoodieGal",
            "text": "I can't believe how good this video is. The food shots are mouth-watering.",
            "avatar": "assets/avatar2.png",
        },
        {
            "username": "FitnessFreak", "text": "This is the motivation I needed today. Keep up the great work!",
            "avatar": "assets/avatar2.png",
        }
    ]
    comment_objects = [Comment(**comment) for comment in comment_dicts]

    target_duration = 15.0  # Target duration in seconds
    processed_comments, duration = generate_comments_with_duration(comment_objects, target_duration,
                                                                   allow_exceed_duration=True)

    return processed_comments


if __name__ == '__main__':
    settings.CACHE_DIR = Path("/tmp/post2video")
    OUTPUT_DIR = "generated/output"
    # Path to your input video
    INPUT_VIDEO = get_first_video_in_directory(OUTPUT_DIR)
    OUTPUT_VIDEO = OUTPUT_DIR + "/output_video.mp4"

    if not INPUT_VIDEO:
        print("No input video found. Please ensure there are videos in the output directory.")
        exit(1)

    # Create the overlay processor
    video = VideoFileClip(INPUT_VIDEO)
    comments = generate_comments()
    video = add_comments_to_video(video, comments)
    video = trim_video_to_fit_comments(video, comments)
    output_path = write_videofile(video, OUTPUT_VIDEO)
    print(f"Video successfully created at: {output_path}")

    # Clean up resources
    video.close()
