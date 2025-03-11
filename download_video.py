import os
import yt_dlp as youtube_dl
import threading
from youtube_transcript_api import YouTubeTranscriptApi

def download_youtube_video(url, output_path="."):
    # ydl_opts = {
    #     'format': 'bestvideo[height>=720]+bestaudio[ext=m4a]/best[height>=720]',
    #     'merge_output_format': 'mp4',
    #     'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
    #     'noplaylist': True,
    #     'external_downloader': 'aria2c',  # Use aria2c for faster downloads
    #     'external_downloader_args': ['-x', '16', '-k', '1M']  # 16 connections, 1M chunk size
    # }
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'noplaylist': True
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_title = ydl.prepare_filename(info_dict)
        return video_title, info_dict

def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print(f"Could not fetch transcript: {e}")
        return None

def download_and_fetch_transcript(youtube_url, download_dir="download"):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    print("Downloading video...")

    download_thread = threading.Thread(target=download_youtube_video, args=(youtube_url, download_dir))
    download_thread.start()

    download_thread.join()

    try:
        video_path, info_dict = download_youtube_video(youtube_url, download_dir)
    except Exception as e:
        print(f"Failed to download video: {e}")
        return

    video_id = info_dict.get("id")
    print("Fetching transcript...")
    transcript = fetch_transcript(video_id)

    if transcript:
        try:
            with open(os.path.join(download_dir, f"{info_dict['title']}_transcript.txt"), "w", encoding="utf-8") as f:
                for line in transcript:
                    f.write(f"{line['start']} - {line['duration']}: {line['text']}\n")
        except Exception as e:
            print(f"Failed to write transcript: {e}")

    print("Download and transcript fetch completed.")
    return video_path

if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=ZkHKGWKq9mY"  # Example URL
    download_and_fetch_transcript(youtube_url)