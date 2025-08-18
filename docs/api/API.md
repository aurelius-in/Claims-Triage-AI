# Claims Triage AI - API Documentation

## Overview

The Claims Triage AI API is a RESTful service built with FastAPI that provides comprehensive case triage functionality. The API follows OpenAPI 3.0 specification and includes automatic documentation generation.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.claimstriage.ai`

## Authentication

All API endpoints require authentication using JWT tokens.

### Authentication Flow

1. **Register/Login**: Obtain access token
2. **Include Token**: Add to request headers
3. **Token Refresh**: Use refresh token when needed

### Headers

```http
Authorization: Bearer <your-jwt-token>
Content-Type: application/json
```

## API Endpoints

### Authentication Endpoints

#### POST /api/v1/auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "agent|manager|admin"
}
```

**Response:**
```json
{
  "user_id": "uuid",
  "username": "string",
  "email": "string",
  "role": "string",
  "created_at": "datetime"
}
```

#### POST /api/v1/auth/login
Authenticate user and obtain access token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "string"
}
```

#### GET /api/v1/auth/me
Get current user information.

**Response:**
```json
{
  "user_id": "uuid",
  "username": "string",
  "email": "string",
  "role": "string",
  "permissions": ["string"]
}
```

### Case Management Endpoints

#### POST /api/v1/cases/
Create a new case.

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "case_type": "auto_insurance|health_insurance|property_insurance|credit_dispute|legal_case",
  "urgency_level": "low|medium|high|critical",
  "risk_level": "low|medium|high",
  "amount": 0.0,
  "metadata": {
    "additional_fields": "value"
  }
}
```

**Response:**
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "case_type": "string",
  "urgency_level": "string",
  "risk_level": "string",
  "status": "new|in_progress|completed|closed",
  "amount": 0.0,
  "created_at": "datetime",
  "updated_at": "datetime",
  "metadata": {}
}
```

#### GET /api/v1/cases/
List cases with filtering and pagination.

**Query Parameters:**
- `page`: Page number (default: 1)
- `size`: Page size (default: 10)
- `case_type`: Filter by case type
- `status`: Filter by status
- `urgency_level`: Filter by urgency
- `risk_level`: Filter by risk level
- `created_after`: Filter by creation date
- `created_before`: Filter by creation date

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "string",
      "case_type": "string",
      "status": "string",
      "urgency_level": "string",
      "risk_level": "string",
      "created_at": "datetime"
    }
  ],
  "total": 100,
  "page": 1,
  "size": 10,
  "pages": 10
}
```

#### GET /api/v1/cases/{case_id}
Get specific case details.

**Response:**
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "case_type": "string",
  "urgency_level": "string",
  "risk_level": "string",
  "status": "string",
  "amount": 0.0,
  "created_at": "datetime",
  "updated_at": "datetime",
  "metadata": {},
  "triage_history": [
    {
      "triage_id": "uuid",
      "created_at": "datetime",
      "results": {}
    }
  ]
}
```

#### PUT /api/v1/cases/{case_id}
Update case information.

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "status": "string",
  "metadata": {}
}
```

#### DELETE /api/v1/cases/{case_id}
Delete a case (soft delete).

### Triage Endpoints

#### POST /api/v1/triage/run
Run triage pipeline on a case.

**Request Body:**
```json
{
  "case_id": "uuid",
  "force_reprocess": false,
  "documents": [
    {
      "filename": "string",
      "document_type": "string",
      "extracted_text": "string",
      "extracted_metadata": {}
    }
  ]
}
```

**Response:**
```json
{
  "triage_id": "uuid",
  "case_id": "uuid",
  "status": "completed|failed|in_progress",
  "results": {
    "classification": {
      "case_type": "string",
      "urgency_level": "string",
      "confidence": 0.95
    },
    "risk_assessment": {
      "risk_score": 0.75,
      "risk_level": "string",
      "top_features": ["string"]
    },
    "routing": {
      "recommended_team": "string",
      "sla_hours": 24,
      "escalation_flag": false
    },
    "decision_support": {
      "suggested_actions": ["string"],
      "template_response": "string",
      "checklist": ["string"]
    },
    "compliance": {
      "pii_detected": false,
      "compliance_issues": ["string"],
      "audit_log": {}
    }
  },
  "processing_time_ms": 1250,
  "created_at": "datetime"
}
```

#### GET /api/v1/triage/history/{case_id}
Get triage history for a case.

**Response:**
```json
{
  "case_id": "uuid",
  "triage_runs": [
    {
      "triage_id": "uuid",
      "status": "string",
      "results": {},
      "processing_time_ms": 1250,
      "created_at": "datetime"
    }
  ]
}
```

#### GET /api/v1/triage/metrics
Get triage performance metrics.

**Response:**
```json
{
  "total_runs": 1000,
  "average_execution_time": 1200,
  "success_rate": 0.98,
  "classification_distribution": {
    "auto_insurance": 300,
    "health_insurance": 250,
    "property_insurance": 200,
    "credit_dispute": 150,
    "legal_case": 100
  },
  "risk_distribution": {
    "low": 400,
    "medium": 350,
    "high": 250
  }
}
```

### Analytics Endpoints

#### GET /api/v1/analytics/case-volume
Get case volume analytics.

