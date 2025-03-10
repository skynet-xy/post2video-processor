from reddit_comment_overlay import RedditCommentOverlay

# Path to your input video
INPUT_VIDEO = "input_video.mp4"
OUTPUT_VIDEO = "output_video.mp4"

# Create the overlay processor
overlay = RedditCommentOverlay(INPUT_VIDEO)

# Define comments to overlay on the video
comments = [
    {
        "username": "JohnDoe123",
        "text": "This video is hilarious! I can't stop watching it over and over again.",
        "avatar": "assets/avatar1.png",  # Optional, uses default if not provided
        "start_time": 2.0,  # Start 2 seconds into the video
        "duration": 4.0     # Display for 4 seconds
    },
    {
        "username": "VideoFan42",
        "text": "I think this deserves to go viral! So clever and well made.",
        "avatar": "assets/avatar2.png",
        "start_time": 7.0,
        "duration": 3.5
    },
    {
        "username": "TechExpert",
        "text": "The way you edited this is amazing. What software did you use?",
        "start_time": 12.0,
        "duration": 4.0
    }
]

# Process the video with the comments
output_path = overlay.add_comments_to_video(comments, OUTPUT_VIDEO)

print(f"Video successfully created at: {output_path}")

# Clean up resources
overlay.close()