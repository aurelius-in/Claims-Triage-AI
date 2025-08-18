"""
Authentication and authorization for the Claims Triage AI platform.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from .config import settings
from ..data.schemas import UserResponse, UserRole

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()


class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key.get_secret_value(), algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
        return token_data
    except JWTError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        token_data = verify_token(token)
        if token_data is None:
            raise credentials_exception
        
        # TODO: Get user from database
        # For now, return a mock user
        if token_data.username == "admin":
            return UserResponse(
                id="admin-user-id",
                email="admin@example.com",
                username="admin",
                full_name="Administrator",
                role=UserRole.ADMIN,
                team_id=None,
                is_active=True,
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
        else:
            raise credentials_exception
            
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise credentials_exception


def require_role(required_role: UserRole):
    """Decorator to require a specific role."""
    def role_checker(current_user: UserResponse = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


def require_any_role(required_roles: list[UserRole]):
    """Decorator to require any of the specified roles."""
    def role_checker(current_user: UserResponse = Depends(get_current_user)):
        if current_user.role not in required_roles and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


# Role-based access control
def can_access_case(user: UserResponse, case_team_id: Optional[str] = None) -> bool:
    """Check if user can access a case."""
    # Admin can access everything
    if user.role == UserRole.ADMIN:
        return True
    
    # Supervisor can access cases in their team
    if user.role == UserRole.SUPERVISOR:
        return user.team_id == case_team_id
    
    # Agent can access cases in their team
    if user.role == UserRole.AGENT:
        return user.team_id == case_team_id
    
    # Auditor can access everything (read-only)
    if user.role == UserRole.AUDITOR:
        return True
    
    return False


def can_modify_case(user: UserResponse, case_team_id: Optional[str] = None) -> bool:
    """Check if user can modify a case."""
    # Admin can modify everything
    if user.role == UserRole.ADMIN:
        return True
    
    # Supervisor can modify cases in their team
    if user.role == UserRole.SUPERVISOR:
        return user.team_id == case_team_id
    
    # Agent can modify cases in their team
    if user.role == UserRole.AGENT:
        return user.team_id == case_team_id
    
    # Auditor cannot modify anything
    return False


def can_run_triage(user: UserResponse) -> bool:
    """Check if user can run triage."""
    return user.role in [UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.AGENT]


def can_view_analytics(user: UserResponse) -> bool:
    """Check if user can view analytics."""
    return user.role in [UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.AUDITOR]


def can_manage_users(user: UserResponse) -> bool:
    """Check if user can manage users."""
    return user.role in [UserRole.ADMIN, UserRole.SUPERVISOR]


def can_manage_teams(user: UserResponse) -> bool:
    """Check if user can manage teams."""
    return user.role == UserRole.ADMIN


def can_view_audit_logs(user: UserResponse) -> bool:
    """Check if user can view audit logs."""
    return user.role in [UserRole.ADMIN, UserRole.AUDITOR]


def can_export_audit_data(user: UserResponse) -> bool:
    """Check if user can export audit data."""
    return user.role == UserRole.AUDITOR
