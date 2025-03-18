import asyncpraw

from app.api.dto.reddit_dto import Comment


class RedditService:
    def __init__(self, reddit_client_id, reddit_client_secret, reddit_user_agent):
        self.reddit_client_id = reddit_client_id
        self.reddit_client_secret = reddit_client_secret
        self.reddit_user_agent = reddit_user_agent

    async def fetch_top_comments(self, post_url: str, limit: int = 10):
        reddit = asyncpraw.Reddit(client_id=self.reddit_client_id,
                               client_secret=self.reddit_client_secret,
                               user_agent=self.reddit_user_agent)

        submission = await reddit.submission(url=post_url)
        submission.comment_sort = "top"  # Sort by top comments
        await submission.comments.replace_more(limit=0)  # Don't expand "load more comments"

        comments = []
        async for comment in submission.comments:
            if len(comments) >= limit:
                break

            # Extract username and comment text
            username = comment.author.name if comment.author else "[deleted]"
            text = comment.body
            # Use Reddit's default avatar as a placeholder
            avatar = "/avatar_default_0.png"

            comments.append(Comment(
                username=username,
                text=text,
                avatar=avatar
            ))

        await reddit.close()  # Important to close the connection when done

        return {
            "title": submission.title,
            "comments": comments
        }