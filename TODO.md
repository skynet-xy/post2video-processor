# VIDEO

- [x] Crawl reddit comment
    - [x] Username
    - [x] Subreddit
    - [x] Avatar
    - [x] Comment
    - [x] Upvote
    - [x] Downvote

- [x] Create an image of comment from the content of comment
  - [x] Input: 1 reddit comment
  - [x] Output: 1 image of comment (avatar, username, comment, upvote, downvote + may cai nut khac(back,...))

# Text To Speech
- [x] Input: 1 loat cac reddit comments
- [x] Output: 1 doan audio
## API

# Transcript
## Sample
```json
[
    {
        "username": "JohnDoe123",
        "text": "This video is hilarious! I can't stop watching it over and over again.",
        "avatar": "assets/avatar1.png",
        "start_time": 2.0,
        "duration": 4.0
    },
    {
        "username": "VideoFan42",
        "text": "I think this deserves to go viral! So clever and well made.",
        "avatar": "assets/avatar2.png",
        "start_time": 7.0,
        "duration": 3.5
    },
    {
        "username": "TechExpert",
        "text": "The way you edited this is amazing. What software did you use?",
        "start_time": 12.0,
        "duration": 4.0
    }
]
```
## Cong thuc
- [x] Tinh toan xem la 1 cai comment dai 30 word -> bao nhieu giay
## Lay tu audio
- Lay transcript tu audio (Whisper)

# Gop cac thu vao
- [x] Input: 1 video minecraft parkour, 1 audio, 1 loat anh cac comment, 1 transcription
- [x] Output: video hoan chinh

# FastAPI
- [ ] APi cho front end

# Input
- User se chuyen vao
  - Link reddit
  - Chon template video co san 
  - Chon voice text-to-speech
  - Ratio cua output video
  - Cho chon do dai video 