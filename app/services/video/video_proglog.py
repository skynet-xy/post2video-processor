from proglog import ProgressLogger

from app.db.redis import get_sync_redis


class VideoProgLog(ProgressLogger):
    def __init__(self, job_code: str, **kw):
        self.is_video_process = False
        self.job_code = job_code
        self.last_percentage = 0
        super().__init__(**kw)

    def update(self, percentage):
        try:
            redis_client = get_sync_redis()
            key = f"video_progress:{self.job_code}"
            redis_client.set(key, str(percentage))
            print(f"VideoProgLog: {key} - {percentage}")
            redis_client.close()
        except Exception as e:
            print(f"Error updating Redis: {str(e)}")

    def callback(self, **kw):
        if ('message' in kw) and kw['message']:
            if not self.is_video_process and isinstance(kw['message'], str) and kw['message'].startswith('Moviepy - Writing video'):
                self.is_video_process = True
            print("VideoProgLog: " + kw['message'])

    def iter_bar(self, **kw):
        _, iterable = kw.popitem()
        iter_len = len(iterable)

        def new_iterable():
            for i, it in enumerate(iterable):
                percentage = i / iter_len * 100
                if percentage - self.last_percentage >= 1 and self.is_video_process:
                    self.last_percentage = percentage
                    self.update(percentage=percentage)
                yield it

        return new_iterable()
