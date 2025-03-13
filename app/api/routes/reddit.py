from fastapi import APIRouter, Depends

from app.api.deps import get_reddit_service
from app.api.dto.reddit_dto import RedditCommentsRequest, RedditCommentsResponse
from app.services.reddit_service import RedditService

router = APIRouter(prefix="/reddit", tags=["Reddit Operations"])


@router.post("/fetch-comments/", response_model=RedditCommentsResponse)
async def fetch_reddit_comments(
        request: RedditCommentsRequest,
        reddit_service: RedditService = Depends(get_reddit_service)
) -> RedditCommentsResponse:
    """Fetch top comments from a Reddit post."""
    comments = reddit_service.fetch_top_comments(
        post_url=str(request.post_url),
        limit=request.limit
    )

    return RedditCommentsResponse(
        comments=comments,
        count=len(comments)
    )