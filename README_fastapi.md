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

2. Send a POST request to the `/api/video/trim/` endpoint with the following parameters:
    - `file`: The video file to be trimmed
    - `start_time`: The start time in seconds
    - `end_time`: The end time in seconds

Example using `requests` in Python:

```python
import requests

url = 'http://localhost:8000/api/video/trim/'
files = {'file': open('path/to/your/video.mp4', 'rb')}
data = {'start_time': 0, 'end_time': 103}

response = requests.post(url, files=files, data=data)
with open('trimmed_video.mp4', 'wb') as f:
    f.write(response.content)
```
or 
```bash
    curl -X 'POST' \
      'http://localhost:8000/api/video/trim/' \
      -H 'accept: application/json' \
      -H 'Content-Type: multipart/form-data' \
      -F 'file=@path/to/video.mp4' \
      -F 'start_time=0' \
      -F 'end_time=103' \
      --output trimmed_video.mp4
```
  
## Endpoints

- `GET /`: Returns a welcome message
- `POST /api/video/trim/`: Trims the provided video file based on the start and end times

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