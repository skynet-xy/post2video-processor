from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as redis

from app.core.config import settings

# Create Redis connection URL
REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"

# Create Redis pool
redis_pool = redis.ConnectionPool.from_url(
    REDIS_URL,
    password=settings.REDIS_PASSWORD or None,
    decode_responses=True,
)

@asynccontextmanager
async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """
    Get a Redis client instance.

    Usage:
        async with get_redis() as redis_client:
            await redis_client.set("key", "value")

    Returns:
        AsyncGenerator yielding a Redis client
    """
    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        await client.aclose()

import redis as redis_sync

def get_sync_redis():
    """Get a synchronous Redis client instance."""
    return redis_sync.Redis(
        host=settings.REDIS_HOST,
        port=int(settings.REDIS_PORT),
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD or None,
        decode_responses=True
    )

async def close_redis_connections():
    """Close all Redis connections."""
    await redis_pool.disconnect()