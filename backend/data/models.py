"""
SQLAlchemy ORM models for the Claims Triage AI platform.
"""
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float, 
    ForeignKey, JSON, Enum as SQLEnum, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID
import uuid
from enum import Enum

Base = declarative_base()


class CaseType(str, Enum):
    """Case type enumeration."""
    AUTO_INSURANCE = "auto_insurance"
    HEALTH_INSURANCE = "health_insurance"
    PROPERTY_INSURANCE = "property_insurance"
    LIFE_INSURANCE = "life_insurance"
    FRAUD_REVIEW = "fraud_review"
    LEGAL_CASE = "legal_case"
    BANK_DISPUTE = "bank_dispute"
    HEALTHCARE_PRIOR_AUTH = "healthcare_prior_auth"
    GENERAL = "general"


class UrgencyLevel(str, Enum):
    """Urgency level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class CaseStatus(str, Enum):
    """Case status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REJECTED = "rejected"


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    AGENT = "agent"
    AUDITOR = "auditor"


class Team(Base):
    """Team model for organizing users and handling cases."""
    __tablename__ = "teams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    domain = Column(String(50), nullable=False)  # insurance, healthcare, finance, legal
    capacity = Column(Integer, default=100)
    current_load = Column(Integer, default=0)
    sla_target_hours = Column(Integer, default=24)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="team")
    cases: Mapped[List["Case"]] = relationship("Case", back_populates="assigned_team")
    
    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}', domain='{self.domain}')>"


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.AGENT)
    is_active = Column(Boolean, default=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="users")
    assigned_cases: Mapped[List["Case"]] = relationship("Case", back_populates="assigned_user")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class Case(Base):
    """Case model representing a triage case."""
    __tablename__ = "cases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(100), unique=True, index=True)
    case_type = Column(SQLEnum(CaseType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    urgency_level = Column(SQLEnum(UrgencyLevel), nullable=False)
    risk_level = Column(SQLEnum(RiskLevel), nullable=False)
    risk_score = Column(Float, nullable=False)
    status = Column(SQLEnum(CaseStatus), nullable=False, default=CaseStatus.PENDING)
    
    # Routing information
    assigned_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    assigned_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    sla_target = Column(DateTime)
    sla_deadline = Column(DateTime)
    
    # Case metadata
    priority_score = Column(Float, default=0.0)
    estimated_value = Column(Float)
    tags = Column(JSON)  # List of tags
    metadata = Column(JSON)  # Additional case-specific data
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    triaged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    # Relationships
    assigned_team: Mapped[Optional["Team"]] = relationship("Team", back_populates="cases")
    assigned_user: Mapped[Optional["User"]] = relationship("User", back_populates="assigned_cases")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="case")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="case")
    triage_results: Mapped[List["TriageResult"]] = relationship("TriageResult", back_populates="case")
    
    def __repr__(self):
        return f"<Case(id={self.id}, external_id='{self.external_id}', type='{self.case_type}')>"
    
    def calculate_sla_deadline(self) -> datetime:
        """Calculate SLA deadline based on urgency and team SLA target."""
        if not self.assigned_team:
            return self.created_at + timedelta(hours=24)
        
        urgency_multipliers = {
            UrgencyLevel.LOW: 4.0,
            UrgencyLevel.MEDIUM: 2.0,
            UrgencyLevel.HIGH: 1.0,
            UrgencyLevel.CRITICAL: 0.5
        }
        
        base_hours = self.assigned_team.sla_target_hours
        multiplier = urgency_multipliers.get(self.urgency_level, 1.0)
        target_hours = base_hours * multiplier
        
        return self.created_at + timedelta(hours=target_hours)


class Document(Base):
    """Document model for case attachments."""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    document_type = Column(String(50))  # claim_form, medical_record, etc.
    
    # Processing metadata
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String(50), default="pending")
    extracted_text = Column(Text)
    extracted_metadata = Column(JSON)
    
    # Security
    is_redacted = Column(Boolean, default=False)
    redaction_reason = Column(String(200))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="documents")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', case_id={self.case_id})>"


class TriageResult(Base):
    """Triage result model for storing agent outputs."""
    __tablename__ = "triage_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    
    # Agent results
    classifier_result = Column(JSON)
    risk_scorer_result = Column(JSON)
    router_result = Column(JSON)
    decision_support_result = Column(JSON)
    compliance_result = Column(JSON)
    
    # Orchestration metadata
    overall_confidence = Column(Float, nullable=False)
    processing_time_ms = Column(Integer, nullable=False)
    agent_errors = Column(JSON)  # List of agent errors if any
    circuit_breaker_triggered = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    case: Mapped["Case"] = relationship("Case", back_populates="triage_results")
    
    def __repr__(self):
        return f"<TriageResult(id={self.id}, case_id={self.case_id}, confidence={self.overall_confidence})>"


class AuditLog(Base):
    """Audit log model for compliance and tracking."""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Audit details
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)  # case, user, team, etc.
    resource_id = Column(String(100))
    details = Column(JSON)
    
    # Security
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    session_id = Column(String(100))
    
    # Compliance
    is_sensitive = Column(Boolean, default=False)
    redacted_details = Column(JSON)
    
    # Chain integrity
    previous_hash = Column(String(64))
    current_hash = Column(String(64), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    case: Mapped[Optional["Case"]] = relationship("Case", back_populates="audit_logs")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', case_id={self.case_id})>"


class AnalyticsSnapshot(Base):
    """Analytics snapshot model for storing aggregated metrics."""
    __tablename__ = "analytics_snapshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_date = Column(DateTime, nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)  # volume, sla, accuracy, etc.
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20))  # count, percentage, hours, etc.
    
    # Dimensions
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"))
    case_type = Column(SQLEnum(CaseType))
    urgency_level = Column(SQLEnum(UrgencyLevel))
    risk_level = Column(SQLEnum(RiskLevel))
    
    # Metadata
    aggregation_period = Column(String(20))  # hourly, daily, weekly, monthly
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    team: Mapped[Optional["Team"]] = relationship("Team")
    
    def __repr__(self):
        return f"<AnalyticsSnapshot(id={self.id}, metric='{self.metric_name}', value={self.metric_value})>"


# Indexes for performance
Index("idx_cases_external_id", Case.external_id)
Index("idx_cases_status_created", Case.status, Case.created_at)
Index("idx_cases_team_status", Case.assigned_team_id, Case.status)
Index("idx_cases_urgency_risk", Case.urgency_level, Case.risk_level)
Index("idx_audit_logs_case_action", AuditLog.case_id, AuditLog.action)
Index("idx_audit_logs_created", AuditLog.created_at)
Index("idx_analytics_snapshot_date_type", AnalyticsSnapshot.snapshot_date, AnalyticsSnapshot.metric_type)
