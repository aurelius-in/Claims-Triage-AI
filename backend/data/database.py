"""
Database connection and session management for the Claims Triage AI platform.
"""

import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager

from ..core.config import settings

logger = logging.getLogger(__name__)

# Create declarative base for models
Base = declarative_base()

# Import models to register them with Base metadata
from . import models

# Database engine and session factory
engine = None
AsyncSessionLocal = None


async def init_db() -> None:
    """Initialize database connection and create tables."""
    global engine, AsyncSessionLocal
    
    try:
        # Create async engine
        engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            poolclass=NullPool,  # Disable connection pooling for async
            future=True
        )
        
        # Create session factory
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


async def close_db() -> None:
    """Close database connections."""
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("Database connections closed")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    if not AsyncSessionLocal:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database sessions."""
    if not AsyncSessionLocal:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            await session.close()


async def health_check() -> dict:
    """Check database health."""
    try:
        if not engine:
            return {"status": "unhealthy", "error": "Database not initialized"}
        
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        
        return {"status": "healthy", "database": "postgresql"}
        
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}
