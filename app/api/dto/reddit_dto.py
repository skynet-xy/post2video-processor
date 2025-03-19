from pydantic import BaseModel, HttpUrl, Field


class Comment(BaseModel):
    username: str
    text: str
    avatar: str
    start_time: float = Field(0, exclude=True)
    duration: float = Field(0, exclude=True)
    # position_x: int = 10  # X position (px from left)
    # position_y: int = 10  # Y position (px from top)
    # font_size: int = 24   # Font size
    # color: str = "white"  # Text color


class RedditCommentsRequest(BaseModel):
    post_url: HttpUrl
    limit: int = 10


class RedditCommentsResponse(BaseModel):
    title: str
    comments: list[Comment]
    count: int
