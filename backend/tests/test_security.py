"""
Tests for security and compliance middleware.
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from ..core.security import (
    SecurityHeadersMiddleware,
    RequestSizeMiddleware,
    InputValidationMiddleware,
    PIIDetectionMiddleware,
    DataRetentionMiddleware,
    sanitize_input,
    validate_file_upload,
    generate_audit_hash,
    setup_security_middleware
)


class TestSecurityHeadersMiddleware:
    """Test security headers middleware."""
    
    @pytest.mark.asyncio
    async def test_security_headers_added(self):
        """Test that security headers are added to responses."""
        app = FastAPI()
        middleware = SecurityHeadersMiddleware(app)
        
        # Mock request and response
        request = Mock(spec=Request)
        request.url.scheme = "http"
        
        response = JSONResponse(content={"test": "data"})
        
        # Mock call_next
        async def call_next(req):
            return response
        
        # Test middleware
        result = await middleware.dispatch(request, call_next)
        
        # Check security headers
        assert result.headers["X-Content-Type-Options"] == "nosniff"
        assert result.headers["X-Frame-Options"] == "DENY"
        assert result.headers["X-XSS-Protection"] == "1; mode=block"
        assert result.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert result.headers["Permissions-Policy"] == "geolocation=(), microphone=(), camera=()"
        assert "Content-Security-Policy" in result.headers
    
    @pytest.mark.asyncio
    async def test_hsts_header_https(self):
        """Test HSTS header is added for HTTPS requests."""
        app = FastAPI()
        middleware = SecurityHeadersMiddleware(app)
        
        # Mock HTTPS request
        request = Mock(spec=Request)
        request.url.scheme = "https"
        
        response = JSONResponse(content={"test": "data"})
        
        async def call_next(req):
            return response
        
        result = await middleware.dispatch(request, call_next)
        
        # Check HSTS header
        assert "Strict-Transport-Security" in result.headers


class TestRequestSizeMiddleware:
    """Test request size middleware."""
    
    @pytest.mark.asyncio
    async def test_request_size_limit_exceeded(self):
        """Test that large requests are rejected."""
        app = FastAPI()
        middleware = RequestSizeMiddleware(app, max_size=1024)  # 1KB limit
        
        # Mock request with large content length
        request = Mock(spec=Request)
        request.headers = {"content-length": "2048"}
        
        async def call_next(req):
            return JSONResponse(content={"test": "data"})
        
        result = await middleware.dispatch(request, call_next)
        
        # Should return 413 error
        assert result.status_code == 413
        assert "Request too large" in result.body.decode()
    
    @pytest.mark.asyncio
    async def test_request_size_under_limit(self):
        """Test that requests under limit are allowed."""
        app = FastAPI()
        middleware = RequestSizeMiddleware(app, max_size=1024)
        
        # Mock request with acceptable content length
        request = Mock(spec=Request)
        request.headers = {"content-length": "512"}
        
        response = JSONResponse(content={"test": "data"})
        
        async def call_next(req):
            return response
        
        result = await middleware.dispatch(request, call_next)
        
        # Should allow the request
        assert result.status_code == 200


class TestInputValidationMiddleware:
    """Test input validation middleware."""
    
    @pytest.mark.asyncio
    async def test_sql_injection_detection(self):
        """Test SQL injection detection."""
        app = FastAPI()
        middleware = InputValidationMiddleware(app)
        
        # Mock request with SQL injection in body
        request = Mock(spec=Request)
        request.method = "POST"
        request.url.path = "/api/test"
        request.query_params = {}
        request.body = AsyncMock(return_value=b"SELECT * FROM users WHERE id = 1")
        
        async def call_next(req):
            return JSONResponse(content={"test": "data"})
        
        result = await middleware.dispatch(request, call_next)
        
        # Should return 400 error
        assert result.status_code == 400
        assert "SQL injection attempt detected" in result.body.decode()
    
    @pytest.mark.asyncio
    async def test_xss_detection(self):
        """Test XSS detection."""
        app = FastAPI()
        middleware = InputValidationMiddleware(app)
        
        # Mock request with XSS in body
        request = Mock(spec=Request)
        request.method = "POST"
        request.url.path = "/api/test"
        request.query_params = {}
        request.body = AsyncMock(return_value=b"<script>alert('xss')</script>")
        
        async def call_next(req):
            return JSONResponse(content={"test": "data"})
        
        result = await middleware.dispatch(request, call_next)
        
        # Should return 400 error
        assert result.status_code == 400
        assert "XSS attempt detected" in result.body.decode()
    
    @pytest.mark.asyncio
    async def test_path_traversal_detection(self):
        """Test path traversal detection."""
        app = FastAPI()
        middleware = InputValidationMiddleware(app)
        
        # Mock request with path traversal
        request = Mock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/../../../etc/passwd"
        request.query_params = {}
        
        async def call_next(req):
            return JSONResponse(content={"test": "data"})
        
        result = await middleware.dispatch(request, call_next)
        
        # Should return 400 error
        assert result.status_code == 400
        assert "Invalid path detected" in result.body.decode()


class TestPIIDetectionMiddleware:
    """Test PII detection middleware."""
    
    @pytest.mark.asyncio
    async def test_ssn_detection(self):
        """Test SSN detection."""
        app = FastAPI()
        middleware = PIIDetectionMiddleware(app)
        
        # Mock request with SSN
        request = Mock(spec=Request)
        request.method = "POST"
        request.client.host = "127.0.0.1"
        request.headers = {}
        request.query_params = {}
        request.body = AsyncMock(return_value=b'{"ssn": "123-45-6789"}')
        
        response = JSONResponse(content={"test": "data"})
        
        async def call_next(req):
            return response
        
        result = await middleware.dispatch(request, call_next)
        
        # Should allow request but log warning
        assert result.status_code == 200
    
    @pytest.mark.asyncio
    async def test_credit_card_detection(self):
        """Test credit card detection."""
        app = FastAPI()
        middleware = PIIDetectionMiddleware(app)
        
        # Mock request with credit card
        request = Mock(spec=Request)
        request.method = "POST"
        request.client.host = "127.0.0.1"
        request.headers = {}
        request.query_params = {}
        request.body = AsyncMock(return_value=b'{"cc": "1234-5678-9012-3456"}')
        
        response = JSONResponse(content={"test": "data"})
        
        async def call_next(req):
            return response
        
        result = await middleware.dispatch(request, call_next)
        
        # Should allow request but log warning
        assert result.status_code == 200
    
    def test_pii_redaction(self):
        """Test PII redaction functionality."""
        middleware = PIIDetectionMiddleware(Mock())
        
        # Test text with PII
        text = "My SSN is 123-45-6789 and my email is test@example.com"
        redacted_text, detected_types = middleware.redact_pii(text)
        
        # Check redaction
        assert "[SSN_REDACTED]" in redacted_text
        assert "[EMAIL_REDACTED]" in redacted_text
        assert "123-45-6789" not in redacted_text
        assert "test@example.com" not in redacted_text
        
        # Check detected types
        assert "ssn" in detected_types
        assert "email" in detected_types


class TestDataRetentionMiddleware:
    """Test data retention middleware."""
    
    @pytest.mark.asyncio
    async def test_data_retention_headers(self):
        """Test that data retention headers are added."""
        app = FastAPI()
        middleware = DataRetentionMiddleware(app)
        
        # Mock request
        request = Mock(spec=Request)
        
        response = JSONResponse(content={"test": "data"})
        
        async def call_next(req):
            return response
        
        result = await middleware.dispatch(request, call_next)
        
        # Check data retention headers
        assert "X-Data-Retention-Policy" in result.headers
        assert "X-Data-Classification" in result.headers


class TestSecurityUtilities:
    """Test security utility functions."""
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        # Test XSS prevention
        malicious_input = '<script>alert("xss")</script>'
        sanitized = sanitize_input(malicious_input)
        
        assert '<script>' not in sanitized
        assert '&lt;script&gt;' in sanitized
    
    def test_validate_file_upload(self):
        """Test file upload validation."""
        # Test valid file
        assert validate_file_upload("test.pdf", "application/pdf", 1024) is True
        
        # Test invalid file type
        assert validate_file_upload("test.exe", "application/octet-stream", 1024) is False
        
        # Test invalid content type
        assert validate_file_upload("test.pdf", "text/plain", 1024) is False
    
    def test_generate_audit_hash(self):
        """Test audit hash generation."""
        data = {"action": "test", "user_id": "123"}
        previous_hash = "abc123"
        
        hash1 = generate_audit_hash(data, previous_hash)
        hash2 = generate_audit_hash(data, previous_hash)
        
        # Same inputs should produce same hash
        assert hash1 == hash2
        
        # Different previous hash should produce different hash
        hash3 = generate_audit_hash(data, "different")
        assert hash1 != hash3


class TestSecurityMiddlewareIntegration:
    """Test security middleware integration."""
    
    def test_setup_security_middleware(self):
        """Test security middleware setup."""
        app = FastAPI()
        
        # Should not raise any exceptions
        setup_security_middleware(app)
        
        # Check that middleware was added
        assert len(app.user_middleware) > 0
    
    def test_security_middleware_order(self):
        """Test that security middleware is applied in correct order."""
        app = FastAPI()
        setup_security_middleware(app)
        
        # Security middleware should be applied
        middleware_names = [str(middleware.cls) for middleware in app.user_middleware]
        
        assert any("SecurityHeadersMiddleware" in name for name in middleware_names)
        assert any("RequestSizeMiddleware" in name for name in middleware_names)
        assert any("InputValidationMiddleware" in name for name in middleware_names)
        assert any("PIIDetectionMiddleware" in name for name in middleware_names)
        assert any("DataRetentionMiddleware" in name for name in middleware_names)


# Integration test with FastAPI app
class TestSecurityIntegration:
    """Integration tests with FastAPI app."""
    
    def test_security_middleware_integration(self):
        """Test security middleware with actual FastAPI app."""
        app = FastAPI()
        
        @app.get("/test")
        def test_endpoint():
            return {"message": "test"}
        
        @app.post("/test-post")
        def test_post_endpoint():
            return {"message": "posted"}
        
        # Setup security middleware
        setup_security_middleware(app)
        
        client = TestClient(app)
        
        # Test normal request
        response = client.get("/test")
        assert response.status_code == 200
        
        # Check security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        
        # Test request with SQL injection
        response = client.post("/test-post", json={"query": "SELECT * FROM users"})
        # Should be blocked by input validation middleware
        assert response.status_code == 400
        
        # Test request with XSS
        response = client.post("/test-post", json={"content": "<script>alert('xss')</script>"})
        # Should be blocked by input validation middleware
        assert response.status_code == 400
