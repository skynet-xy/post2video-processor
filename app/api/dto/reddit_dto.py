from typing import Optional

from pydantic import BaseModel, HttpUrl, Field


class Comment(BaseModel):
    username: str
    text: str
    avatar: Optional[str] = ''
    upvote: Optional[int] = Field(0, description="Number of upvote for the comment")
    start_time: float = Field(0, exclude=True)
    duration: Optional[float] = Field(0.0, exclude=True)
    is_title: Optional[bool] = Field(False, exclude=True)
    # position_x: int = 10  # X position (px from left)
    # position_y: int = 10  # Y position (px from top)
    # font_size: int = 24   # Font size
    # color: str = "white"  # Text color


class RedditCommentsRequest(BaseModel):
    post_url: HttpUrl = Field(
        default="https://www.reddit.com/r/AskReddit/comments/1jh1232/which_celebrity_gives_you_i_sold_my_soul_to_the/",
        description="URL of the Reddit post to fetch comments from"
    )
    limit: int = 10


class RedditCommentsResponse(BaseModel):
    title: str
    comments: list[Comment]
    count: int
