import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Get database settings from config
DB_USER = settings.DB_USER if hasattr(settings, "DB_USER") else os.getenv("DB_USER", "postgres")
DB_PASSWORD = settings.DB_PASSWORD if hasattr(settings, "DB_PASSWORD") else os.getenv("DB_PASSWORD", "postgres")
DB_HOST = settings.DB_HOST if hasattr(settings, "DB_HOST") else os.getenv("DB_HOST", "localhost")
DB_PORT = settings.DB_PORT if hasattr(settings, "DB_PORT") else os.getenv("DB_PORT", "5432")
DB_NAME = settings.DB_NAME if hasattr(settings, "DB_NAME") else os.getenv("DB_NAME", "reddit_comments")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool,  # Using NullPool for FastAPI compatibility
)

# Create a session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Context manager to get a database session
@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager to get and automatically close a database session.

    Example:
        async with get_db() as session:
            # Use session here

    Returns:
        AsyncGenerator yielding an AsyncSession
    """
    session = async_session_maker()
    try:
        yield session
    finally:
        await session.close()


async def close_db_connections():
    """Close all database connections."""
    await engine.dispose()
