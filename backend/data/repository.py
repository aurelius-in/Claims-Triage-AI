"""
Repository pattern implementations for the Claims Triage AI platform.
"""

import logging
from typing import List, Optional, Dict, Any, TypeVar, Generic
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta

from .models import (
    User, Team, TeamMember, Case, Document, TriageResult, 
    AuditLog, SystemMetrics, CaseStatus, CasePriority, CaseType, UserRole
)
from .schemas import (
    UserCreate, UserUpdate, TeamCreate, TeamUpdate, 
    CaseCreate, CaseUpdate, DocumentCreate, DocumentUpdate,
    TriageResultCreate, AuditLogCreate
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, model: type[T]):
        self.model = model
    
    async def create(self, session: AsyncSession, **kwargs) -> T:
        """Create a new record."""
        instance = self.model(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance
    
    async def get_by_id(self, session: AsyncSession, id: str) -> Optional[T]:
        """Get record by ID."""
        result = await session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination."""
        result = await session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def update(self, session: AsyncSession, id: str, **kwargs) -> Optional[T]:
        """Update a record."""
        result = await session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
            .returning(self.model)
        )
        await session.commit()
        return result.scalar_one_or_none()
    
    async def delete(self, session: AsyncSession, id: str) -> bool:
        """Delete a record."""
        result = await session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await session.commit()
        return result.rowcount > 0
    
    async def count(self, session: AsyncSession) -> int:
        """Count total records."""
        result = await session.execute(select(func.count(self.model.id)))
        return result.scalar()


class UserRepository(BaseRepository[User]):
    """User repository with user-specific operations."""
    
    def __init__(self):
        super().__init__(User)
    
    async def get_by_username(self, session: AsyncSession, username: str) -> Optional[User]:
        """Get user by username."""
        result = await session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_active_users(self, session: AsyncSession) -> List[User]:
        """Get all active users."""
        result = await session.execute(
            select(User).where(User.is_active == True)
        )
        return result.scalars().all()
    
    async def get_users_by_role(self, session: AsyncSession, role: UserRole) -> List[User]:
        """Get users by role."""
        result = await session.execute(
            select(User).where(User.role == role)
        )
        return result.scalars().all()


class TeamRepository(BaseRepository[Team]):
    """Team repository with team-specific operations."""
    
    def __init__(self):
        super().__init__(Team)
    
    async def get_by_name(self, session: AsyncSession, name: str) -> Optional[Team]:
        """Get team by name."""
        result = await session.execute(
            select(Team).where(Team.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_active_teams(self, session: AsyncSession) -> List[Team]:
        """Get all active teams."""
        result = await session.execute(
            select(Team).where(Team.is_active == True)
        )
        return result.scalars().all()
    
    async def get_team_with_members(self, session: AsyncSession, team_id: UUID) -> Optional[Team]:
        """Get team with members loaded."""
        result = await session.execute(
            select(Team)
            .options(selectinload(Team.members))
            .where(Team.id == team_id)
        )
        return result.scalar_one_or_none()


class CaseRepository(BaseRepository[Case]):
    """Case repository with case-specific operations."""
    
    def __init__(self):
        super().__init__(Case)
    
    async def get_by_case_number(self, session: AsyncSession, case_number: str) -> Optional[Case]:
        """Get case by case number."""
        result = await session.execute(
            select(Case).where(Case.case_number == case_number)
        )
        return result.scalar_one_or_none()
    
    async def get_cases_by_status(self, session: AsyncSession, status: CaseStatus) -> List[Case]:
        """Get cases by status."""
        result = await session.execute(
            select(Case).where(Case.status == status)
        )
        return result.scalars().all()
    
    async def get_cases_by_priority(self, session: AsyncSession, priority: CasePriority) -> List[Case]:
        """Get cases by priority."""
        result = await session.execute(
            select(Case).where(Case.priority == priority)
        )
        return result.scalars().all()
    
    async def get_cases_by_type(self, session: AsyncSession, case_type: CaseType) -> List[Case]:
        """Get cases by type."""
        result = await session.execute(
            select(Case).where(Case.case_type == case_type)
        )
        return result.scalars().all()
    
    async def get_cases_by_assigned_user(self, session: AsyncSession, user_id: str) -> List[Case]:
        """Get cases assigned to a user."""
        result = await session.execute(
            select(Case).where(Case.assigned_user_id == user_id)
        )
        return result.scalars().all()
    
    async def get_cases_by_team(self, session: AsyncSession, team_id: str) -> List[Case]:
        """Get cases assigned to a team."""
        result = await session.execute(
            select(Case).where(Case.team_id == team_id)
        )
        return result.scalars().all()
    
    async def get_pending_cases(self, session: AsyncSession) -> List[Case]:
        """Get all pending cases."""
        result = await session.execute(
            select(Case).where(Case.status == CaseStatus.PENDING)
        )
        return result.scalars().all()
    
    async def get_urgent_cases(self, session: AsyncSession) -> List[Case]:
        """Get urgent and critical priority cases."""
        result = await session.execute(
            select(Case).where(
                or_(
                    Case.priority == CasePriority.URGENT,
                    Case.priority == CasePriority.CRITICAL
                )
            )
        )
        return result.scalars().all()
    
    async def get_case_with_details(self, session: AsyncSession, case_id: str) -> Optional[Case]:
        """Get case with all related data loaded."""
        result = await session.execute(
            select(Case)
            .options(
                selectinload(Case.documents),
                selectinload(Case.triage_results),
                selectinload(Case.assigned_user),
                selectinload(Case.team)
            )
            .where(Case.id == case_id)
        )
        return result.scalar_one_or_none()
    
    async def get_cases_analytics(self, session: AsyncSession) -> Dict[str, Any]:
        """Get analytics data for cases."""
        # Total cases
        total_result = await session.execute(select(func.count(Case.id)))
        total_cases = total_result.scalar()
        
        # Cases by status
        status_result = await session.execute(
            select(Case.status, func.count(Case.id))
            .group_by(Case.status)
        )
        cases_by_status = dict(status_result.all())
        
        # Cases by priority
        priority_result = await session.execute(
            select(Case.priority, func.count(Case.id))
            .group_by(Case.priority)
        )
        cases_by_priority = dict(priority_result.all())
        
        # Cases by type
        type_result = await session.execute(
            select(Case.case_type, func.count(Case.id))
            .group_by(Case.case_type)
        )
        cases_by_type = dict(type_result.all())
        
        return {
            "total_cases": total_cases,
            "cases_by_status": cases_by_status,
            "cases_by_priority": cases_by_priority,
            "cases_by_type": cases_by_type
        }


class DocumentRepository(BaseRepository[Document]):
    """Document repository with document-specific operations."""
    
    def __init__(self):
        super().__init__(Document)
    
    async def get_by_case(self, session: AsyncSession, case_id: str) -> List[Document]:
        """Get all documents for a case."""
        result = await session.execute(
            select(Document).where(Document.case_id == case_id)
        )
        return result.scalars().all()
    
    async def get_processed_documents(self, session: AsyncSession) -> List[Document]:
        """Get all processed documents."""
        result = await session.execute(
            select(Document).where(Document.is_processed == True)
        )
        return result.scalars().all()
    
    async def get_pending_documents(self, session: AsyncSession) -> List[Document]:
        """Get all pending documents for processing."""
        result = await session.execute(
            select(Document).where(Document.is_processed == False)
        )
        return result.scalars().all()


class TriageResultRepository(BaseRepository[TriageResult]):
    """Triage result repository with triage-specific operations."""
    
    def __init__(self):
        super().__init__(TriageResult)
    
    async def get_by_case(self, session: AsyncSession, case_id: str) -> List[TriageResult]:
        """Get all triage results for a case."""
        result = await session.execute(
            select(TriageResult).where(TriageResult.case_id == case_id)
        )
        return result.scalars().all()
    
    async def get_latest_by_case(self, session: AsyncSession, case_id: str) -> Optional[TriageResult]:
        """Get the latest triage result for a case."""
        result = await session.execute(
            select(TriageResult)
            .where(TriageResult.case_id == case_id)
            .order_by(TriageResult.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_high_confidence_results(self, session: AsyncSession, threshold: float = 0.8) -> List[TriageResult]:
        """Get triage results with high confidence scores."""
        result = await session.execute(
            select(TriageResult).where(TriageResult.confidence_score >= threshold)
        )
        return result.scalars().all()


class AuditRepository(BaseRepository[AuditLog]):
    """Audit repository with audit-specific operations."""
    
    def __init__(self):
        super().__init__(AuditLog)
    
    async def get_by_user(self, session: AsyncSession, user_id: str) -> List[AuditLog]:
        """Get audit logs for a user."""
        result = await session.execute(
            select(AuditLog).where(AuditLog.user_id == user_id)
        )
        return result.scalars().all()
    
    async def get_by_case(self, session: AsyncSession, case_id: str) -> List[AuditLog]:
        """Get audit logs for a case."""
        result = await session.execute(
            select(AuditLog).where(AuditLog.case_id == case_id)
        )
        return result.scalars().all()
    
    async def get_recent_activity(self, session: AsyncSession, days: int = 7) -> List[AuditLog]:
        """Get recent audit activity."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = await session.execute(
            select(AuditLog)
            .where(AuditLog.created_at >= cutoff_date)
            .order_by(AuditLog.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_by_action(self, session: AsyncSession, action: str) -> List[AuditLog]:
        """Get audit logs by action type."""
        result = await session.execute(
            select(AuditLog).where(AuditLog.action == action)
        )
        return result.scalars().all()


# Repository instances
user_repository = UserRepository()
team_repository = TeamRepository()
case_repository = CaseRepository()
document_repository = DocumentRepository()
triage_result_repository = TriageResultRepository()
audit_repository = AuditRepository()