**Query Parameters:**
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `case_type`: Filter by case type

**Response:**
```json
{
  "total_cases": 1500,
  "cases_by_type": {
    "auto_insurance": 500,
    "health_insurance": 400,
    "property_insurance": 300,
    "credit_dispute": 200,
    "legal_case": 100
  },
  "cases_by_status": {
    "new": 600,
    "in_progress": 450,
    "completed": 450
  },
  "cases_by_urgency": {
    "low": 500,
    "medium": 600,
    "high": 300,
    "critical": 100
  },
  "trends": {
    "daily": [
      {
        "date": "2024-01-01",
        "count": 50
      }
    ],
    "weekly": [],
    "monthly": []
  }
}
```

#### GET /api/v1/analytics/sla
Get SLA performance analytics.

**Response:**
```json
{
  "sla_adherence_rate": 0.85,
  "average_resolution_time": 48,
  "sla_violations": 75,
  "team_performance": [
    {
      "team": "string",
      "cases_handled": 100,
      "average_resolution_time": 36,
      "sla_adherence_rate": 0.90
    }
  ]
}
```

#### GET /api/v1/analytics/accuracy
Get model accuracy analytics.

**Response:**
```json
{
  "classification_accuracy": 0.92,
  "risk_prediction_accuracy": 0.88,
  "routing_accuracy": 0.95,
  "overrides": {
    "total_overrides": 50,
    "override_rate": 0.05,
    "override_reasons": {
      "manual_review": 30,
      "policy_change": 15,
      "system_error": 5
    }
  }
}
```

### Audit Endpoints

#### GET /api/v1/audit/logs
Get audit logs with filtering.

**Query Parameters:**
- `page`: Page number
- `size`: Page size
- `action`: Filter by action
- `resource_type`: Filter by resource type
- `user_id`: Filter by user
- `start_date`: Start date
- `end_date`: End date

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "action": "string",
      "resource_type": "string",
      "resource_id": "string",
      "details": {},
      "ip_address": "string",
      "user_agent": "string",
      "timestamp": "datetime"
    }
  ],
  "total": 1000,
  "page": 1,
  "size": 10
}
```

#### GET /api/v1/audit/case/{case_id}
Get audit trail for specific case.

**Response:**
```json
{
  "case_id": "uuid",
  "audit_entries": [
    {
      "id": "uuid",
      "action": "string",
      "user_id": "uuid",
      "details": {},
      "timestamp": "datetime"
    }
  ]
}
```

#### GET /api/v1/audit/export
Export audit logs.

**Query Parameters:**
- `format`: csv|json|pdf
- `start_date`: Start date
- `end_date`: End date

### Health & Monitoring Endpoints

#### GET /health
Basic health check.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "datetime",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "opa": "healthy",
    "chroma": "healthy"
  }
}
```

#### GET /metrics
Prometheus metrics endpoint.

**Response:**
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/health"} 150
```

#### GET /ready
Readiness check.

**Response:**
```json
{
  "status": "ready",
  "timestamp": "datetime"
}
```

#### GET /live
Liveness check.

**Response:**
```json
{
  "status": "alive",
  "timestamp": "datetime"
}
```

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "datetime",
  "request_id": "uuid"
}
```

### Common Error Codes

- `400`: Bad Request - Invalid input data
- `401`: Unauthorized - Authentication required
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `422`: Validation Error - Data validation failed
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - Server error

## Rate Limiting

API requests are rate-limited to prevent abuse:

- **Authenticated Users**: 1000 requests per hour
- **Unauthenticated**: 100 requests per hour
- **Bulk Operations**: 100 requests per hour

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination with the following parameters:

- `page`: Page number (1-based)
- `size`: Number of items per page (max 100)

Response includes pagination metadata:

```json
{
  "items": [],
  "total": 1000,
  "page": 1,
  "size": 10,
  "pages": 100
}
```

## WebSocket Support

Real-time updates are available via WebSocket connections:

### WebSocket Endpoint

```
ws://localhost:8000/ws
```

### Message Types

#### Subscribe to Updates
```json
{
  "type": "subscribe",
  "channel": "cases|triage|analytics"
}
```

#### Case Update
```json
{
  "type": "case_update",
  "case_id": "uuid",
  "data": {}
}
```

#### Triage Result
```json
{
  "type": "triage_result",
  "triage_id": "uuid",
  "data": {}
}
```

## SDKs and Libraries

### Python SDK
```python
from claims_triage import ClaimsTriageClient

client = ClaimsTriageClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Create a case
case = client.cases.create(
    title="Test Case",
    description="Test description",
    case_type="auto_insurance"
)

# Run triage
result = client.triage.run(case_id=case.id)
```

### JavaScript SDK
```javascript
import { ClaimsTriageClient } from '@claimstriage/sdk';

const client = new ClaimsTriageClient({
  baseUrl: 'http://localhost:8000',
  apiKey: 'your-api-key'
});

// Create a case
const case = await client.cases.create({
  title: 'Test Case',
  description: 'Test description',
  caseType: 'auto_insurance'
});

// Run triage
const result = await client.triage.run(case.id);
```

## OpenAPI Documentation

Interactive API documentation is available at:

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`

## Support

For API support and questions:

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/Claims-Triage-AI/issues)
- **Email**: api-support@claimstriage.ai