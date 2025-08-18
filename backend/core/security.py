"""
Security and compliance middleware for the Claims Triage AI platform.
"""

import re
import json
import hashlib
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import html
from datetime import datetime

from .config import settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        # HSTS (only for HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class RequestSizeMiddleware(BaseHTTPMiddleware):
    """Middleware to limit request size."""
    
    def __init__(self, app: ASGIApp, max_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_size = max_size
    
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_size:
                    return JSONResponse(
                        status_code=413,
                        content={"detail": f"Request too large. Maximum size is {self.max_size} bytes."}
                    )
            except ValueError:
                pass
        
        response = await call_next(request)
        return response


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for input validation and sanitization."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        
        # SQL injection patterns
        self.sql_patterns = [
            r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
            r"(\b(and|or)\b\s+\d+\s*=\s*\d+)",
            r"(\b(and|or)\b\s+['\"].*['\"])",
            r"(--|#|/\*|\*/)",
            r"(\bxp_|sp_|sysobjects|syscolumns)",
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
        ]
        
        # Path traversal patterns
        self.path_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Validate path
        if not self._validate_path(request.url.path):
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid path detected"}
            )
        
        # Validate query parameters
        if not self._validate_query_params(request.query_params):
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid query parameters detected"}
            )
        
        # For POST/PUT requests, validate body
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    # Check for SQL injection in body
                    body_str = body.decode('utf-8', errors='ignore')
                    if self._contains_sql_injection(body_str):
                        return JSONResponse(
                            status_code=400,
                            content={"detail": "SQL injection attempt detected"}
                        )
                    
                    # Check for XSS in body
                    if self._contains_xss(body_str):
                        return JSONResponse(
                            status_code=400,
                            content={"detail": "XSS attempt detected"}
                        )
            except Exception as e:
                logger.warning(f"Error validating request body: {e}")
        
        response = await call_next(request)
        return response
    
    def _validate_path(self, path: str) -> bool:
        """Validate path for path traversal attempts."""
        path_lower = path.lower()
        for pattern in self.path_patterns:
            if re.search(pattern, path_lower, re.IGNORECASE):
                return False
        return True
    
    def _validate_query_params(self, query_params) -> bool:
        """Validate query parameters."""
        for key, value in query_params.items():
            param_str = f"{key}={value}"
            if self._contains_sql_injection(param_str) or self._contains_xss(param_str):
                return False
        return True
    
    def _contains_sql_injection(self, text: str) -> bool:
        """Check for SQL injection patterns."""
        for pattern in self.sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _contains_xss(self, text: str) -> bool:
        """Check for XSS patterns."""
        for pattern in self.xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False


