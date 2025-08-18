"""
Repository pattern implementation for database operations.
"""
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime, timedelta
import json
import hashlib

from .models import (
    Case, User, Team, Document, AuditLog, TriageResult, AnalyticsSnapshot,
    CaseType, UrgencyLevel, RiskLevel, CaseStatus, UserRole
)
from .schemas import (
    CaseCreate, CaseUpdate, UserCreate, UserUpdate, TeamCreate, TeamUpdate,
    AuditLogCreate, DocumentCreate
)


class BaseRepository:
    """Base repository with common CRUD operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def commit(self):
        """Commit the current transaction."""
        await self.session.commit()
    
    async def rollback(self):
        """Rollback the current transaction."""
        await self.session.rollback()


class CaseRepository(BaseRepository):
    """Repository for Case operations."""
    
    async def create_case(self, case_data: CaseCreate) -> Case:
        """Create a new case."""
        case = Case(**case_data.dict())
        self.session.add(case)
        await self.session.flush()
        await self.session.refresh(case)
        return case
    
    async def get_case(self, case_id: UUID) -> Optional[Case]:
        """Get a case by ID with all relationships."""
        result = await self.session.execute(
            select(Case)
            .options(
                selectinload(Case.assigned_team),
                selectinload(Case.assigned_user),
                selectinload(Case.documents),
                selectinload(Case.triage_results),
                selectinload(Case.audit_logs)
            )
            .where(Case.id == case_id)
        )
        return result.scalar_one_or_none()
    
    async def get_case_by_external_id(self, external_id: str) -> Optional[Case]:
        """Get a case by external ID."""
        result = await self.session.execute(
            select(Case).where(Case.external_id == external_id)
        )
        return result.scalar_one_or_none()
    
    async def list_cases(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[CaseStatus] = None,
        case_type: Optional[CaseType] = None,
        urgency_level: Optional[UrgencyLevel] = None,
        risk_level: Optional[RiskLevel] = None,
        team_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None
    ) -> List[Case]:
        """List cases with filtering and pagination."""
        query = select(Case).options(
            selectinload(Case.assigned_team),
            selectinload(Case.assigned_user)
        )
        
        # Apply filters
        conditions = []
        if status:
            conditions.append(Case.status == status)
        if case_type:
            conditions.append(Case.case_type == case_type)
        if urgency_level:
            conditions.append(Case.urgency_level == urgency_level)
        if risk_level:
            conditions.append(Case.risk_level == risk_level)
        if team_id:
            conditions.append(Case.assigned_team_id == team_id)
        if user_id:
            conditions.append(Case.assigned_user_id == user_id)
        if created_after:
            conditions.append(Case.created_at >= created_after)
        if created_before:
            conditions.append(Case.created_at <= created_before)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Apply pagination and ordering
        query = query.order_by(desc(Case.created_at)).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update_case(self, case_id: UUID, case_data: CaseUpdate) -> Optional[Case]:
        """Update a case."""
        update_data = case_data.dict(exclude_unset=True)
        if not update_data:
            return await self.get_case(case_id)
        
        await self.session.execute(
            update(Case)
            .where(Case.id == case_id)
            .values(**update_data, updated_at=datetime.utcnow())
        )
        await self.session.flush()
        return await self.get_case(case_id)
    
    async def delete_case(self, case_id: UUID) -> bool:
        """Delete a case."""
        result = await self.session.execute(
            delete(Case).where(Case.id == case_id)
        )
        return result.rowcount > 0
    
    async def get_case_count(self, status: Optional[CaseStatus] = None) -> int:
        """Get total case count with optional status filter."""
        query = select(func.count(Case.id))
        if status:
            query = query.where(Case.status == status)
        result = await self.session.execute(query)
        return result.scalar()
    
    async def get_cases_by_team(self, team_id: UUID) -> List[Case]:
        """Get all cases assigned to a team."""
        result = await self.session.execute(
            select(Case)
            .where(Case.assigned_team_id == team_id)
            .order_by(desc(Case.created_at))
        )
        return result.scalars().all()
    
    async def get_overdue_cases(self) -> List[Case]:
        """Get cases that are overdue based on SLA deadline."""
        result = await self.session.execute(
            select(Case)
            .where(
                and_(
                    Case.sla_deadline < datetime.utcnow(),
                    Case.status.in_([CaseStatus.PENDING, CaseStatus.IN_PROGRESS])
                )
            )
            .order_by(Case.sla_deadline)
        )
        return result.scalars().all()


class UserRepository(BaseRepository):
    """Repository for User operations."""
    
    async def create_user(self, user_data: Union[UserCreate, Dict[str, Any]]) -> User:
        """Create a new user."""
        if isinstance(user_data, dict):
            user = User(**user_data)
        else:
            user = User(**user_data.dict())
        
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
    
    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Get a user by ID."""
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.team))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        team_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """List users with filtering and pagination."""
        query = select(User).options(selectinload(User.team))
        
        conditions = []
        if role:
            conditions.append(User.role == role)
        if team_id:
            conditions.append(User.team_id == team_id)
        if is_active is not None:
            conditions.append(User.is_active == is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(asc(User.username)).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        """Update a user."""
        update_data = user_data.dict(exclude_unset=True)
        if not update_data:
            return await self.get_user(user_id)
        
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data, updated_at=datetime.utcnow())
        )
        await self.session.flush()
        return await self.get_user(user_id)
    
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user."""
        result = await self.session.execute(
            delete(User).where(User.id == user_id)
        )
        return result.rowcount > 0
    
    async def update_last_login(self, user_id: UUID) -> None:
        """Update user's last login timestamp."""
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.utcnow())
        )


