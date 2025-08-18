# Core Module

This directory contains the core configuration and utilities for the Claims Triage AI platform.

## Redis Integration

The Redis integration provides comprehensive caching, queue management, rate limiting, and session management capabilities.

## Vector Store Integration (ChromaDB)

The vector store integration provides RAG (Retrieval Augmented Generation) capabilities for decision support and knowledge base indexing.

## Open Policy Agent (OPA) Integration

The OPA integration provides policy-as-code capabilities for routing, compliance, access control, and data governance decisions.

### Features

#### 1. **Redis Client Configuration**
- Connection pooling with health checks
- Automatic reconnection and timeout handling
- Configurable via environment variables (`REDIS_URL`)

#### 2. **Caching Layer**
- Simple key-value caching with expiration
- JSON serialization for complex objects
- Error handling and logging

**Usage:**
```python
from backend.core.redis import cache_set_json, cache_get_json

# Cache data
await cache_set_json("user:123", {"name": "John", "role": "admin"}, expire=3600)

# Retrieve cached data
user_data = await cache_get_json("user:123")
```

#### 3. **Queue Management**
- Priority-based job queues using Redis sorted sets
- Job enqueueing and dequeuing with metadata
- Queue length monitoring

**Usage:**
```python
from backend.core.redis import enqueue_job, dequeue_job, get_queue_length

# Enqueue a job
await enqueue_job("background_jobs", {
    "type": "process_document",
    "document_id": "123",
    "priority": 1
})

# Dequeue a job
job = await dequeue_job("background_jobs")

# Check queue length
length = await get_queue_length("background_jobs")
```

#### 4. **Rate Limiting**
- Per-IP rate limiting with configurable limits
- Sliding window implementation
- Middleware integration

**Usage:**
```python
from backend.core.redis import check_rate_limit

# Check if rate limit is exceeded
allowed = await check_rate_limit("rate_limit:192.168.1.1", limit=60, window=60)
```

#### 5. **Session Management**
- User session storage with expiration
- Session data serialization
- Clean session cleanup

**Usage:**
```python
from backend.core.redis import set_session, get_session, delete_session

# Set session
await set_session("session:abc123", {"user_id": "123", "role": "admin"}, expire=1800)

# Get session
session_data = await get_session("session:abc123")

# Delete session
await delete_session("session:abc123")
```

#### 6. **Health Monitoring**
- Redis health check endpoint
- Connection status monitoring
- Performance metrics collection
- Cache statistics and management

**Usage:**
```python
from backend.core.redis import redis_health_check, get_cache_stats

# Check Redis health
health = await redis_health_check()
# Returns: {"status": "healthy", "version": "7.0.0", ...}

# Get cache statistics
stats = await get_cache_stats()
# Returns: {"total_keys": 100, "used_memory": "1.2MB", ...}
```

#### 7. **Cache Decorator**
- Automatic function result caching
- Configurable expiration and key prefixes
- Transparent cache integration

**Usage:**
```python
from backend.core.redis import cache_result

@cache_result(expire=3600, key_prefix="analytics")
async def get_analytics_data(date_range: str):
    # Expensive computation here
    return {"data": "analytics_result"}

# Result is automatically cached for 1 hour
```

#### 8. **Idempotency Keys**
- Prevent duplicate request processing
- Configurable expiration times
- Automatic key management

**Usage:**
```python
from backend.core.redis import set_idempotency_key, check_idempotency_key

# Set idempotency key
success = await set_idempotency_key("request:123", expire=300)

# Check if key exists
exists = await check_idempotency_key("request:123")
```

#### 9. **Cache Management**
- Pattern-based cache clearing
- Cache statistics and monitoring
- Bulk cache operations

**Usage:**
```python
from backend.core.redis import clear_cache_pattern

# Clear all cache entries matching pattern
await clear_cache_pattern("user:*")

# Clear specific cache entries
await clear_cache_pattern("case:123:*")
```

### API Endpoints

The Redis integration adds several new API endpoints:

#### Rate Limiting
- Automatically applied to all endpoints via middleware
- Configurable via `RATE_LIMIT_PER_MINUTE` setting

#### Queue Management
- `POST /api/v1/queue/jobs` - Enqueue background job
- `GET /api/v1/queue/status` - Get queue status

