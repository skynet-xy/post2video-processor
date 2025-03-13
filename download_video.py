import os

import yt_dlp as youtube_dl


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
        'outtmpl': os.path.join(output_path, f'%(id)s-standard-%(title,sanitize)s.%(ext)s'),
        'noplaylist': True,
        'restrictfilenames': True,
        'trim_file_name': len(output_path) + 64,
        'overwrites': False,
        'external_downloader': 'aria2c',  # Use aria2c for faster downloads
        'external_downloader_args': ['-x', '16', '-k', '1M']  # 16 connections, 1M chunk size
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_title = ydl.prepare_filename(info_dict)
        return video_title, info_dict


if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=ZkHKGWKq9mY"  # Example URL
    title, _ = download_youtube_video(youtube_url, output_path="assets/video_templates")
    print(title)
