# Backend Core Module

This module contains the core configuration and utilities for the Claims Triage AI platform.

## Components

### Configuration Management (`config.py`)
- Application settings with environment variable support
- Database, Redis, OPA, and Vector Store configuration
- Security and monitoring settings

### Logging (`logging.py`)
- Structured logging configuration
- Audit log setup
- Log rotation and formatting

### Monitoring & Observability

#### Telemetry (`telemetry.py`)
OpenTelemetry implementation for distributed tracing and metrics collection.

**Features:**
- Distributed tracing with spans and context propagation
- Metrics collection for business and technical metrics
- Log correlation with trace IDs
- Automatic instrumentation for FastAPI, SQLAlchemy, Redis, and HTTP clients

**Key Functions:**
```python
# Setup telemetry
setup_telemetry(
    service_name="claims-triage-ai",
    service_version="1.0.0",
    environment="development",
    otlp_endpoint=None,
    enable_console_export=True,
    enable_otlp_export=False
)

# Trace spans
with trace_span("operation_name", attributes={"key": "value"}) as span:
    # Your code here
    pass

# Record metrics
record_request_metric("GET", "/api/cases", 200, 1.5, success=True)
record_triage_metric("insurance", 2.5, success=True, risk_score=0.7)
record_agent_execution_metric("classifier", 1.0, success=True, confidence=0.9)

# Function decorator
@trace_function("function_name")
def my_function():
    return "result"
```

#### Prometheus (`prometheus.py`)
Prometheus metrics collection and exposure.

**Features:**
- Custom business metrics for triage operations
- Agent performance metrics
- System health metrics
- Integration with Prometheus client library

**Key Metrics:**
- `triage_requests_total`: Total number of triage requests
- `triage_duration_seconds`: Time spent processing triage requests
- `agent_executions_total`: Total number of agent executions
- `risk_scores`: Distribution of risk scores
- `confidence_scores`: Distribution of confidence scores
- `errors_total`: Total number of errors
- `active_requests`: Number of active requests

**Usage:**
```python
# Get metrics collector
collector = get_metrics_collector()

# Record metrics
collector.record_triage_request("insurance", "success", "normal", 1.5)
collector.record_agent_execution("classifier", "success", "insurance", 0.8, 0.9)

# Context managers for automatic tracking
with track_request("endpoint_name"):
    # Request processing
    pass

with track_agent_execution("classifier", "insurance"):
    # Agent execution
    pass

with track_triage_request("insurance", "high"):
    # Triage processing
    pass
```

#### Monitoring (`monitoring.py`)
High-level monitoring orchestration and health checks.

**Features:**
- Unified monitoring setup
- Application instrumentation
- Health status reporting
- System metrics updates

**Usage:**
```python
# Setup monitoring
setup_monitoring(
    enable_telemetry=True,
    enable_prometheus=True,
    prometheus_port=9090,
    environment="development"
)

# Instrument application
instrument_application(app, engine)

# Get health status
status = get_health_status()
```

### Authentication (`auth.py`)
- JWT token management
- Role-based access control
- User authentication utilities

### Redis Integration (`redis.py`)
- Redis client configuration
- Caching layer implementation
- Queue management for background jobs
- Rate limiting and session management

### Vector Store (`vector_store.py`)
- ChromaDB client configuration
- Embedding generation and storage
- RAG capabilities for knowledge base
- Document similarity search

### Background Jobs (`background_jobs.py`)
- Background job processor
- Queue management
- Job execution and monitoring

### OPA Integration (`opa.py`)
- Open Policy Agent client
- Policy management and evaluation
- Hot-reloading capabilities
- Access control and compliance policies

## API Endpoints

### Health Check
```
GET /health
```
Returns comprehensive health status including monitoring components.

### Prometheus Metrics
```
GET /metrics
```
Exposes Prometheus-formatted metrics for scraping.

## Monitoring Stack

### Prometheus Configuration
- **Location**: `monitoring/prometheus/prometheus.yml`
- **Port**: 9090
- **Scrape Targets**: Backend API, Redis, PostgreSQL
- **Recording Rules**: `monitoring/prometheus/recording_rules.yml`

### Grafana Configuration
- **Location**: `monitoring/grafana/`
- **Port**: 3001
- **Default Credentials**: admin/admin
- **Dashboards**: Auto-provisioned from `monitoring/grafana/dashboards/`

### Key Dashboards
1. **Overview Dashboard** (`overview.json`)
   - Request rates and success rates
   - Processing time distributions
   - Agent performance metrics
   - Error rates and system resources

## Makefile Commands

```bash
# Setup monitoring stack
make monitoring

# Test telemetry setup
make telemetry

# Open monitoring interfaces
make prometheus
make grafana
```

## Environment Variables

```bash
# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001

# Telemetry
OTLP_ENDPOINT=http://localhost:4317  # Optional OTLP endpoint
ENVIRONMENT=development
```

## Testing

Run observability tests:
```bash
cd backend
pytest tests/test_observability.py -v
```

## Integration

The observability components are automatically integrated into the main application:

1. **Startup**: Telemetry and Prometheus are initialized during app startup
2. **Instrumentation**: FastAPI, SQLAlchemy, Redis, and HTTP clients are automatically instrumented
3. **Metrics**: Business metrics are automatically collected during operations
4. **Health Checks**: Comprehensive health status is available via `/health` endpoint
5. **Monitoring**: Prometheus metrics are exposed via `/metrics` endpoint

## Performance Considerations

- **Sampling**: Configure trace sampling for high-volume environments
- **Metrics Cardinality**: Use appropriate labels to avoid high cardinality issues
- **Storage**: Configure retention policies for metrics and traces
- **Resource Usage**: Monitor the impact of observability on application performance

## Troubleshooting

### Common Issues

1. **Prometheus Connection Refused**
   - Check if Prometheus server is running on port 9090
   - Verify firewall settings

2. **Grafana Login Issues**
   - Default credentials: admin/admin
   - Check if Grafana is running on port 3001

3. **Metrics Not Appearing**
   - Verify Prometheus is scraping the `/metrics` endpoint
   - Check application logs for telemetry errors

4. **High Memory Usage**
   - Consider reducing metrics retention
   - Check for memory leaks in custom metrics

### Debug Commands

```bash
# Check monitoring status
curl http://localhost:8000/health

# View raw metrics
curl http://localhost:8000/metrics

# Test telemetry setup
make telemetry

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

## Security Features

### Security Middleware Stack

The platform implements a comprehensive security middleware stack:

1. **SecurityHeadersMiddleware**: Adds security headers to all responses
2. **RequestSizeMiddleware**: Enforces request size limits
3. **InputValidationMiddleware**: Validates and sanitizes input
4. **PIIDetectionMiddleware**: Detects and logs PII in requests/responses
5. **DataRetentionMiddleware**: Enforces data retention policies

### Security Testing

```bash
# Run security tests
make test-security

# Test specific security components
pytest backend/tests/test_security.py::TestSecurityHeadersMiddleware -v
pytest backend/tests/test_security.py::TestInputValidationMiddleware -v
pytest backend/tests/test_security.py::TestPIIDetectionMiddleware -v
```

### Security Configuration

Security settings are configured in `config.py`:

```python
# Security settings
pii_detection_enabled: bool = True
rate_limit_per_minute: int = 60
max_file_size: int = 10 * 1024 * 1024  # 10MB
audit_log_retention_days: int = 365
allowed_origins: List[str] = ["http://localhost:3000"]
```
