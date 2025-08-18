"""
Test database layer functionality.
"""
import pytest
import asyncio
from uuid import uuid4
from datetime import datetime

from backend.data.database import get_test_db, create_tables, drop_tables
from backend.data.repository import CaseRepository, UserRepository, TeamRepository
from backend.data.schemas import CaseCreate, UserCreate, TeamCreate
from backend.data.models import CaseType, UrgencyLevel, RiskLevel, UserRole


@pytest.fixture
async def db_session():
    """Create a test database session."""
    async for session in get_test_db():
        yield session


@pytest.fixture
async def setup_db():
    """Setup test database."""
    await create_tables()
    yield
    await drop_tables()


@pytest.mark.asyncio
async def test_create_case(db_session, setup_db):
    """Test case creation."""
    case_repo = CaseRepository(db_session)
    
    case_data = CaseCreate(
        external_id="TEST-001",
        case_type=CaseType.AUTO_INSURANCE,
        title="Test Auto Claim",
        description="Test auto insurance claim",
        urgency_level=UrgencyLevel.MEDIUM,
        risk_level=RiskLevel.LOW,
        risk_score=0.3
    )
    
    case = await case_repo.create_case(case_data)
    await db_session.commit()
    
    assert case.id is not None
    assert case.external_id == "TEST-001"
    assert case.case_type == CaseType.AUTO_INSURANCE
    assert case.title == "Test Auto Claim"


@pytest.mark.asyncio
async def test_create_user(db_session, setup_db):
    """Test user creation."""
    user_repo = UserRepository(db_session)
    
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        role=UserRole.AGENT
    )
    
    user = await user_repo.create_user(user_data)
    await db_session.commit()
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.role == UserRole.AGENT


@pytest.mark.asyncio
async def test_create_team(db_session, setup_db):
    """Test team creation."""
    team_repo = TeamRepository(db_session)
    
    team_data = TeamCreate(
        name="Test Team",
        description="Test team description",
        domain="insurance",
        capacity=10,
        sla_target_hours=24
    )
    
    team = await team_repo.create_team(team_data)
    await db_session.commit()
    
    assert team.id is not None
    assert team.name == "Test Team"
    assert team.domain == "insurance"
    assert team.capacity == 10


@pytest.mark.asyncio
async def test_list_cases(db_session, setup_db):
    """Test case listing."""
    case_repo = CaseRepository(db_session)
    
    # Create multiple cases
    for i in range(3):
        case_data = CaseCreate(
            external_id=f"TEST-{i:03d}",
            case_type=CaseType.AUTO_INSURANCE,
            title=f"Test Case {i}",
            description=f"Test case {i} description",
            urgency_level=UrgencyLevel.MEDIUM,
            risk_level=RiskLevel.LOW,
            risk_score=0.3
        )
        await case_repo.create_case(case_data)
    
    await db_session.commit()
    
    # List cases
    cases = await case_repo.list_cases(limit=10)
    assert len(cases) == 3
    assert cases[0].external_id == "TEST-002"  # Most recent first


@pytest.mark.asyncio
async def test_case_filtering(db_session, setup_db):
    """Test case filtering."""
    case_repo = CaseRepository(db_session)
    
    # Create cases with different types
    case_data_1 = CaseCreate(
        external_id="AUTO-001",
        case_type=CaseType.AUTO_INSURANCE,
        title="Auto Claim",
        description="Auto insurance claim",
        urgency_level=UrgencyLevel.MEDIUM,
        risk_level=RiskLevel.LOW,
        risk_score=0.3
    )
    
    case_data_2 = CaseCreate(
        external_id="HEALTH-001",
        case_type=CaseType.HEALTH_INSURANCE,
        title="Health Claim",
        description="Health insurance claim",
        urgency_level=UrgencyLevel.HIGH,
        risk_level=RiskLevel.MEDIUM,
        risk_score=0.6
    )
    
    await case_repo.create_case(case_data_1)
    await case_repo.create_case(case_data_2)
    await db_session.commit()
    
    # Filter by case type
    auto_cases = await case_repo.list_cases(case_type=CaseType.AUTO_INSURANCE)
    assert len(auto_cases) == 1
    assert auto_cases[0].case_type == CaseType.AUTO_INSURANCE
    
    # Filter by urgency level
    high_urgency_cases = await case_repo.list_cases(urgency_level=UrgencyLevel.HIGH)
    assert len(high_urgency_cases) == 1
    assert high_urgency_cases[0].urgency_level == UrgencyLevel.HIGH
