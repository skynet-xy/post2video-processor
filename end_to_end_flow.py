import os
from download_video import download_and_fetch_transcript
from split_video import split_video
from create_video import get_first_video_in_directory, get_video_length, generate_comments
from reddit_comment_overlay import RedditCommentOverlay

def main():
    # Default configuration
    youtube_url = "https://www.youtube.com/watch?v=ZkHKGWKq9mY"  # Example URL
    download_dir = "download"
    output_dir = "output"
    duration_in_minutes = 1.43  # Example duration
    segment_length = duration_in_minutes * 60
    final_output = "final_output.mp4"

    # Step 1: Download the YouTube video
    print("STEP 1: Downloading YouTube video...")
    video_path = download_and_fetch_transcript(youtube_url, download_dir)
    if not video_path:
        print("Error: Failed to download video. Exiting.")
        return
    print(f"Video downloaded successfully: {video_path}")

    # Step 2: Split the video into segments
    print(f"\nSTEP 2: Splitting video into segments of {segment_length} seconds length...")
    try:

        split_video(video_path, segment_length, output_dir)
        print(f"Video successfully split into segments in {output_dir}")
    except Exception as e:
        print(f"Error during video splitting: {e}")
        return

    # Step 3: Create video with Reddit comments overlay
    print("\nSTEP 3: Adding Reddit comments overlay to the first segment...")
    first_segment = get_first_video_in_directory(output_dir)
    if not first_segment:
        print("Error: No split video segments found. Exiting.")
        return

    try:
        video_length = get_video_length(first_segment)
        overlay = RedditCommentOverlay(first_segment)
        comments = generate_comments(video_length)
        output_path = overlay.add_comments_to_video(comments, final_output)
        overlay.close()
        print(f"Final video with comments created successfully: {output_path}")
    except Exception as e:
        print(f"Error creating video with comments: {e}")
        return

    print("\nComplete workflow finished successfully!")
    print(f"1. Downloaded video: {video_path}")
    print(f"2. Split video segments: {output_dir}")
    print(f"3. Final video with comments: {final_output}")

if __name__ == "__main__":
    main()