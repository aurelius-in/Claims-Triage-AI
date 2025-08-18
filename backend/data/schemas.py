"""
Pydantic schemas for API requests and responses.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
from uuid import UUID


class CaseType(str, Enum):
    """Case types supported by the system."""
    INSURANCE_CLAIM = "insurance_claim"
    HEALTHCARE_PRIOR_AUTH = "healthcare_prior_auth"
    BANK_DISPUTE = "bank_dispute"
    LEGAL_INTAKE = "legal_intake"
    FRAUD_REVIEW = "fraud_review"


class UrgencyLevel(str, Enum):
    """Urgency levels for cases."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(str, Enum):
    """Risk levels for cases."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class CaseStatus(str, Enum):
    """Case processing status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW_REQUIRED = "review_required"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    CLOSED = "closed"


class UserRole(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    AGENT = "agent"
    AUDITOR = "auditor"


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


# Case schemas
class CaseCreate(BaseSchema):
    """Schema for creating a new case."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    case_type: CaseType
    customer_id: Optional[str] = Field(None, max_length=100)
    amount: Optional[float] = Field(None, ge=0)
    priority: Optional[UrgencyLevel] = UrgencyLevel.MEDIUM
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    attachments: Optional[List[str]] = Field(default_factory=list)


class CaseUpdate(BaseSchema):
    """Schema for updating a case."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    status: Optional[CaseStatus] = None
    assigned_team_id: Optional[UUID] = None
    assigned_user_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None


class CaseResponse(BaseSchema):
    """Schema for case response."""
    id: UUID
    title: str
    description: str
    case_type: CaseType
    status: CaseStatus
    urgency: UrgencyLevel
    risk_level: RiskLevel
    risk_score: float
    customer_id: Optional[str]
    amount: Optional[float]
    priority: UrgencyLevel
    assigned_team_id: Optional[UUID]
    assigned_user_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    triaged_at: Optional[datetime]
    metadata: Dict[str, Any]
    attachments: List[str]


# Triage schemas
class TriageRequest(BaseSchema):
    """Schema for triage request."""
    case_id: UUID
    force_reprocess: bool = Field(default=False, description="Force reprocessing even if already triaged")


class AgentResult(BaseSchema):
    """Schema for individual agent results."""
    agent_name: str
    confidence: float = Field(..., ge=0, le=1)
    result: Dict[str, Any]
    reasoning: str
    processing_time_ms: int
    error: Optional[str] = None


class TriageResponse(BaseSchema):
    """Schema for triage response."""
    case_id: UUID
    triage_id: UUID
    case_type: CaseType
    urgency: UrgencyLevel
    risk_level: RiskLevel
    risk_score: float = Field(..., ge=0, le=1)
    recommended_team: str
    sla_target_hours: int
    escalation_flag: bool
    agent_results: List[AgentResult]
    suggested_actions: List[str]
    missing_fields: List[str]
    compliance_issues: List[str]
    processing_time_ms: int
    created_at: datetime


# User schemas
class UserCreate(BaseSchema):
    """Schema for creating a user."""
    email: str = Field(..., regex=r"^[^@]+@[^@]+\.[^@]+$")
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole
    team_id: Optional[UUID] = None
    is_active: bool = True


class UserUpdate(BaseSchema):
    """Schema for updating a user."""
    email: Optional[str] = Field(None, regex=r"^[^@]+@[^@]+\.[^@]+$")
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    team_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class UserResponse(BaseSchema):
    """Schema for user response."""
    id: UUID
    email: str
    username: str
    full_name: str
    role: UserRole
    team_id: Optional[UUID]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]


# Team schemas
class TeamCreate(BaseSchema):
    """Schema for creating a team."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    capacity: int = Field(..., ge=1)
    case_types: List[CaseType] = Field(default_factory=list)
    sla_target_hours: int = Field(..., ge=1)
    is_active: bool = True


class TeamUpdate(BaseSchema):
    """Schema for updating a team."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    capacity: Optional[int] = Field(None, ge=1)
    case_types: Optional[List[CaseType]] = None
    sla_target_hours: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class TeamResponse(BaseSchema):
    """Schema for team response."""
    id: UUID
    name: str
    description: Optional[str]
    capacity: int
    current_load: int
    case_types: List[CaseType]
    sla_target_hours: int
    is_active: bool
    created_at: datetime
    members: List[UserResponse]


# Audit schemas
class AuditLogCreate(BaseSchema):
    """Schema for creating audit log."""
    case_id: UUID
    user_id: Optional[UUID]
    action: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogResponse(BaseSchema):
    """Schema for audit log response."""
    id: UUID
    case_id: UUID
    user_id: Optional[UUID]
    user_name: Optional[str]
    action: str
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime


# Analytics schemas
class AnalyticsRequest(BaseSchema):
    """Schema for analytics request."""
    start_date: datetime
    end_date: datetime
    team_id: Optional[UUID] = None
    case_type: Optional[CaseType] = None
    status: Optional[CaseStatus] = None


class VolumeMetrics(BaseSchema):
    """Schema for volume metrics."""
    total_cases: int
    cases_by_type: Dict[str, int]
    cases_by_status: Dict[str, int]
    cases_by_urgency: Dict[str, int]
    cases_by_risk: Dict[str, int]


class SLAMetrics(BaseSchema):
    """Schema for SLA metrics."""
    avg_processing_time_hours: float
    sla_adherence_rate: float
    sla_breaches: int
    avg_time_to_triage_minutes: float


class RiskMetrics(BaseSchema):
    """Schema for risk metrics."""
    avg_risk_score: float
    risk_distribution: Dict[str, int]
    high_risk_cases: int
    fraud_detection_rate: float


class AnalyticsResponse(BaseSchema):
    """Schema for analytics response."""
    volume: VolumeMetrics
    sla: SLAMetrics
    risk: RiskMetrics
    team_performance: Dict[str, Dict[str, Any]]


# Document schemas
class DocumentUpload(BaseSchema):
    """Schema for document upload."""
    case_id: UUID
    file_name: str
    file_type: str
    file_size: int
    content_hash: str


class DocumentResponse(BaseSchema):
    """Schema for document response."""
    id: UUID
    case_id: UUID
    file_name: str
    file_type: str
    file_size: int
    content_hash: str
    uploaded_at: datetime
    uploaded_by: UUID
    pii_detected: bool
    pii_redacted: bool


# Error schemas
class ErrorResponse(BaseSchema):
    """Schema for error responses."""
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Health check schemas
class HealthCheck(BaseSchema):
    """Schema for health check response."""
    status: str
    version: str
    timestamp: datetime
    services: Dict[str, str]
    database: str
    redis: str
    opa: str
    vector_store: str
