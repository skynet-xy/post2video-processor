import praw

from app.api.dto.reddit_dto import Comment


class RedditService:
    def __init__(self, reddit_client_id, reddit_client_secret, reddit_user_agent):
        self.reddit_client_id = reddit_client_id
        self.reddit_client_secret = reddit_client_secret
        self.reddit_user_agent = reddit_user_agent

    def fetch_top_comments(self, post_url: str, limit: int = 10):
        reddit = praw.Reddit(client_id=self.reddit_client_id,
                             client_secret=self.reddit_client_secret,
                             user_agent=self.reddit_user_agent)

        submission = reddit.submission(url=post_url)
        submission.comment_sort = "top"  # Sort by top comments
        submission.comments.replace_more(limit=0)  # Don't expand "load more comments"

        comments = []
        for comment in submission.comments[:limit]:
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

        return comments