class TeamRepository(BaseRepository):
    """Repository for Team operations."""
    
    async def create_team(self, team_data: Union[TeamCreate, Dict[str, Any]]) -> Team:
        """Create a new team."""
        if isinstance(team_data, dict):
            team = Team(**team_data)
        else:
            team = Team(**team_data.dict())
        
        self.session.add(team)
        await self.session.flush()
        await self.session.refresh(team)
        return team
    
    async def get_team(self, team_id: UUID) -> Optional[Team]:
        """Get a team by ID."""
        result = await self.session.execute(
            select(Team)
            .options(
                selectinload(Team.users),
                selectinload(Team.cases)
            )
            .where(Team.id == team_id)
        )
        return result.scalar_one_or_none()
    
    async def list_teams(
        self,
        skip: int = 0,
        limit: int = 100,
        domain: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Team]:
        """List teams with filtering and pagination."""
        query = select(Team)
        
        conditions = []
        if domain:
            conditions.append(Team.domain == domain)
        if is_active is not None:
            conditions.append(Team.is_active == is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(asc(Team.name)).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update_team(self, team_id: UUID, team_data: TeamUpdate) -> Optional[Team]:
        """Update a team."""
        update_data = team_data.dict(exclude_unset=True)
        if not update_data:
            return await self.get_team(team_id)
        
        await self.session.execute(
            update(Team)
            .where(Team.id == team_id)
            .values(**update_data, updated_at=datetime.utcnow())
        )
        await self.session.flush()
        return await self.get_team(team_id)
    
    async def delete_team(self, team_id: UUID) -> bool:
        """Delete a team."""
        result = await self.session.execute(
            delete(Team).where(Team.id == team_id)
        )
        return result.rowcount > 0
    
    async def update_team_load(self, team_id: UUID, load_change: int) -> None:
        """Update team's current load."""
        await self.session.execute(
            update(Team)
            .where(Team.id == team_id)
            .values(current_load=Team.current_load + load_change)
        )


class DocumentRepository(BaseRepository):
    """Repository for Document operations."""
    
    async def create_document(self, document_data: DocumentCreate) -> Document:
        """Create a new document."""
        document = Document(**document_data.dict())
        self.session.add(document)
        await self.session.flush()
        await self.session.refresh(document)
        return document
    
    async def get_document(self, document_id: UUID) -> Optional[Document]:
        """Get a document by ID."""
        result = await self.session.execute(
            select(Document)
            .options(selectinload(Document.case))
            .where(Document.id == document_id)
        )
        return result.scalar_one_or_none()
    
    async def list_documents_by_case(self, case_id: UUID) -> List[Document]:
        """Get all documents for a case."""
        result = await self.session.execute(
            select(Document)
            .where(Document.case_id == case_id)
            .order_by(desc(Document.created_at))
        )
        return result.scalars().all()
    
    async def update_document_processing(
        self,
        document_id: UUID,
        is_processed: bool,
        processing_status: str,
        extracted_text: Optional[str] = None,
        extracted_metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Document]:
        """Update document processing status."""
        update_data = {
            "is_processed": is_processed,
            "processing_status": processing_status,
            "updated_at": datetime.utcnow()
        }
        
        if extracted_text is not None:
            update_data["extracted_text"] = extracted_text
        if extracted_metadata is not None:
            update_data["extracted_metadata"] = extracted_metadata
        
        await self.session.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(**update_data)
        )
        await self.session.flush()
        return await self.get_document(document_id)
    
    async def delete_document(self, document_id: UUID) -> bool:
        """Delete a document."""
        result = await self.session.execute(
            delete(Document).where(Document.id == document_id)
        )
        return result.rowcount > 0


