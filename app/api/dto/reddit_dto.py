from pydantic import BaseModel, HttpUrl


class RedditCommentsRequest(BaseModel):
    post_url: HttpUrl
    limit: int = 10


class RedditCommentsResponse(BaseModel):
    comments: list[str]
    count: int