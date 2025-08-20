"""
Tests for database implementation.
"""

import pytest
import asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from data.database import init_db, get_db_session, close_db
from data.models import User, Case, CaseStatus, CasePriority, CaseType, UserRole
from data.repository import user_repository, case_repository
from core.auth import get_password_hash


@pytest.fixture
async def db_session():
    """Create a database session for testing."""
    await init_db()
    async with get_db_session() as session:
        yield session
    await close_db()


@pytest.mark.asyncio
async def test_database_connection(db_session: AsyncSession):
    """Test database connection and basic operations."""
    # Test that we can execute a simple query
    result = await db_session.execute("SELECT 1")
    assert result.scalar() == 1


@pytest.mark.asyncio
async def test_user_creation(db_session: AsyncSession):
    """Test user creation and retrieval."""
    # Create a test user
    test_user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass"),
        full_name="Test User",
        role=UserRole.ANALYST,
        is_active=True
    )
    
    db_session.add(test_user)
    await db_session.commit()
    await db_session.refresh(test_user)
    
    # Verify user was created
    assert test_user.id is not None
    assert test_user.username == "testuser"
    assert test_user.email == "test@example.com"
    assert test_user.role == UserRole.ANALYST


@pytest.mark.asyncio
async def test_case_creation(db_session: AsyncSession):
    """Test case creation and retrieval."""
    # Create a test user first
    test_user = User(
        username="caseuser",
        email="case@example.com",
        hashed_password=get_password_hash("testpass"),
        full_name="Case User",
        role=UserRole.ANALYST,
        is_active=True
    )
    db_session.add(test_user)
    await db_session.commit()
    await db_session.refresh(test_user)
    
    # Create a test case
    test_case = Case(
        case_number="TEST-001",
        title="Test Case",
        description="A test case for testing",
        case_type=CaseType.AUTO_CLAIM,
        customer_name="John Doe",
        customer_email="john@example.com",
        claim_amount=5000.00,
        priority=CasePriority.NORMAL,
        assigned_user_id=test_user.id
    )
    
    db_session.add(test_case)
    await db_session.commit()
    await db_session.refresh(test_case)
    
    # Verify case was created
    assert test_case.id is not None
    assert test_case.case_number == "TEST-001"
    assert test_case.title == "Test Case"
    assert test_case.case_type == CaseType.AUTO_CLAIM
    assert test_case.priority == CasePriority.NORMAL
    assert test_case.status == CaseStatus.PENDING  # Default status


@pytest.mark.asyncio
async def test_user_repository(db_session: AsyncSession):
    """Test user repository operations."""
    # Create a test user using repository
    user_data = {
        "username": "repouser",
        "email": "repo@example.com",
        "hashed_password": get_password_hash("testpass"),
        "full_name": "Repo User",
        "role": UserRole.REVIEWER,
        "is_active": True
    }
    
    user = await user_repository.create(db_session, **user_data)
    assert user.id is not None
    assert user.username == "repouser"
    
    # Test get by username
    retrieved_user = await user_repository.get_by_username(db_session, "repouser")
    assert retrieved_user is not None
    assert retrieved_user.email == "repo@example.com"
    
    # Test get by email
    retrieved_user = await user_repository.get_by_email(db_session, "repo@example.com")
    assert retrieved_user is not None
    assert retrieved_user.username == "repouser"


@pytest.mark.asyncio
async def test_case_repository(db_session: AsyncSession):
    """Test case repository operations."""
    # Create a test user first
    test_user = User(
        username="caserepouser",
        email="caserepo@example.com",
        hashed_password=get_password_hash("testpass"),
        full_name="Case Repo User",
        role=UserRole.ANALYST,
        is_active=True
    )
    db_session.add(test_user)
    await db_session.commit()
    await db_session.refresh(test_user)
    
    # Create test cases using repository
    case_data = {
        "case_number": "REPO-001",
        "title": "Repository Test Case",
        "description": "Testing case repository",
        "case_type": CaseType.HOME_CLAIM,
        "customer_name": "Jane Smith",
        "customer_email": "jane@example.com",
        "claim_amount": 15000.00,
        "priority": CasePriority.HIGH,
        "assigned_user_id": test_user.id
    }
    
    case = await case_repository.create(db_session, **case_data)
    assert case.id is not None
    assert case.case_number == "REPO-001"
    
    # Test get by case number
    retrieved_case = await case_repository.get_by_case_number(db_session, "REPO-001")
    assert retrieved_case is not None
    assert retrieved_case.title == "Repository Test Case"
    
    # Test get cases by status
    pending_cases = await case_repository.get_cases_by_status(db_session, CaseStatus.PENDING)
    assert len(pending_cases) >= 1
    assert any(c.case_number == "REPO-001" for c in pending_cases)
    
    # Test get cases by priority
    high_priority_cases = await case_repository.get_cases_by_priority(db_session, CasePriority.HIGH)
    assert len(high_priority_cases) >= 1
    assert any(c.case_number == "REPO-001" for c in high_priority_cases)


@pytest.mark.asyncio
async def test_database_health_check():
    """Test database health check functionality."""
    await init_db()
    
    from data.database import health_check
    health_status = await health_check()
    
    assert health_status["status"] == "healthy"
    assert health_status["database"] == "postgresql"
    
    await close_db()
