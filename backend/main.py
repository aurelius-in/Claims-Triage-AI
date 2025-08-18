"""
Main FastAPI application for the Claims Triage AI platform.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from .core.security import setup_security_middleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn
from uuid import UUID
from datetime import datetime

from .core.config import settings, get_settings
from .core.logging import setup_logging
from .core.monitoring import setup_monitoring, instrument_application, shutdown_monitoring, get_health_status
from .core.telemetry import trace_span, record_request_metric, record_triage_metric, record_agent_execution_metric
from .core.prometheus import get_metrics, get_metrics_content_type
from .core.auth import get_current_user, create_access_token, can_access_case
from .core.redis import init_redis, close_redis, redis_health_check, check_rate_limit, cache_get_json, cache_set_json, enqueue_job, get_queue_length
from .core.vector_store import init_vector_store, close_vector_store, vector_store_health_check
from .core.opa import init_opa, close_opa, opa_health_check
from .core.background_jobs import start_background_processor, stop_background_processor
from .data.schemas import *
from .data.database import get_db, init_db, close_db
from .data.repository import (
    CaseRepository, UserRepository, TeamRepository, 
    DocumentRepository, AuditRepository, TriageResultRepository
)
from .agents.orchestrator import AgentOrchestrator

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator: AgentOrchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global orchestrator
    
    # Startup
    logger.info("Starting Claims Triage AI application...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize Redis
    redis_ok = await init_redis()
    if redis_ok:
        logger.info("Redis initialized")
    else:
        logger.warning("Redis initialization failed - some features may be limited")
    
    # Initialize Vector Store
    vector_store_ok = await init_vector_store()
    if vector_store_ok:
        logger.info("Vector store initialized")
    else:
        logger.warning("Vector store initialization failed - RAG features may be limited")
    
    # Initialize OPA
    opa_ok = await init_opa()
    if opa_ok:
        logger.info("OPA initialized")
    else:
        logger.warning("OPA initialization failed - policy features may be limited")
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    logger.info("Agent orchestrator initialized")
    
    # Setup monitoring and telemetry
    setup_monitoring(
        enable_telemetry=True,
        enable_prometheus=True,
        prometheus_port=settings.prometheus_port,
        environment="development"
    )
    logger.info("Monitoring setup complete")
    
    # Instrument the application
    instrument_application(app)
    logger.info("Application instrumentation complete")
    
    # Start background job processor
    asyncio.create_task(start_background_processor())
    logger.info("Background job processor started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Claims Triage AI application...")
    await stop_background_processor()
    shutdown_monitoring()
    await close_db()
    await close_redis()
    await close_vector_store()
    await close_opa()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Next-generation agent-driven case triage platform",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Setup security middleware
setup_security_middleware(app)


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    """Rate limiting middleware."""
    client_ip = request.client.host
    rate_limit_key = f"rate_limit:{client_ip}"
    
    # Check rate limit (60 requests per minute)
    if not await check_rate_limit(rate_limit_key, settings.rate_limit_per_minute, 60):
        raise HTTPException(
            status_code=429, 
            detail="Rate limit exceeded. Please try again later."
        )
    
    response = await call_next(request)
    return response

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


# Health check endpoint
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    return get_health_status()


# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=get_metrics(),
        media_type=get_metrics_content_type()
    )


# API v1 router
from fastapi import APIRouter

api_v1_router = APIRouter(prefix=settings.api_v1_prefix)


# Cases endpoints
@api_v1_router.post("/cases", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case: CaseCreate, 
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new case."""
    try:
        case_repo = CaseRepository(db)
        
        # Create case
        db_case = await case_repo.create_case(case)
        
        # Create audit log
        audit_repo = AuditRepository(db)
        await audit_repo.create_audit_log(AuditLogCreate(
            action="case_created",
            resource_type="case",
            resource_id=str(db_case.id),
            user_id=current_user.id,
            details={"case_type": case.case_type, "title": case.title}
        ))
        
        await db.commit()
        
        return CaseResponse.from_orm(db_case)
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Case creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.get("/cases/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: UUID, 
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a case by ID."""
    try:
        # Try to get from cache first
        cache_key = f"case:{case_id}"
        cached_case = await cache_get_json(cache_key)
        
        if cached_case:
            # Check access permissions for cached data
            if not can_access_case(current_user, cached_case):
                raise HTTPException(status_code=403, detail="Access denied")
            return CaseResponse(**cached_case)
        
        # If not in cache, get from database
        case_repo = CaseRepository(db)
        db_case = await case_repo.get_case(case_id)
        
        if not db_case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Check access permissions
        if not can_access_case(current_user, db_case):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Cache the case for 5 minutes
        case_data = CaseResponse.from_orm(db_case).dict()
        await cache_set_json(cache_key, case_data, expire=300)
        
        return CaseResponse.from_orm(db_case)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Case retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.put("/cases/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: UUID, 
    case_update: CaseUpdate, 
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a case."""
    try:
        case_repo = CaseRepository(db)
        
        # Get existing case
        db_case = await case_repo.get_case(case_id)
        if not db_case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Check access permissions
        if not can_access_case(current_user, db_case):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update case
        updated_case = await case_repo.update_case(case_id, case_update)
        
        # Create audit log
        audit_repo = AuditRepository(db)
        await audit_repo.create_audit_log(AuditLogCreate(
            action="case_updated",
            resource_type="case",
            resource_id=str(case_id),
            user_id=current_user.id,
            details={"updated_fields": list(case_update.dict(exclude_unset=True).keys())}
        ))
        
        await db.commit()
        
        return CaseResponse.from_orm(updated_case)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Case update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.get("/cases", response_model=List[CaseResponse])
async def list_cases(
    skip: int = 0,
    limit: int = 100,
    status: Optional[CaseStatus] = None,
    case_type: Optional[CaseType] = None,
    urgency_level: Optional[UrgencyLevel] = None,
    risk_level: Optional[RiskLevel] = None,
    team_id: Optional[UUID] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List cases with filtering."""
    try:
        case_repo = CaseRepository(db)
        
        # Get cases with filters
        db_cases = await case_repo.list_cases(
            skip=skip,
            limit=limit,
            status=status,
            case_type=case_type,
            urgency_level=urgency_level,
            risk_level=risk_level,
            team_id=team_id
        )
        
        return [CaseResponse.from_orm(case) for case in db_cases]
        
    except Exception as e:
        logger.error(f"Case listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Triage endpoints
@api_v1_router.post("/triage/run", response_model=TriageResponse)
async def run_triage(
    triage_request: TriageRequest, 
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Run triage for a case."""
    global orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Triage service not available")
    
    try:
        # Get case from database
        case_repo = CaseRepository(db)
        db_case = await case_repo.get_case(UUID(triage_request.case_id))
        
        if not db_case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Check access permissions
        if not can_access_case(current_user, db_case):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Prepare case data for triage
        case_data = {
            "id": str(db_case.id),
            "title": db_case.title,
            "description": db_case.description,
            "case_type": db_case.case_type.value,
            "urgency_level": db_case.urgency_level.value,
            "risk_level": db_case.risk_level.value,
            "risk_score": db_case.risk_score,
            "metadata": db_case.metadata or {}
        }
        
        # Run triage
        orchestration_result = await orchestrator.run_triage(
            case_data, 
            force_reprocess=triage_request.force_reprocess
        )
        
        if not orchestration_result.success:
            raise HTTPException(
                status_code=500, 
                detail=orchestration_result.error_message or "Triage failed"
            )
        
        # Store triage result in database
        triage_repo = TriageResultRepository(db)
        await triage_repo.create_triage_result({
            "case_id": db_case.id,
            "classifier_result": orchestration_result.classifier_result,
            "risk_scorer_result": orchestration_result.risk_scorer_result,
            "router_result": orchestration_result.router_result,
            "decision_support_result": orchestration_result.decision_support_result,
            "compliance_result": orchestration_result.compliance_result,
            "overall_confidence": orchestration_result.overall_confidence,
            "processing_time_ms": orchestration_result.processing_time_ms,
            "agent_errors": orchestration_result.agent_errors,
            "circuit_breaker_triggered": orchestration_result.circuit_breaker_triggered
        })
        
        # Update case with triage results
        if orchestration_result.router_result:
            router_result = orchestration_result.router_result
            await case_repo.update_case(db_case.id, CaseUpdate(
                assigned_team_id=UUID(router_result.get("assigned_team_id")) if router_result.get("assigned_team_id") else None,
                status=CaseStatus.IN_PROGRESS,
                triaged_at=datetime.utcnow()
            ))
        
        # Create audit log
        audit_repo = AuditRepository(db)
        await audit_repo.create_audit_log(AuditLogCreate(
            action="triage_completed",
            resource_type="case",
            resource_id=str(db_case.id),
            user_id=current_user.id,
            details={
                "confidence": orchestration_result.overall_confidence,
                "processing_time_ms": orchestration_result.processing_time_ms
            }
        ))
        
        await db.commit()
        
        # Convert to response
        triage_response = orchestrator.to_triage_response(orchestration_result)
        
        return triage_response
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Triage failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.get("/triage/status")
async def get_triage_status(current_user: UserResponse = Depends(get_current_user)):
    """Get triage system status."""
    global orchestrator
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Triage service not available")
    
    try:
        agent_status = orchestrator.get_agent_status()
        return {
            "status": "operational",
            "agents": agent_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Analytics endpoints
@api_v1_router.post("/analytics/overview", response_model=AnalyticsResponse)
async def get_analytics_overview(
    analytics_request: AnalyticsRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get analytics overview."""
    try:
        # TODO: Implement analytics calculation
        return AnalyticsResponse(
            volume=VolumeMetrics(
                total_cases=0,
                cases_by_type={},
                cases_by_status={},
                cases_by_urgency={},
                cases_by_risk={}
            ),
            sla=SLAMetrics(
                avg_processing_time_hours=0.0,
                sla_adherence_rate=0.0,
                sla_breaches=0,
                avg_time_to_triage_minutes=0.0
            ),
            risk=RiskMetrics(
                avg_risk_score=0.0,
                risk_distribution={},
                high_risk_cases=0,
                fraud_detection_rate=0.0
            ),
            team_performance={}
        )
        
    except Exception as e:
        logger.error(f"Analytics failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.get("/analytics/volume")
async def get_volume_metrics(
    start_date: datetime,
    end_date: datetime,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get volume metrics."""
    try:
        # TODO: Implement volume metrics calculation
        return {
            "total_cases": 0,
            "cases_by_type": {},
            "cases_by_status": {},
            "cases_by_urgency": {},
            "cases_by_risk": {}
        }
        
    except Exception as e:
        logger.error(f"Volume metrics failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.get("/analytics/sla")
async def get_sla_metrics(
    start_date: datetime,
    end_date: datetime,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get SLA metrics."""
    try:
        # TODO: Implement SLA metrics calculation
        return {
            "avg_processing_time_hours": 0.0,
            "sla_adherence_rate": 0.0,
            "sla_breaches": 0,
            "avg_time_to_triage_minutes": 0.0
        }
        
    except Exception as e:
        logger.error(f"SLA metrics failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Audit endpoints
@api_v1_router.get("/audit/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    case_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get audit logs."""
    try:
        audit_repo = AuditRepository(db)
        db_logs = await audit_repo.list_audit_logs(
            case_id=case_id,
            created_after=start_date,
            created_before=end_date,
            skip=skip,
            limit=limit
        )
        
        return [AuditLogResponse.from_orm(log) for log in db_logs]
        
    except Exception as e:
        logger.error(f"Audit log retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.get("/audit/export/{case_id}")
async def export_audit_packet(
    case_id: str,
    format: str = "json",
    current_user: UserResponse = Depends(get_current_user)
):
    """Export audit packet for a case."""
    try:
        # TODO: Implement audit packet export
        return {"message": "Export not implemented yet"}
        
    except Exception as e:
        logger.error(f"Audit export failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Teams endpoints
@api_v1_router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team: TeamCreate, 
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new team."""
    try:
        team_repo = TeamRepository(db)
        db_team = await team_repo.create_team(team)
        
        # Create audit log
        audit_repo = AuditRepository(db)
        await audit_repo.create_audit_log(AuditLogCreate(
            action="team_created",
            resource_type="team",
            resource_id=str(db_team.id),
            user_id=current_user.id,
            details={"team_name": team.name, "domain": team.domain}
        ))
        
        await db.commit()
        
        return TeamResponse.from_orm(db_team)
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Team creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.get("/teams", response_model=List[TeamResponse])
async def list_teams(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all teams."""
    try:
        team_repo = TeamRepository(db)
        db_teams = await team_repo.list_teams()
        
        return [TeamResponse.from_orm(team) for team in db_teams]
        
    except Exception as e:
        logger.error(f"Team listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Users endpoints
@api_v1_router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate, 
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user."""
    try:
        user_repo = UserRepository(db)
        db_user = await user_repo.create_user(user)
        
        # Create audit log
        audit_repo = AuditRepository(db)
        await audit_repo.create_audit_log(AuditLogCreate(
            action="user_created",
            resource_type="user",
            resource_id=str(db_user.id),
            user_id=current_user.id,
            details={"username": user.username, "role": user.role}
        ))
        
        await db.commit()
        
        return UserResponse.from_orm(db_user)
        
    except Exception as e:
        await db.rollback()
        logger.error(f"User creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all users."""
    try:
        user_repo = UserRepository(db)
        db_users = await user_repo.list_users()
        
        return [UserResponse.from_orm(user) for user in db_users]
        
    except Exception as e:
        logger.error(f"User listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Auth endpoints
@api_v1_router.post("/auth/login")
async def login(username: str, password: str):
    """User login."""
    try:
        # TODO: Implement actual authentication
        if username == "admin" and password == "password":
            access_token = create_access_token(data={"sub": username})
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Document endpoints
@api_v1_router.post("/cases/{case_id}/documents", response_model=DocumentResponse)
async def upload_document(
    case_id: UUID,
    file: UploadFile = File(...),
    document_type: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a document for a case."""
    try:
        # Check if case exists
        case_repo = CaseRepository(db)
        db_case = await case_repo.get_case(case_id)
        if not db_case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Check access permissions
        if not can_access_case(current_user, db_case):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Save file to storage
        import os
        from pathlib import Path
        
        upload_dir = Path("uploads") / str(case_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / f"{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create document record
        document_repo = DocumentRepository(db)
        document_data = DocumentCreate(
            case_id=case_id,
            filename=str(file_path),
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=len(content),
            mime_type=file.content_type or "application/octet-stream",
            document_type=document_type
        )
        
        db_document = await document_repo.create_document(document_data)
        
        # Create audit log
        audit_repo = AuditRepository(db)
        await audit_repo.create_audit_log(AuditLogCreate(
            action="document_uploaded",
            resource_type="document",
            resource_id=str(db_document.id),
            user_id=current_user.id,
            details={
                "filename": file.filename,
                "file_size": len(content),
                "document_type": document_type
            }
        ))
        
        await db.commit()
        
        return DocumentResponse.from_orm(db_document)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Document upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Queue management endpoints
@api_v1_router.post("/queue/jobs")
async def enqueue_background_job(
    job_type: str,
    job_data: dict,
    priority: int = 0,
    current_user: UserResponse = Depends(get_current_user)
):
    """Enqueue a background job."""
    try:
        # Add user info to job data
        job_data["user_id"] = str(current_user.id)
        job_data["timestamp"] = datetime.utcnow().isoformat()
        
        # Enqueue the job
        await enqueue_job("background_jobs", {
            "type": job_type,
            "data": job_data
        }, priority=priority)
        
        return {
            "message": "Job enqueued successfully",
            "job_type": job_type,
            "priority": priority
        }
        
    except Exception as e:
        logger.error(f"Job enqueue failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.get("/queue/status")
async def get_queue_status(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get queue status and length."""
    try:
        queue_length = await get_queue_length("background_jobs")
        
        return {
            "queue": "background_jobs",
            "length": queue_length,
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"Queue status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.get("/cache/stats")
async def get_cache_stats(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get cache statistics."""
    try:
        from .core.redis import get_cache_stats
        stats = await get_cache_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Cache stats failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.delete("/cache/clear")
async def clear_cache(
    pattern: str = "*",
    current_user: UserResponse = Depends(get_current_user)
):
    """Clear cache entries matching pattern."""
    try:
        from .core.redis import clear_cache_pattern
        await clear_cache_pattern(pattern)
        return {"message": f"Cache cleared for pattern: {pattern}"}
        
    except Exception as e:
        logger.error(f"Cache clear failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.post("/cache/idempotency")
async def set_idempotency_key_endpoint(
    key: str,
    expire: int = 300,
    current_user: UserResponse = Depends(get_current_user)
):
    """Set idempotency key."""
    try:
        from .core.redis import set_idempotency_key
        success = await set_idempotency_key(key, expire)
        return {"success": success, "key": key}
        
    except Exception as e:
        logger.error(f"Idempotency key set failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Vector Store endpoints
@api_v1_router.post("/vector-store/knowledge-base")
async def add_knowledge_base_entry(
    content: str,
    metadata: dict,
    category: str = "general",
    current_user: UserResponse = Depends(get_current_user)
):
    """Add entry to knowledge base."""
    try:
        from .core.vector_store import add_knowledge_base_entry
        
        entry_id = await add_knowledge_base_entry(content, metadata, category)
        
        return {
            "message": "Knowledge base entry added successfully",
            "entry_id": entry_id,
            "category": category
        }
        
    except Exception as e:
        logger.error(f"Knowledge base entry addition failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.get("/vector-store/knowledge-base/search")
async def search_knowledge_base(
    query: str,
    n_results: int = 5,
    category: Optional[str] = None,
    threshold: float = 0.7,
    current_user: UserResponse = Depends(get_current_user)
):
    """Search knowledge base."""
    try:
        from .core.vector_store import search_knowledge_base
        
        results = await search_knowledge_base(query, n_results, category, threshold)
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        logger.error(f"Knowledge base search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.post("/vector-store/documents")
async def add_document_embedding(
    document_id: str,
    content: str,
    metadata: dict,
    current_user: UserResponse = Depends(get_current_user)
):
    """Add document embedding for similarity search."""
    try:
        from .core.vector_store import add_document_embedding
        
        doc_id = await add_document_embedding(document_id, content, metadata)
        
        return {
            "message": "Document embedding added successfully",
            "document_id": doc_id
        }
        
    except Exception as e:
        logger.error(f"Document embedding addition failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.get("/vector-store/documents/similar")
async def find_similar_documents(
    content: str,
    n_results: int = 5,
    threshold: float = 0.7,
    current_user: UserResponse = Depends(get_current_user)
):
    """Find similar documents."""
    try:
        from .core.vector_store import find_similar_documents
        
        results = await find_similar_documents(content, n_results, threshold)
        
        return {
            "content": content,
            "similar_documents": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        logger.error(f"Similar document search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.post("/vector-store/decision-support")
async def get_decision_support(
    case_context: str,
    decision_type: str = "general",
    n_results: int = 3,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get decision support information."""
    try:
        from .core.vector_store import get_decision_support
        
        support_info = await get_decision_support(case_context, decision_type, n_results)
        
        return {
            "case_context": case_context,
            "decision_type": decision_type,
            "support_info": support_info
        }
        
    except Exception as e:
        logger.error(f"Decision support failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# OPA Policy endpoints
@api_v1_router.post("/policies/routing/evaluate")
async def evaluate_routing_policy_endpoint(
    case_data: dict,
    current_user: UserResponse = Depends(get_current_user)
):
    """Evaluate routing policy for case assignment."""
    try:
        from .core.opa import evaluate_routing_policy
        
        result = await evaluate_routing_policy(case_data)
        
        return {
            "case_data": case_data,
            "routing_result": result
        }
        
    except Exception as e:
        logger.error(f"Routing policy evaluation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.post("/policies/compliance/evaluate")
async def evaluate_compliance_policy_endpoint(
    case_data: dict,
    current_user: UserResponse = Depends(get_current_user)
):
    """Evaluate compliance policy for case validation."""
    try:
        from .core.opa import evaluate_compliance_policy
        
        result = await evaluate_compliance_policy(case_data)
        
        return {
            "case_data": case_data,
            "compliance_result": result
        }
        
    except Exception as e:
        logger.error(f"Compliance policy evaluation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.post("/policies/access-control/evaluate")
async def evaluate_access_control_policy_endpoint(
    user_data: dict,
    resource_data: dict,
    current_user: UserResponse = Depends(get_current_user)
):
    """Evaluate access control policy."""
    try:
        from .core.opa import evaluate_access_control_policy
        
        result = await evaluate_access_control_policy(user_data, resource_data)
        
        return {
            "user_data": user_data,
            "resource_data": resource_data,
            "access_result": result
        }
        
    except Exception as e:
        logger.error(f"Access control policy evaluation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.post("/policies/data-governance/evaluate")
async def evaluate_data_governance_policy_endpoint(
    data_operation: dict,
    current_user: UserResponse = Depends(get_current_user)
):
    """Evaluate data governance policy."""
    try:
        from .core.opa import evaluate_data_governance_policy
        
        result = await evaluate_data_governance_policy(data_operation)
        
        return {
            "data_operation": data_operation,
            "governance_result": result
        }
        
    except Exception as e:
        logger.error(f"Data governance policy evaluation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.post("/policies")
async def create_policy_endpoint(
    policy_name: str,
    policy_content: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new policy."""
    try:
        from .core.opa import create_policy
        
        result = await create_policy(policy_name, policy_content)
        
        return {
            "policy_name": policy_name,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Policy creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.put("/policies/{policy_name}")
async def update_policy_endpoint(
    policy_name: str,
    policy_content: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update an existing policy."""
    try:
        from .core.opa import update_policy
        
        result = await update_policy(policy_name, policy_content)
        
        return {
            "policy_name": policy_name,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Policy update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.delete("/policies/{policy_name}")
async def delete_policy_endpoint(
    policy_name: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a policy."""
    try:
        from .core.opa import delete_policy
        
        result = await delete_policy(policy_name)
        
        return {
            "policy_name": policy_name,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Policy deletion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.get("/policies")
async def list_policies_endpoint(
    current_user: UserResponse = Depends(get_current_user)
):
    """List all available policies."""
    try:
        from .core.opa import list_policies
        
        result = await list_policies()
        
        return result
        
    except Exception as e:
        logger.error(f"Policy listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_v1_router.post("/policies/validate")
async def validate_policy_endpoint(
    policy_content: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Validate policy syntax and structure."""
    try:
        from .core.opa import validate_policy
        
        result = await validate_policy(policy_content)
        
        return {
            "policy_content": policy_content,
            "validation_result": result
        }
        
    except Exception as e:
        logger.error(f"Policy validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Include API router
app.include_router(api_v1_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