class PIIDetectionMiddleware(BaseHTTPMiddleware):
    """Middleware for PII detection and redaction."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        
        # PII patterns for detection
        self.pii_patterns = {
            "ssn": {
                "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
                "replacement": "[SSN_REDACTED]",
                "description": "Social Security Number"
            },
            "credit_card": {
                "pattern": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
                "replacement": "[CC_REDACTED]",
                "description": "Credit Card Number"
            },
            "phone": {
                "pattern": r"\b\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}\b",
                "replacement": "[PHONE_REDACTED]",
                "description": "Phone Number"
            },
            "email": {
                "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "replacement": "[EMAIL_REDACTED]",
                "description": "Email Address"
            },
            "address": {
                "pattern": r"\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b",
                "replacement": "[ADDRESS_REDACTED]",
                "description": "Street Address"
            },
            "account_number": {
                "pattern": r"\b\d{8,}\b",
                "replacement": "[ACCOUNT_REDACTED]",
                "description": "Account Number"
            },
            "date_of_birth": {
                "pattern": r"\b(?:DOB|Date of Birth|Birth Date)[:\s]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
                "replacement": "[DOB_REDACTED]",
                "description": "Date of Birth"
            }
        }
    
    async def dispatch(self, request: Request, call_next):
        if not settings.pii_detection_enabled:
            return await call_next(request)
        
        # Detect PII in request
        pii_detected = await self._detect_request_pii(request)
        
        if pii_detected:
            logger.warning(f"PII detected in request from {request.client.host}")
            # For now, we'll log but allow the request to proceed
            # In production, you might want to block or flag these requests
        
        response = await call_next(request)
        
        # Detect PII in response (if it's JSON)
        if response.headers.get("content-type", "").startswith("application/json"):
            await self._detect_response_pii(response)
        
        return response
    
    async def _detect_request_pii(self, request: Request) -> bool:
        """Detect PII in request body and headers."""
        pii_found = False
        
        # Check headers
        for header_name, header_value in request.headers.items():
            if self._contains_pii(header_value):
                pii_found = True
                logger.warning(f"PII detected in header {header_name}")
        
        # Check query parameters
        for param_name, param_value in request.query_params.items():
            if self._contains_pii(param_value):
                pii_found = True
                logger.warning(f"PII detected in query parameter {param_name}")
        
        # Check request body for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    body_str = body.decode('utf-8', errors='ignore')
                    if self._contains_pii(body_str):
                        pii_found = True
                        logger.warning("PII detected in request body")
            except Exception as e:
                logger.warning(f"Error checking request body for PII: {e}")
        
        return pii_found
    
    async def _detect_response_pii(self, response: Response):
        """Detect PII in response body."""
        try:
            # Get response body
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # Check for PII
            if response_body:
                body_str = response_body.decode('utf-8', errors='ignore')
                if self._contains_pii(body_str):
                    logger.warning("PII detected in response body")
            
            # Reconstruct response
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        except Exception as e:
            logger.warning(f"Error checking response for PII: {e}")
            return response
    
    def _contains_pii(self, text: str) -> bool:
        """Check if text contains PII patterns."""
        for pii_type, pattern_info in self.pii_patterns.items():
            if re.search(pattern_info["pattern"], text, re.IGNORECASE):
                return True
        return False
    
    def redact_pii(self, text: str) -> Tuple[str, List[str]]:
        """Redact PII from text and return redacted text and detected types."""
        redacted_text = text
        detected_types = []
        
        for pii_type, pattern_info in self.pii_patterns.items():
            if re.search(pattern_info["pattern"], text, re.IGNORECASE):
                redacted_text = re.sub(
                    pattern_info["pattern"],
                    pattern_info["replacement"],
                    redacted_text,
                    flags=re.IGNORECASE
                )
                detected_types.append(pii_type)
        
        return redacted_text, detected_types


class DataRetentionMiddleware(BaseHTTPMiddleware):
    """Middleware for data retention policy enforcement."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        # Add data retention headers
        response = await call_next(request)
        
        # Add data retention policy headers
        response.headers["X-Data-Retention-Policy"] = f"{settings.audit_log_retention_days} days"
        response.headers["X-Data-Classification"] = "internal"
        
        return response


# Utility functions
def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS."""
    return html.escape(text, quote=True)


def validate_file_upload(filename: str, content_type: str, file_size: int) -> bool:
    """Validate file upload for security."""
    # Check file size
    if file_size > settings.max_file_size:
        return False
    
    # Check file extension
    allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png']
    file_ext = filename.lower()[filename.rfind('.'):]
    if file_ext not in allowed_extensions:
        return False
    
    # Check content type
    allowed_types = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'image/jpeg',
        'image/png'
    ]
    if content_type not in allowed_types:
        return False
    
    return True


def generate_audit_hash(data: Dict[str, Any], previous_hash: Optional[str] = None) -> str:
    """Generate hash for audit trail integrity."""
    # Create deterministic string representation
    hash_data = {
        "data": data,
        "timestamp": str(datetime.utcnow()),
        "previous_hash": previous_hash or ""
    }
    
    hash_string = json.dumps(hash_data, sort_keys=True)
    return hashlib.sha256(hash_string.encode()).hexdigest()


# Middleware setup function
def setup_security_middleware(app):
    """Setup all security middleware."""
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestSizeMiddleware, max_size=settings.max_file_size)
    app.add_middleware(InputValidationMiddleware)
    app.add_middleware(PIIDetectionMiddleware)
    app.add_middleware(DataRetentionMiddleware)
