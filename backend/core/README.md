# Core Module

This directory contains the core configuration and utilities for the Claims Triage AI platform.

## Redis Integration

The Redis integration provides comprehensive caching, queue management, rate limiting, and session management capabilities.

## Vector Store Integration (ChromaDB)

The vector store integration provides RAG (Retrieval Augmented Generation) capabilities for decision support and knowledge base indexing.

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

**Usage:**
```python
from backend.core.redis import redis_health_check

# Check Redis health
health = await redis_health_check()
# Returns: {"status": "healthy", "version": "7.0.0", ...}
```

### API Endpoints

The Redis integration adds several new API endpoints:

#### Rate Limiting
- Automatically applied to all endpoints via middleware
- Configurable via `RATE_LIMIT_PER_MINUTE` setting

#### Queue Management
- `POST /api/v1/queue/jobs` - Enqueue background job
- `GET /api/v1/queue/status` - Get queue status

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
