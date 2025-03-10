# Reddit Comment Video Overlay Tool

This tool allows you to overlay Reddit-style comments on existing videos. Each comment can include:
- Custom avatar image
- Username
- Comment text
- Specific start time and duration

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install moviepy pillow
```

3. Download some font files (Arial and Arial Bold) and place them in the `fonts` directory:
   - `fonts/arial.ttf`
   - `fonts/arial_bold.ttf`

## Usage

1. Place your video file in the project directory
2. Modify the `create_video.py` script with your comments:

```python
comments = [
    {
        "username": "RedditUser123",
        "text": "Your comment text here",
        "avatar": "path/to/avatar.png",  # Optional
        "start_time": 2.0,  # When to show the comment (seconds)
        "duration": 4.0     # How long to show the comment (seconds)
    },
    # Add more comments as needed
]
```

3. Run the script:

```bash
python create_video.py
```

4. Find the output video in the location specified in the script

## Customization

- Adjust the comment style by modifying the `create_reddit_comment` function
- Change comment positioning by modifying the position values in `add_comments_to_video`

## Requirements

- Python 3.6+
- MoviePy
- Pillow (PIL)