"""
Database configuration and connection management.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from .models import Base
from ..core.config import get_settings

settings = get_settings()

# Database URL
DATABASE_URL = settings.database_url

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections every hour
    pool_size=10,        # Connection pool size
    max_overflow=20,     # Additional connections when pool is full
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# For testing - in-memory SQLite
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get test database session."""
    async with TestSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Drop all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def init_db():
    """Initialize database with tables and seed data."""
    await create_tables()
    
    # Import here to avoid circular imports
    from .repository import TeamRepository, UserRepository
    
    async with AsyncSessionLocal() as session:
        # Check if we already have teams
        team_repo = TeamRepository(session)
        existing_teams = await team_repo.list_teams()
        
        if not existing_teams:
            # Create default teams
            default_teams = [
                {
                    "name": "Auto Insurance Team",
                    "description": "Handles auto insurance claims",
                    "domain": "insurance",
                    "capacity": 50,
                    "sla_target_hours": 24
                },
                {
                    "name": "Health Insurance Team", 
                    "description": "Handles health insurance claims",
                    "domain": "insurance",
                    "capacity": 40,
                    "sla_target_hours": 48
                },
                {
                    "name": "Fraud Review Team",
                    "description": "Investigates potential fraud cases",
                    "domain": "insurance",
                    "capacity": 20,
                    "sla_target_hours": 72
                },
                {
                    "name": "Legal Team",
                    "description": "Handles legal cases and disputes",
                    "domain": "legal",
                    "capacity": 15,
                    "sla_target_hours": 96
                },
                {
                    "name": "Healthcare Team",
                    "description": "Handles healthcare prior authorizations",
                    "domain": "healthcare",
                    "capacity": 30,
                    "sla_target_hours": 24
                }
            ]
            
            for team_data in default_teams:
                await team_repo.create_team(team_data)
            
            # Create default admin user
            user_repo = UserRepository(session)
            admin_user = {
                "username": "admin",
                "email": "admin@claims-triage-ai.com",
                "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK8i",  # "admin123"
                "full_name": "System Administrator",
                "role": "admin"
            }
            await user_repo.create_user(admin_user)
            
            await session.commit()


async def close_db():
    """Close database connections."""
    await engine.dispose()
