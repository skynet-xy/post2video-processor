# FastAPI Video Trimming Service

This service provides an API to trim videos using FastAPI.

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
  pip install -r requirements.txt
```

## Usage

1. Start the FastAPI server:

```bash
  uvicorn app.main:app --reload
```

2. Download a video file
```shell
python download_video.py
```
3. Send a POST request to the `/api/video/add-reddit-comments/` endpoint:
Example:

```bash
curl -X POST "http://localhost:8000/api/video/add-reddit-comments/" \
  -H "Content-Type: application/json" \
  -d '{
    "video_name": "ZkHKGWKq9mY-standard-6_Minutes_Minecraft_Shader_Parkour_Gamepla.mp4",
    "comments": [
      {
        "text": "This is a sample comment",
        "time_start": 1.5,
        "time_end": 6.5
      },
      {
        "text": "Another comment example",
        "time_start": 8.0,
        "time_end": 12.0
      }
    ]
  }'
```
  
## Requirements

- Python 3.6+
- FastAPI
- Uvicorn
- Requests
```

## Project Structure

- `app/main.py`: The main FastAPI application
- `app/api/routes/video.py`: The video trimming endpoint
- `test_fast_api.py`: Test script for the video trimming endpoint
```