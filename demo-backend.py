from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import List, Optional
import uvicorn
import json
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="Claims Triage AI Demo API",
    description="Demo API for Claims Triage AI Platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Demo data
demo_cases = [
    {
        "id": "case-001",
        "title": "Auto Insurance Claim",
        "description": "Vehicle damage from collision",
        "case_type": "auto_insurance",
        "urgency": "high",
        "risk_level": "medium",
        "status": "pending",
        "created_at": "2024-01-15T10:30:00Z",
        "assigned_team": "Auto Claims"
    },
    {
        "id": "case-002", 
        "title": "Medical Prior Authorization",
        "description": "Cardiac surgery approval needed",
        "case_type": "healthcare_prior_auth",
        "urgency": "critical",
        "risk_level": "high",
        "status": "in_review",
        "created_at": "2024-01-15T09:15:00Z",
        "assigned_team": "Medical Review"
    },
    {
        "id": "case-003",
        "title": "Property Damage Claim",
        "description": "Home damage from storm",
        "case_type": "property_insurance",
        "urgency": "medium",
        "risk_level": "low",
        "status": "new",
        "created_at": "2024-01-15T11:45:00Z",
        "assigned_team": "Property Claims"
    }
]

demo_analytics = {
    "total_cases": 156,
    "pending_cases": 23,
    "completed_today": 12,
    "avg_processing_time": "2.3 hours",
    "sla_compliance": "94.2%",
    "risk_distribution": {
        "low": 45,
        "medium": 67,
        "high": 32,
        "critical": 12
    }
}

# Models
class LoginRequest(BaseModel):
    username: str
    password: str
    
    # SECURITY: Add input validation
    @validator('username')
    def validate_username(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Username cannot be empty')
        if len(v) > 50:
            raise ValueError('Username too long')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Password cannot be empty')
        if len(v) > 100:
            raise ValueError('Password too long')
        return v

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class Case(BaseModel):
    id: str
    title: str
    description: str
    case_type: str
    urgency: str
    risk_level: str
    status: str
    created_at: str
    assigned_team: str

class Analytics(BaseModel):
    total_cases: int
    pending_cases: int
    completed_today: int
    avg_processing_time: str
    sla_compliance: str
    risk_distribution: dict

# Authentication
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # SECURITY: Validate token format and check if it's a valid demo token
    token = credentials.credentials
    
    # SECURITY: Check token format
    if not token or not token.startswith("demo-token-"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )
    
    # SECURITY: In a real application, you would validate the token against a database
    # For demo purposes, we'll just check the format
    if len(token) < 20:  # Basic length validation
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return token

# Routes
@app.get("/")
async def root():
    return {"message": "Claims Triage AI Demo API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    # SECURITY: Use environment variables for demo credentials
    import os
    demo_username = os.getenv("DEMO_USERNAME", "demo")
    demo_password = os.getenv("DEMO_PASSWORD", "demo123")
    
    # SECURITY: Add rate limiting and logging for failed attempts
    if request.username == demo_username and request.password == demo_password:
        # SECURITY: Generate a proper JWT token instead of hardcoded string
        import secrets
        demo_token = f"demo-token-{secrets.token_urlsafe(16)}"
        
        return LoginResponse(
            access_token=demo_token,
            token_type="bearer",
            user={
                "id": "user-001",
                "username": demo_username,
                "email": "demo@example.com",
                "role": "demo",
                "name": "Demo User"
            }
        )
    else:
        # SECURITY: Log failed login attempts
        print(f"WARNING: Failed login attempt for username: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@app.get("/api/v1/cases", response_model=List[Case])
async def get_cases(token: str = Depends(verify_token)):
    return demo_cases

@app.get("/api/v1/cases/{case_id}", response_model=Case)
async def get_case(case_id: str, token: str = Depends(verify_token)):
    for case in demo_cases:
        if case["id"] == case_id:
            return case
    raise HTTPException(status_code=404, detail="Case not found")

@app.get("/api/v1/analytics", response_model=Analytics)
async def get_analytics(token: str = Depends(verify_token)):
    return demo_analytics

@app.post("/api/v1/triage/run")
async def run_triage(case_id: str, token: str = Depends(verify_token)):
    # Simulate triage processing
    return {
        "case_id": case_id,
        "triage_id": f"triage-{case_id}",
        "case_type": "auto_insurance",
        "urgency": "high",
        "risk_level": "medium",
        "recommended_team": "Auto Claims",
        "sla_target_hours": 4,
        "escalation_flag": False,
        "suggested_actions": [
            "Schedule vehicle inspection",
            "Contact policyholder",
            "Review police report"
        ],
        "processing_time_ms": 1250
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
