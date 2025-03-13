import praw


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

        # Only get top-level comments (no children) and respect the limit
        top_comments = [comment.body for comment in submission.comments[:limit]]

        return top_comments
