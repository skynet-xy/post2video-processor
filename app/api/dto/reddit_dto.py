from pydantic import BaseModel, HttpUrl

class Comment(BaseModel):
    username: str
    text: str
    avatar: str
    # position_x: int = 10  # X position (px from left)
    # position_y: int = 10  # Y position (px from top)
    # font_size: int = 24   # Font size
    # color: str = "white"  # Text color


class RedditCommentsRequest(BaseModel):
    post_url: HttpUrl
    limit: int = 10


class RedditCommentsResponse(BaseModel):
    comments: list[Comment]
    count: int
