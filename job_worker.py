#!/usr/bin/env python
import asyncio
import logging
import signal
import sys

from sqlalchemy import text

from app.core.config import settings
from app.db.redis import get_redis
from app.db.session import get_db
from app.services.video_service import VideoService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('job_worker.log')
    ]
)
logger = logging.getLogger('job_worker')


async def start_video_worker():
    """Worker process that processes video jobs from Redis queue"""
    logger.info("Starting video processing worker...")

    video_service = VideoService(
        output_dir=settings.OUTPUT_DIR,
        video_templates_dir=settings.VIDEO_TEMPLATES_DIR
    )

    while True:
        try:
            # Get Redis connection
            async with get_redis() as redis_client:
                # BRPOP blocks until a job is available, timeout=0 means block indefinitely
                result = await redis_client.brpop("video_processing_queue", timeout=0)

                if result:
                    # Extract job code from result tuple (key, value)
                    _, job_code = result
                    job_code = job_code.decode('utf-8')

                    logger.info(f"Received job code: {job_code} from queue")

                    # Get job details from database
                    async with get_db() as db:
                        db_session = db()
                        query = """
                        SELECT * FROM job_add_reddit_comment_overlay
                        WHERE job_code = :job_code AND status = 'pending'
                        """
                        result = await db_session.execute(text(query), {"job_code": job_code})
                        job = result.fetchone()

                        if job:
                            # Convert row to dict for processing
                            job_dict = dict(job)

                            # Update status to processing before actual processing
                            await db_session.execute(
                                text("""
                                UPDATE job_add_reddit_comment_overlay 
                                SET status = 'processing' 
                                WHERE job_code = :job_code
                                """),
                                {"job_code": job_code}
                            )
                            await db_session.commit()
                            logger.info(f"Updated job {job_code} to processing status")

                            # Process the job
                            await video_service.process_video_job(job_dict)
                        else:
                            logger.warning(f"Job {job_code} not found or not in pending status")

        except asyncio.CancelledError:
            logger.info("Worker shutting down...")
            break
        except Exception as e:
            logger.error(f"Error in video worker: {str(e)}", exc_info=True)
            # Wait before retrying to avoid tight error loops
            await asyncio.sleep(5)

async def process_pending_jobs():
    """Process any pending jobs that might have been missed"""
    logger.info("Checking for pending jobs...")

    try:
        async with get_db() as db:
            db_session = db()

            # Find jobs that are still pending
            result = await db_session.execute(
                text("""
                SELECT job_code FROM job_add_reddit_comment_overlay
                WHERE status = 'pending'
                ORDER BY created_at ASC
                LIMIT 10
                """)
            )

            pending_jobs = result.fetchall()

            if pending_jobs:
                logger.info(f"Found {len(pending_jobs)} pending jobs to process")
                async with get_redis() as redis_client:
                    for job in pending_jobs:
                        job_code = job[0]
                        # Add job back to the queue
                        await redis_client.lpush("video_processing_queue", job_code)
                        logger.info(f"Re-queued pending job {job_code}")
            else:
                logger.info("No pending jobs found")

    except Exception as e:
        logger.error(f"Error checking pending jobs: {str(e)}", exc_info=True)


async def shutdown(signal, loop):
    """Cleanup resources and shut down gracefully"""
    logger.info(f"Received exit signal {signal.name}...")

    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    for task in tasks:
        task.cancel()

    logger.info(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()
    logger.info("Shutdown complete")


async def main():
    """Main entry point for the worker"""
    loop = asyncio.get_event_loop()

    # Register signal handlers for graceful shutdown
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig, lambda s=sig: asyncio.create_task(shutdown(s, loop))
        )

    # Check for existing pending jobs before starting
    await process_pending_jobs()

    # Start the worker process
    try:
        logger.info("Video processing worker starting up...")
        await start_video_worker()
    finally:
        logger.info("Worker stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by keyboard interrupt")
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)