class AuditRepository(BaseRepository):
    """Repository for AuditLog operations."""
    
    async def create_audit_log(self, audit_data: AuditLogCreate) -> AuditLog:
        """Create a new audit log entry."""
        # Calculate hash for chain integrity
        audit_dict = audit_data.dict()
        audit_dict["current_hash"] = self._calculate_hash(audit_dict)
        
        audit_log = AuditLog(**audit_dict)
        self.session.add(audit_log)
        await self.session.flush()
        await self.session.refresh(audit_log)
        return audit_log
    
    def _calculate_hash(self, audit_data: Dict[str, Any]) -> str:
        """Calculate hash for audit log entry."""
        # Create a deterministic string representation
        hash_data = {
            "action": audit_data.get("action"),
            "resource_type": audit_data.get("resource_type"),
            "resource_id": audit_data.get("resource_id"),
            "details": audit_data.get("details"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    async def list_audit_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        case_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None
    ) -> List[AuditLog]:
        """List audit logs with filtering and pagination."""
        query = select(AuditLog).options(
            selectinload(AuditLog.case),
            selectinload(AuditLog.user)
        )
        
        conditions = []
        if case_id:
            conditions.append(AuditLog.case_id == case_id)
        if user_id:
            conditions.append(AuditLog.user_id == user_id)
        if action:
            conditions.append(AuditLog.action == action)
        if resource_type:
            conditions.append(AuditLog.resource_type == resource_type)
        if created_after:
            conditions.append(AuditLog.created_at >= created_after)
        if created_before:
            conditions.append(AuditLog.created_at <= created_before)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_audit_logs_by_case(self, case_id: UUID) -> List[AuditLog]:
        """Get all audit logs for a specific case."""
        result = await self.session.execute(
            select(AuditLog)
            .options(selectinload(AuditLog.user))
            .where(AuditLog.case_id == case_id)
            .order_by(desc(AuditLog.created_at))
        )
        return result.scalars().all()


class TriageResultRepository(BaseRepository):
    """Repository for TriageResult operations."""
    
    async def create_triage_result(self, triage_data: Dict[str, Any]) -> TriageResult:
        """Create a new triage result."""
        triage_result = TriageResult(**triage_data)
        self.session.add(triage_result)
        await self.session.flush()
        await self.session.refresh(triage_result)
        return triage_result
    
    async def get_latest_triage_result(self, case_id: UUID) -> Optional[TriageResult]:
        """Get the latest triage result for a case."""
        result = await self.session.execute(
            select(TriageResult)
            .where(TriageResult.case_id == case_id)
            .order_by(desc(TriageResult.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_triage_results_by_case(self, case_id: UUID) -> List[TriageResult]:
        """Get all triage results for a case."""
        result = await self.session.execute(
            select(TriageResult)
            .where(TriageResult.case_id == case_id)
            .order_by(desc(TriageResult.created_at))
        )
        return result.scalars().all()


class AnalyticsRepository(BaseRepository):
    """Repository for AnalyticsSnapshot operations."""
    
    async def create_snapshot(self, snapshot_data: Dict[str, Any]) -> AnalyticsSnapshot:
        """Create a new analytics snapshot."""
        snapshot = AnalyticsSnapshot(**snapshot_data)
        self.session.add(snapshot)
        await self.session.flush()
        await self.session.refresh(snapshot)
        return snapshot
    
    async def get_metrics(
        self,
        metric_type: str,
        metric_name: str,
        team_id: Optional[UUID] = None,
        case_type: Optional[CaseType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        aggregation_period: str = "daily"
    ) -> List[AnalyticsSnapshot]:
        """Get metrics for a specific type and name."""
        query = select(AnalyticsSnapshot).where(
            and_(
                AnalyticsSnapshot.metric_type == metric_type,
                AnalyticsSnapshot.metric_name == metric_name,
                AnalyticsSnapshot.aggregation_period == aggregation_period
            )
        )
        
        conditions = []
        if team_id:
            conditions.append(AnalyticsSnapshot.team_id == team_id)
        if case_type:
            conditions.append(AnalyticsSnapshot.case_type == case_type)
        if start_date:
            conditions.append(AnalyticsSnapshot.snapshot_date >= start_date)
        if end_date:
            conditions.append(AnalyticsSnapshot.snapshot_date <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(asc(AnalyticsSnapshot.snapshot_date))
        
        result = await self.session.execute(query)
        return result.scalars().all()
