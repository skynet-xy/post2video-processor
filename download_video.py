import os

import yt_dlp as youtube_dl
from moviepy.editor import VideoFileClip


def crop_to_vertical(video_path, output_path=None, target_ratio=9 / 16, audio_codec: str | bool = "aac"):
    """
    Crop a landscape video to vertical format by trimming left and right sides.

    Args:
        video_path: Path to the video file
        output_path: Path for the output file (if None, will append '_vertical' to original)
        target_ratio: Target aspect ratio as width/height (default 9/16 for vertical)
        audio_codec: Audio codec to use for the output video

    Returns:
        Path to the cropped video
    """
    if output_path is None:
        filename, ext = os.path.splitext(video_path)
        output_path = f"{filename}_vertical{ext}"

    clip = VideoFileClip(video_path)

    # Calculate dimensions for the crop
    original_width, original_height = clip.size
    new_width = int(original_height * target_ratio)

    # Calculate left crop to center the video
    x_center = original_width / 2
    x1 = int(x_center - new_width / 2)

    # Crop the video
    cropped_clip = clip.crop(x1=x1, y1=0, width=new_width, height=original_height)

    # Write the cropped video
    cropped_clip.write_videofile(output_path, codec="libx264", audio_codec=audio_codec)

    # Close the clips to release resources
    clip.close()
    cropped_clip.close()

    return output_path


def download_youtube_video(url, output_path=".", height=720, make_vertical=False, tag: str = None):
    dl_format = f'bestvideo[height={height}]'
    resolution_tag = str(height) + "p"
    ydl_opts = {
        'format': dl_format,
        'outtmpl': os.path.join(output_path, f'%(id)s-{resolution_tag}-{tag}-%(title,sanitize)s.%(ext)s'),
        'noplaylist': True,
        'restrictfilenames': True,
        'trim_file_name': len(output_path) + 32,
        'overwrites': False,
        'external_downloader': 'aria2c',  # Use aria2c for faster downloads
        'external_downloader_args': ['-x', '16', '-k', '1M'],  # 16 connections, 1M chunk size
        'cookiefile': 'generated/cookies.txt' if os.path.exists('generated/cookies.txt') else None,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info_dict)
        if make_vertical:
            video_path = crop_to_vertical(video_path, audio_codec=False)

        return video_path, info_dict


if __name__ == "__main__":
    minecraft_youtube_urls = {
        "https://www.youtube.com/watch?v=ZkHKGWKq9mY",
        "https://www.youtube.com/watch?v=NX-i0IWl3yg",
        "https://www.youtube.com/watch?v=AsetdKZN11o",
        "https://www.youtube.com/watch?v=-Gm27KL-JKI",
        "https://www.youtube.com/watch?v=CiidOooHG7U",
        "https://www.youtube.com/watch?v=cz_y5nCzGMw",
    }
    for url in minecraft_youtube_urls:
        title, _ = download_youtube_video(url, output_path="assets/video_templates", height=720, make_vertical=True, tag="minecraft")
        print(title)
        title, _ = download_youtube_video(url, output_path="assets/video_templates", height=1080, make_vertical=True, tag="minecraft")
        print(title)
