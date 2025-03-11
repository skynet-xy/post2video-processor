import subprocess

def trim_video(video_path, trim_length, output_file):
    try:
        # Construct the ffmpeg command
        command = [
            'ffmpeg',
            '-i', video_path,
            '-t', trim_length,
            '-c', 'copy',
            output_file
        ]

        # Run the ffmpeg command
        subprocess.run(command, check=True)
        print(f"Trimmed video saved as {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    video_path = "download/ZkHKGWKq9mY.mp4"  # Example path
    trim_length = "00:01:43"  # Example trim length
    output_file = "output/trimmed_video.mp4"  # Example output file name

    trim_video(video_path, trim_length, output_file)