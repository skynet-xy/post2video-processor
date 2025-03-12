import requests

url = 'http://localhost:8000/api/video/trim/'
files = {'file': open('download/ZkHKGWKq9mY_lowres.mp4', 'rb')}
data = {'start_time': 0, 'end_time': 103}

response = requests.post(url, files=files, data=data)
with open('trimmed_video.mp4', 'wb') as f:
    f.write(response.content)