"""
Pydantic schemas for the Claims Triage AI platform API.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import UUID

from .models import CaseStatus, CasePriority, CaseType, UserRole


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


# User schemas
class UserBase(BaseSchema):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r"^[^@]+@[^@]+\.[^@]+$")
    full_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.VIEWER


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseSchema):
    """Schema for updating a user."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, regex=r"^[^@]+@[^@]+\.[^@]+$")
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# Team schemas
class TeamBase(BaseSchema):
    """Base team schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class TeamCreate(TeamBase):
    """Schema for creating a team."""
    manager_id: Optional[UUID] = None


class TeamUpdate(BaseSchema):
    """Schema for updating a team."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    manager_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class TeamResponse(TeamBase):
    """Schema for team response."""
    id: UUID
    manager_id: Optional[UUID] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# Case schemas
class CaseBase(BaseSchema):
    """Base case schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    case_type: CaseType
    customer_name: str = Field(..., min_length=1, max_length=100)
    customer_email: Optional[str] = Field(None, regex=r"^[^@]+@[^@]+\.[^@]+$")
    customer_phone: Optional[str] = Field(None, max_length=20)
    claim_amount: Optional[float] = Field(None, ge=0)


class CaseCreate(CaseBase):
    """Schema for creating a case."""
    priority: CasePriority = CasePriority.NORMAL
    assigned_user_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    due_date: Optional[datetime] = None


class CaseUpdate(BaseSchema):
    """Schema for updating a case."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[CaseStatus] = None
    priority: Optional[CasePriority] = None
    customer_name: Optional[str] = Field(None, min_length=1, max_length=100)
    customer_email: Optional[str] = Field(None, regex=r"^[^@]+@[^@]+\.[^@]+$")
    customer_phone: Optional[str] = Field(None, max_length=20)
    claim_amount: Optional[float] = Field(None, ge=0)
    approved_amount: Optional[float] = Field(None, ge=0)
    assigned_user_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    due_date: Optional[datetime] = None


class CaseResponse(CaseBase):
    """Schema for case response."""
    id: UUID
    case_number: str
    status: CaseStatus
    priority: CasePriority
    approved_amount: Optional[float] = None
    assigned_user_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    ai_confidence_score: Optional[float] = None
    ai_risk_score: Optional[float] = None
    ai_recommendation: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    closed_at: Optional[datetime] = None


# Document schemas
class DocumentBase(BaseSchema):
    """Base document schema."""
    original_filename: str = Field(..., min_length=1, max_length=255)
    document_type: Optional[str] = Field(None, max_length=50)


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    case_id: UUID
    file_path: str
    file_size: int
    mime_type: str


class DocumentUpdate(BaseSchema):
    """Schema for updating a document."""
    document_type: Optional[str] = Field(None, max_length=50)
    is_processed: Optional[bool] = None
    processing_status: Optional[str] = None
    extracted_text: Optional[str] = None


class DocumentResponse(DocumentBase):
    """Schema for document response."""
    id: UUID
    case_id: UUID
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    is_processed: bool
    processing_status: str
    uploaded_at: datetime
    processed_at: Optional[datetime] = None


# Triage Result schemas
class TriageResultBase(BaseSchema):
    """Base triage result schema."""
    classifier_result: Optional[Dict[str, Any]] = None
    risk_scorer_result: Optional[Dict[str, Any]] = None
    router_result: Optional[Dict[str, Any]] = None
    decision_support_result: Optional[Dict[str, Any]] = None
    compliance_result: Optional[Dict[str, Any]] = None


class TriageResultCreate(TriageResultBase):
    """Schema for creating a triage result."""
    case_id: UUID
    final_priority: Optional[CasePriority] = None
    final_status: Optional[CaseStatus] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    processing_time: Optional[float] = Field(None, ge=0)


class TriageResultResponse(TriageResultBase):
    """Schema for triage result response."""
    id: UUID
    case_id: UUID
    final_priority: Optional[CasePriority] = None
    final_status: Optional[CaseStatus] = None
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None
    created_at: datetime


# Audit Log schemas
class AuditLogBase(BaseSchema):
    """Base audit log schema."""
    action: str = Field(..., min_length=1, max_length=100)
    resource_type: str = Field(..., min_length=1, max_length=50)
    resource_id: Optional[str] = Field(None, max_length=50)
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)


class AuditLogCreate(AuditLogBase):
    """Schema for creating an audit log."""
    user_id: Optional[UUID] = None
    case_id: Optional[UUID] = None


class AuditLogResponse(AuditLogBase):
    """Schema for audit log response."""
    id: UUID
    user_id: Optional[UUID] = None
    case_id: Optional[UUID] = None
    created_at: datetime


# Authentication schemas
class LoginRequest(BaseSchema):
    """Schema for login request."""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseSchema):
    """Schema for login response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseSchema):
    """Schema for token data."""
    username: Optional[str] = None
    user_id: Optional[UUID] = None
    role: Optional[UserRole] = None


# Analytics schemas
class AnalyticsMetrics(BaseSchema):
    """Schema for analytics metrics."""
    total_cases: int
    pending_cases: int
    completed_cases: int
    average_processing_time: float
    sla_compliance_rate: float
    accuracy_rate: float


class AnalyticsResponse(BaseSchema):
    """Schema for analytics response."""
    metrics: AnalyticsMetrics
    cases_by_status: Dict[str, int]
    cases_by_priority: Dict[str, int]
    cases_by_type: Dict[str, int]
    recent_activity: List[Dict[str, Any]]


# API Response schemas
class PaginatedResponse(BaseSchema):
    """Schema for paginated responses."""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


class ErrorResponse(BaseSchema):
    """Schema for error responses."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseSchema):
    """Schema for success responses."""
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
