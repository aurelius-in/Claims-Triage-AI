#!/usr/bin/env python3
"""
Database initialization script for the Claims Triage AI platform.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from data.database import init_db, get_db_session
from data.models import (
    User, Team, TeamMember, Case, Document, TriageResult, 
    AuditLog, SystemMetrics, CaseStatus, CasePriority, CaseType, UserRole
)
from core.auth import get_password_hash
from core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_initial_data():
    """Create initial data for the application."""
    async with get_db_session() as session:
        try:
            # Create admin user
            admin_user = await create_admin_user(session)
            logger.info(f"Created admin user: {admin_user.username}")
            
            # Create default team
            default_team = await create_default_team(session, admin_user.id)
            logger.info(f"Created default team: {default_team.name}")
            
            # Create sample cases
            sample_cases = await create_sample_cases(session, admin_user.id, default_team.id)
            logger.info(f"Created {len(sample_cases)} sample cases")
            
            # Create sample documents
            sample_docs = await create_sample_documents(session, sample_cases)
            logger.info(f"Created {len(sample_docs)} sample documents")
            
            # Create sample triage results
            sample_results = await create_sample_triage_results(session, sample_cases)
            logger.info(f"Created {len(sample_results)} sample triage results")
            
            # Create sample audit logs
            sample_audits = await create_sample_audit_logs(session, admin_user.id, sample_cases)
            logger.info(f"Created {len(sample_audits)} sample audit logs")
            
            # Create sample system metrics
            sample_metrics = await create_sample_metrics(session)
            logger.info(f"Created {len(sample_metrics)} sample system metrics")
            
            await session.commit()
            logger.info("Database initialization completed successfully")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to create initial data: {str(e)}")
            raise


async def create_admin_user(session) -> User:
    """Create the default admin user."""
    from sqlalchemy import select
    
    # Check if admin user already exists
    result = await session.execute(select(User).where(User.username == "admin"))
    existing_admin = result.scalar_one_or_none()
    if existing_admin:
        logger.info("Admin user already exists")
        return existing_admin
    
    # Create admin user
    admin_user = User(
        username="admin",
        email="admin@claimstriage.ai",
        hashed_password=get_password_hash("admin123"),
        full_name="System Administrator",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )
    session.add(admin_user)
    await session.flush()
    return admin_user


async def create_default_team(session, manager_id) -> Team:
    """Create the default team."""
    from sqlalchemy import select
    
    # Check if default team already exists
    result = await session.execute(select(Team).where(Team.name == "Claims Processing Team"))
    existing_team = result.scalar_one_or_none()
    if existing_team:
        logger.info("Default team already exists")
        return existing_team
    
    # Create default team
    default_team = Team(
        name="Claims Processing Team",
        description="Default team for processing insurance claims",
        manager_id=manager_id,
        is_active=True
    )
    session.add(default_team)
    await session.flush()
    
    # Add manager to team
    team_member = TeamMember(
        team_id=default_team.id,
        user_id=manager_id,
        role="Manager"
    )
    session.add(team_member)
    await session.flush()
    
    return default_team


async def create_sample_cases(session, user_id, team_id) -> list:
    """Create sample cases."""
    sample_cases = [
        {
            "case_number": "CLM-2024-001",
            "title": "Auto Accident Claim",
            "description": "Vehicle collision on highway, moderate damage",
            "case_type": CaseType.AUTO_CLAIM,
            "customer_name": "John Smith",
            "customer_email": "john.smith@email.com",
            "customer_phone": "+1-555-0123",
            "claim_amount": 15000.00,
            "priority": CasePriority.HIGH,
            "assigned_user_id": user_id,
            "team_id": team_id
        },
        {
            "case_number": "CLM-2024-002",
            "title": "Home Fire Damage",
            "description": "Kitchen fire causing structural damage",
            "case_type": CaseType.HOME_CLAIM,
            "customer_name": "Sarah Johnson",
            "customer_email": "sarah.j@email.com",
            "customer_phone": "+1-555-0456",
            "claim_amount": 75000.00,
            "priority": CasePriority.URGENT,
            "assigned_user_id": user_id,
            "team_id": team_id
        },
        {
            "case_number": "CLM-2024-003",
            "title": "Medical Procedure Claim",
            "description": "Emergency surgery for appendicitis",
            "case_type": CaseType.HEALTH_CLAIM,
            "customer_name": "Michael Brown",
            "customer_email": "mike.brown@email.com",
            "customer_phone": "+1-555-0789",
            "claim_amount": 25000.00,
            "priority": CasePriority.NORMAL,
            "assigned_user_id": user_id,
            "team_id": team_id
        },
        {
            "case_number": "CLM-2024-004",
            "title": "Business Interruption",
            "description": "Office building damage from storm",
            "case_type": CaseType.BUSINESS_CLAIM,
            "customer_name": "ABC Corporation",
            "customer_email": "claims@abc-corp.com",
            "customer_phone": "+1-555-0321",
            "claim_amount": 125000.00,
            "priority": CasePriority.CRITICAL,
            "assigned_user_id": user_id,
            "team_id": team_id
        },
        {
            "case_number": "CLM-2024-005",
            "title": "Life Insurance Claim",
            "description": "Death benefit claim for policyholder",
            "case_type": CaseType.LIFE_CLAIM,
            "customer_name": "Emily Davis",
            "customer_email": "emily.davis@email.com",
            "customer_phone": "+1-555-0654",
            "claim_amount": 500000.00,
            "priority": CasePriority.HIGH,
            "assigned_user_id": user_id,
            "team_id": team_id
        }
    ]
    
    cases = []
    for case_data in sample_cases:
        # Check if case already exists
        result = await session.execute(select(Case).where(Case.case_number == case_data['case_number']))
        existing_case = result.scalar_one_or_none()
        if existing_case:
            continue
        
        case = Case(**case_data)
        session.add(case)
        await session.flush()
        cases.append(case)
    
    return cases


async def create_sample_documents(session, cases) -> list:
    """Create sample documents for cases."""
    documents = []
    for case in cases:
        doc_types = ["police_report", "medical_records", "photos", "receipts"]
        for i, doc_type in enumerate(doc_types):
            doc = Document(
                case_id=case.id,
                filename=f"{case.case_number}_{doc_type}_{i+1}.pdf",
                original_filename=f"{doc_type}_{i+1}.pdf",
                file_path=f"/uploads/{case.case_number}/{doc_type}_{i+1}.pdf",
                file_size=1024 * (i + 1),
                mime_type="application/pdf",
                document_type=doc_type,
                is_processed=True,
                processing_status="completed",
                extracted_text=f"Sample extracted text for {doc_type}",
                extracted_data={"type": doc_type, "confidence": 0.95}
            )
            session.add(doc)
            documents.append(doc)
    
    await session.flush()
    return documents


async def create_sample_triage_results(session, cases) -> list:
    """Create sample triage results for cases."""
    results = []
    for case in cases:
        result = TriageResult(
            case_id=case.id,
            classifier_result={
                "claim_type": case.case_type.value,
                "confidence": 0.92,
                "features": ["damage_amount", "location", "witnesses"]
            },
            risk_scorer_result={
                "risk_score": 0.75,
                "risk_factors": ["high_amount", "complex_case"],
                "recommendation": "Requires manual review"
            },
            router_result={
                "assigned_priority": case.priority.value,
                "sla_target": 48,
                "routing_reason": "High value claim"
            },
            decision_support_result={
                "recommended_action": "Approve with conditions",
                "confidence": 0.88,
                "supporting_evidence": ["documentation_complete", "witness_statements"]
            },
            compliance_result={
                "compliance_score": 0.95,
                "violations": [],
                "recommendations": ["Standard processing"]
            },
            final_priority=case.priority,
            final_status=CaseStatus.IN_REVIEW,
            confidence_score=0.87,
            processing_time=2.5
        )
        session.add(result)
        results.append(result)
    
    await session.flush()
    return results


async def create_sample_audit_logs(session, user_id, cases) -> list:
    """Create sample audit logs."""
    logs = []
    actions = ["case_created", "case_updated", "document_uploaded", "triage_completed"]
    
    for case in cases:
        for action in actions:
            log = AuditLog(
                user_id=user_id,
                case_id=case.id,
                action=action,
                resource_type="case",
                resource_id=str(case.id),
                details={"case_number": case.case_number},
                ip_address="192.168.1.100",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            session.add(log)
            logs.append(log)
    
    await session.flush()
    return logs


async def create_sample_metrics(session) -> list:
    """Create sample system metrics."""
    metrics_data = [
        {"metric_name": "total_cases", "metric_value": 150, "metric_unit": "count"},
        {"metric_name": "pending_cases", "metric_value": 45, "metric_unit": "count"},
        {"metric_name": "avg_processing_time", "metric_value": 2.3, "metric_unit": "hours"},
        {"metric_name": "sla_compliance_rate", "metric_value": 0.94, "metric_unit": "percentage"},
        {"metric_name": "accuracy_rate", "metric_value": 0.89, "metric_unit": "percentage"},
        {"metric_name": "system_uptime", "metric_value": 0.999, "metric_unit": "percentage"}
    ]
    
    metrics = []
    for metric_data in metrics_data:
        metric = SystemMetrics(**metric_data)
        session.add(metric)
        metrics.append(metric)
    
    await session.flush()
    return metrics


async def main():
    """Main initialization function."""
    try:
        logger.info("Starting database initialization...")
        
        # Initialize database
        await init_db()
        logger.info("Database schema created")
        
        # Create initial data
        await create_initial_data()
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
