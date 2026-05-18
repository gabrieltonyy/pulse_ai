"""
Database configuration and session management for Pulse AI.
Uses SQLAlchemy 2.x with asyncpg for async PostgreSQL operations.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool

from app.config import settings

# Base class for all models
Base = declarative_base()

# Global engine instance
engine: AsyncEngine | None = None
async_session_maker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """
    Create and configure the async database engine.
    
    Returns:
        AsyncEngine: Configured SQLAlchemy async engine
    """
    global engine
    
    if engine is None:
        engine_kwargs = {
            "echo": settings.debug,
            "pool_pre_ping": True,  # Verify connections before using
        }

        if settings.is_production:
            engine_kwargs.update(
                {
                    "poolclass": QueuePool,
                    "pool_size": settings.database_pool_size,
                    "max_overflow": settings.database_max_overflow,
                    "pool_timeout": settings.database_pool_timeout,
                    "pool_recycle": settings.database_pool_recycle,
                }
            )
        else:
            # NullPool is intentional for dev/test so connections are not reused.
            engine_kwargs["poolclass"] = NullPool

        engine = create_async_engine(settings.database_url, **engine_kwargs)
    
    return engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """
    Get or create the async session maker.
    
    Returns:
        async_sessionmaker: Session factory for creating database sessions
    """
    global async_session_maker
    
    if async_session_maker is None:
        async_session_maker = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    
    return async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes to get database sessions.
    
    Yields:
        AsyncSession: Database session
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database connection and create tables if needed.
    Called during application startup.
    """
    engine = get_engine()
    
    # Import all models to ensure they're registered with Base
    from app.models import saved_events, search_history, api_cache, outbound_clicks
    
    # Create tables (in production, use Alembic migrations instead)
    if settings.debug:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.
    Called during application shutdown.
    """
    global engine, async_session_maker
    
    if engine is not None:
        await engine.dispose()
        engine = None
        async_session_maker = None


async def check_db_connection() -> bool:
    """
    Check if database connection is healthy.
    
    Returns:
        bool: True if connection is healthy, False otherwise
    """
    try:
        from sqlalchemy import text
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

# Made with Bob
