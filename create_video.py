from moviepy.editor import VideoFileClip
import os
from reddit_comment_overlay import RedditCommentOverlay


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


def calculate_comment_duration(text):
    # Simple heuristic to calculate duration based on text length
    return max(3.0, len(text) * 0.1)


def generate_comments(video_duration, num_comments=10):
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
            "username": "FoodieGal", "text": "I can't believe how good this video is. The food shots are mouth-watering.",
            "avatar": "assets/avatar2.png",
        },
        {
            "username": "FitnessFreak", "text": "This is the motivation I needed today. Keep up the great work!",
            "avatar": "assets/avatar2.png",
        }]
    total_comments = len(comments)
    interval = video_duration / total_comments
    for i, comment in enumerate(comments):
        comment["start_time"] = i * interval
        comment["duration"] = calculate_comment_duration(comment["text"])
    return comments


if __name__ == '__main__':
    OUTPUT_DIR = "./output"
    # Path to your input video
    INPUT_VIDEO = get_first_video_in_directory(OUTPUT_DIR)
    OUTPUT_VIDEO = "output_video.mp4"

    if not INPUT_VIDEO:
        print("No input video found. Please ensure there are videos in the output directory.")
        exit(1)

    video_length = get_video_length(INPUT_VIDEO)

    # Create the overlay processor
    overlay = RedditCommentOverlay(INPUT_VIDEO)
    comments = generate_comments(video_length)  # Assuming the video duration is 60 seconds
    output_path = overlay.add_comments_to_video(comments, OUTPUT_VIDEO)

    print(f"Video successfully created at: {output_path}")

    # Clean up resources
    overlay.close()
