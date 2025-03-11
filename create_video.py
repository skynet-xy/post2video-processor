import os
import tempfile

from moviepy.editor import VideoFileClip, AudioFileClip

from reddit_comment_overlay import RedditCommentOverlay
from text_to_speech import generate_audio_from_text


def get_first_video_in_directory(directory="./output"):
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


def get_video_length(video_path):
    clip = VideoFileClip(video_path)
    duration = clip.duration
    clip.close()
    return duration


# In the generate_comments function
def generate_comments():
    # Define comments to overlay on the video
    comments = [
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

    total_comments = len(comments)

    # Create temp directory for audio files
    temp_audio_dir = os.path.join(tempfile.gettempdir(), "comment_audio")
    os.makedirs(temp_audio_dir, exist_ok=True)

    start_time: int = 0
    sleep_between_comments = 1  # Sleep for 1 second between comments
    for i, comment in enumerate(comments):
        comment["start_time"] = start_time

        # Generate audio and get its duration
        audio_file = generate_audio_from_text(
            text=comment["text"],
            output_file=os.path.join(temp_audio_dir, f"comment_{i}.mp3")
        )

        # Get audio duration using moviepy
        audio_clip = AudioFileClip(audio_file)
        comment["duration"] = audio_clip.duration
        start_time = start_time + comment["duration"] + sleep_between_comments
        audio_clip.close()

        # Store audio path for later use
        comment["audio_path"] = audio_file

    return comments


if __name__ == '__main__':
    OUTPUT_DIR = "./output"
    # Path to your input video
    INPUT_VIDEO = get_first_video_in_directory(OUTPUT_DIR)
    OUTPUT_VIDEO = OUTPUT_DIR + "/output_video.mp4"

    if not INPUT_VIDEO:
        print("No input video found. Please ensure there are videos in the output directory.")
        exit(1)

    # Create the overlay processor
    overlay = RedditCommentOverlay(INPUT_VIDEO)
    comments = generate_comments()
    output_path = overlay.add_comments_to_video(comments, OUTPUT_VIDEO)

    print(f"Video successfully created at: {output_path}")

    # Clean up resources
    overlay.close()
