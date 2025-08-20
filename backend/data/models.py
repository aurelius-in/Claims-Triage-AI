"""
SQLAlchemy ORM models for the Claims Triage AI platform.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey, JSON, Enum
# from sqlalchemy.dialects.postgresql import UUID  # Commented out for SQLite compatibility
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

from .database import Base


class CaseStatus(str, enum.Enum):
    """Case status enumeration."""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    CLOSED = "closed"


class CasePriority(str, enum.Enum):
    """Case priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class CaseType(str, enum.Enum):
    """Case type enumeration."""
    AUTO_CLAIM = "auto_claim"
    HOME_CLAIM = "home_claim"
    HEALTH_CLAIM = "health_claim"
    LIFE_CLAIM = "life_claim"
    BUSINESS_CLAIM = "business_claim"


class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    REVIEWER = "reviewer"
    VIEWER = "viewer"


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    cases_assigned = relationship("Case", back_populates="assigned_user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Team(Base):
    """Team model."""
    __tablename__ = "teams"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    manager_id = Column(String(36), ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    manager = relationship("User")
    members = relationship("TeamMember", back_populates="team")
    cases = relationship("Case", back_populates="team")


class TeamMember(Base):
    """Team member model."""
    __tablename__ = "team_members"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey("teams.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role = Column(String(50), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User")


class Case(Base):
    """Case model."""
    __tablename__ = "cases"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    case_type = Column(Enum(CaseType), nullable=False)
    status = Column(Enum(CaseStatus), nullable=False, default=CaseStatus.PENDING)
    priority = Column(Enum(CasePriority), nullable=False, default=CasePriority.NORMAL)
    
    # Customer information
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(100))
    customer_phone = Column(String(20))
    
    # Financial information
    claim_amount = Column(Float)
    approved_amount = Column(Float)
    
    # Assignment
    assigned_user_id = Column(String(36), ForeignKey("users.id"))
    team_id = Column(String(36), ForeignKey("teams.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    due_date = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))
    
    # AI Analysis
    ai_confidence_score = Column(Float)
    ai_risk_score = Column(Float)
    ai_recommendation = Column(Text)
    ai_analysis_data = Column(JSON)
    
    # Relationships
    assigned_user = relationship("User", back_populates="cases_assigned")
    team = relationship("Team", back_populates="cases")
    documents = relationship("Document", back_populates="case")
    triage_results = relationship("TriageResult", back_populates="case")
    audit_logs = relationship("AuditLog", back_populates="case")


class Document(Base):
    """Document model."""
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    document_type = Column(String(50))
    
    # Processing
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String(50), default="pending")
    extracted_text = Column(Text)
    extracted_data = Column(JSON)
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    # Relationships
    case = relationship("Case", back_populates="documents")


class TriageResult(Base):
    """Triage result model."""
    __tablename__ = "triage_results"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False)
    
    # Agent results
    classifier_result = Column(JSON)
    risk_scorer_result = Column(JSON)
    router_result = Column(JSON)
    decision_support_result = Column(JSON)
    compliance_result = Column(JSON)
    
    # Overall result
    final_priority = Column(Enum(CasePriority))
    final_status = Column(Enum(CaseStatus))
    confidence_score = Column(Float)
    processing_time = Column(Float)  # in seconds
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    case = relationship("Case", back_populates="triage_results")


class AuditLog(Base):
    """Audit log model."""
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    case_id = Column(String(36), ForeignKey("cases.id"))
    
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(50))
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    case = relationship("Case", back_populates="audit_logs")


class SystemMetrics(Base):
    """System metrics model."""
    __tablename__ = "system_metrics"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20))
    tags = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    class Meta:
        indexes = [
            ("metric_name", "timestamp"),
        ]