#### Cache Management
- `GET /api/v1/cache/stats` - Get cache statistics
- `DELETE /api/v1/cache/clear` - Clear cache entries
- `POST /api/v1/cache/idempotency` - Set idempotency key

#### Health Check
- `GET /health` - Includes Redis health status

### Configuration

Redis configuration is handled via environment variables:

```bash
# Redis connection URL
REDIS_URL=redis://localhost:6379

# Rate limiting
RATE_LIMIT_PER_MINUTE=60
```

### Error Handling

All Redis operations include comprehensive error handling:
- Connection failures are logged but don't crash the application
- Cache misses are handled gracefully
- Queue operations include retry logic
- Rate limiting falls back to allowing requests if Redis is down

### Performance Considerations

- Connection pooling reduces connection overhead
- JSON serialization is optimized for common data types
- Cache expiration prevents memory bloat
- Priority queues ensure important jobs are processed first

### Vector Store Features

#### 1. **ChromaDB Client Configuration**
- Persistent storage with automatic backups
- Embedding model management (all-MiniLM-L6-v2)
- Collection management for different data types
- Health monitoring and status checks

#### 2. **Knowledge Base Management**
- Add and search knowledge base entries
- Category-based filtering and organization
- Similarity-based retrieval with configurable thresholds
- Metadata enrichment and tagging

**Usage:**
```python
from backend.core.vector_store import add_knowledge_base_entry, search_knowledge_base

# Add knowledge base entry
entry_id = await add_knowledge_base_entry(
    content="Auto insurance claims require police reports...",
    metadata={"domain": "insurance", "category": "auto_claims"},
    category="auto_claims"
)

# Search knowledge base
results = await search_knowledge_base(
    query="What documents are needed for auto claims?",
    n_results=5,
    category="auto_claims"
)
```

#### 3. **Document Embedding and Similarity Search**
- Document embedding generation and storage
- Similarity-based document retrieval
- Metadata preservation and search
- Configurable similarity thresholds

**Usage:**
```python
from backend.core.vector_store import add_document_embedding, find_similar_documents

# Add document embedding
doc_id = await add_document_embedding(
    document_id="doc_123",
    content="Claim document content...",
    metadata={"case_id": "case_456", "document_type": "police_report"}
)

# Find similar documents
similar_docs = await find_similar_documents(
    content="Similar claim document...",
    n_results=5,
    threshold=0.7
)
```

#### 4. **Policy and SOP Management**
- Policy document storage and retrieval
- Standard Operating Procedure management
- Version control and metadata tracking
- Category-based organization

**Usage:**
```python
from backend.core.vector_store import add_policy, add_sop, search_policies, search_sops

# Add policy
policy_id = await add_policy(
    policy_name="Fraud Detection Policy",
    content="All claims over $10,000 require...",
    metadata={"policy_type": "fraud", "version": "1.0"}
)

# Add SOP
sop_id = await add_sop(
    sop_name="Claim Intake Procedure",
    content="1. Verify claimant identity...",
    metadata={"sop_type": "intake", "version": "1.0"}
)
```

#### 5. **Decision Support System**
- Multi-source knowledge retrieval
- Context-aware decision recommendations
- Policy and procedure integration
- Confidence scoring and ranking

**Usage:**
```python
from backend.core.vector_store import get_decision_support

# Get decision support
support_info = await get_decision_support(
    case_context="Auto accident claim with $15,000 in damages",
    decision_type="fraud_assessment",
    n_results=3
)
```

### Vector Store API Endpoints

The vector store integration adds several new API endpoints:

#### Knowledge Base Management
- `POST /api/v1/vector-store/knowledge-base` - Add knowledge base entry
- `GET /api/v1/vector-store/knowledge-base/search` - Search knowledge base

#### Document Management
- `POST /api/v1/vector-store/documents` - Add document embedding
- `GET /api/v1/vector-store/documents/similar` - Find similar documents

#### Decision Support
- `POST /api/v1/vector-store/decision-support` - Get decision support information

### Vector Store Configuration

ChromaDB configuration is handled via environment variables:

