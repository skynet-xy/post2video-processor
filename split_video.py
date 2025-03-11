import cv2
import os

def split_video(video_path, duration, output_dir="output"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video file {video_path}")

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_duration = total_frames / fps

    num_clips = int(video_duration // duration) + 1
    base_name = os.path.basename(video_path)
    name, ext = os.path.splitext(base_name)

    for i in range(num_clips):
        start_frame = int(i * duration * fps)
        end_frame = int(min((i + 1) * duration * fps, total_frames))
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        output_file = os.path.join(output_dir, f"{name}_part{i+1}{ext}")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_file, fourcc, fps, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

        for j in range(start_frame, end_frame):
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)

        out.release()
        print(f"Created clip: {output_file} from frame {start_frame} to {end_frame}")

    cap.release()
    print("Video splitting completed.")

if __name__ == "__main__":
    video_path = "download/ZkHKGWKq9mY.mp4"  # Example path
    duration_in_minutes = 1.43  # Example duration
    duration_in_seconds = duration_in_minutes * 60
    try:
        split_video(video_path, duration_in_seconds)
    except Exception as e:
        print(f"Error occurred: {e}")