```bash
# ChromaDB settings (optional - uses defaults)
CHROMA_DB_PATH=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Vector Store Error Handling

All vector store operations include comprehensive error handling:
- Connection failures are logged but don't crash the application
- Embedding generation failures are handled gracefully
- Search operations include fallback mechanisms
- Health checks provide detailed status information

### Vector Store Performance Considerations

- Embedding model is loaded once and reused
- Collections are optimized for different data types
- Similarity thresholds prevent irrelevant results
- Metadata filtering improves search performance
- Persistent storage ensures data durability

### OPA Features

#### 1. **OPA Client Configuration**
- HTTP client for OPA server communication
- Connection pooling and timeout handling
- Health monitoring and status checks
- Configurable via environment variables (`OPA_BASE_URL`, `OPA_TIMEOUT`)

#### 2. **Policy Engine Integration**
- Routing policy evaluation for case assignment
- Compliance policy validation for case processing
- Access control policy enforcement
- Data governance policy management

**Usage:**
```python
from backend.core.opa import evaluate_routing_policy, evaluate_compliance_policy

# Evaluate routing policy
routing_result = await evaluate_routing_policy({
    "case_type": "auto_insurance",
    "risk_level": "high",
    "urgency_level": "normal"
})

# Evaluate compliance policy
compliance_result = await evaluate_compliance_policy({
    "title": "Case Title",
    "description": "Case description",
    "case_type": "health_insurance"
})
```

#### 3. **Policy Management**
- Policy creation, update, and deletion
- Policy validation and syntax checking
- Policy hot-reloading with file watcher
- Policy versioning and metadata tracking

**Usage:**
```python
from backend.core.opa import create_policy, update_policy, delete_policy, list_policies

# Create new policy
result = await create_policy("custom_routing", """
package custom_routing

default allow = false

allow {
    input.case.risk_level == "low"
    input.case.urgency_level == "normal"
}
""")

# List all policies
policies = await list_policies()

# Update policy
await update_policy("custom_routing", updated_policy_content)

# Delete policy
await delete_policy("custom_routing")
```

#### 4. **Policy Hot-Reloading**
- Automatic policy file monitoring
- Real-time policy updates without restart
- File change detection and validation
- Error handling and rollback capabilities

#### 5. **Default Policies**
- **Routing Policy**: Case assignment based on type, risk, and urgency
- **Compliance Policy**: Data validation and regulatory compliance
- **Access Control Policy**: Role-based and team-based access control
- **Data Governance Policy**: Data operations and retention rules

#### 6. **Policy Validation**
- Rego syntax validation
- Policy structure verification
- OPA server validation
- Error reporting and debugging

**Usage:**
```python
from backend.core.opa import validate_policy

# Validate policy syntax
validation_result = await validate_policy(policy_content)
if validation_result["success"]:
    print("Policy is valid")
else:
    print(f"Policy validation failed: {validation_result['error']}")
```

### OPA API Endpoints

The OPA integration adds several new API endpoints:

#### Policy Evaluation
- `POST /api/v1/policies/routing/evaluate` - Evaluate routing policy
- `POST /api/v1/policies/compliance/evaluate` - Evaluate compliance policy
- `POST /api/v1/policies/access-control/evaluate` - Evaluate access control policy
- `POST /api/v1/policies/data-governance/evaluate` - Evaluate data governance policy

#### Policy Management
- `POST /api/v1/policies` - Create new policy
- `PUT /api/v1/policies/{policy_name}` - Update existing policy
- `DELETE /api/v1/policies/{policy_name}` - Delete policy
- `GET /api/v1/policies` - List all policies
- `POST /api/v1/policies/validate` - Validate policy syntax

### OPA Configuration

OPA configuration is handled via environment variables:

```bash
# OPA server settings
OPA_BASE_URL=http://localhost:8181
OPA_TIMEOUT=30
OPA_POLICIES_PATH=./policies
```

### OPA Error Handling

All OPA operations include comprehensive error handling:
- Connection failures are logged but don't crash the application
- Policy evaluation failures are handled gracefully
- Policy validation includes detailed error messages
- Health checks provide detailed status information

### OPA Performance Considerations

- HTTP connection pooling reduces overhead
- Policy caching improves evaluation performance
- Hot-reloading minimizes downtime
- Validation prevents invalid policies from being loaded
- Health monitoring ensures system reliability
