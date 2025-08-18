# Database Layer

This directory contains the database layer implementation for the Claims Triage AI platform.

## Overview

The database layer provides:
- **SQLAlchemy ORM models** for all entities (cases, users, teams, documents, audit logs, etc.)
- **Repository pattern** for clean data access
- **Alembic migrations** for database schema management
- **Async database operations** with PostgreSQL
- **Test database support** with SQLite

## Structure

```
data/
├── __init__.py          # Package exports
├── models.py            # SQLAlchemy ORM models
├── schemas.py           # Pydantic schemas for API
├── database.py          # Database configuration and connection
├── repository.py        # Repository pattern implementation
├── migrations/          # Alembic migrations
│   ├── env.py          # Migration environment
│   └── versions/       # Migration scripts
└── README.md           # This file
```

## Models

### Core Entities

- **Case**: Main triage cases with metadata, status, and assignments
- **User**: System users with roles and team assignments
- **Team**: Teams that handle cases with capacity and SLA targets
- **Document**: Case attachments with processing metadata
- **AuditLog**: Compliance audit trail with hash chain integrity
- **TriageResult**: Agent outputs and orchestration metadata
- **AnalyticsSnapshot**: Aggregated metrics for reporting

### Key Features

- **UUID primary keys** for security and scalability
- **Enum types** for status, roles, and categories
- **JSON fields** for flexible metadata storage
- **Timestamps** for audit and tracking
- **Foreign key relationships** with proper indexing
- **Soft deletes** support via status fields

## Repository Pattern

Each entity has a dedicated repository class with async CRUD operations:

```python
# Example usage
case_repo = CaseRepository(db_session)
case = await case_repo.create_case(case_data)
cases = await case_repo.list_cases(status=CaseStatus.PENDING)
```

### Repository Features

- **Async operations** for better performance
- **Filtering and pagination** support
- **Transaction management** with rollback on errors
- **Relationship loading** with selectinload
- **Audit logging** integration

## Database Configuration

### Environment Variables

```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
DATABASE_ECHO=false  # SQL query logging
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

### Connection Management

- **Connection pooling** for efficient resource usage
- **Pre-ping** to verify connections before use
- **Auto-recycle** connections every hour
- **Async context managers** for proper cleanup

## Migrations

### Alembic Setup

```bash
# Initialize migrations
alembic init migrations

# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Migration Features

- **Auto-generation** from model changes
- **Version control** for schema changes
- **Rollback support** for safe deployments
- **Environment-specific** configurations

## Testing

### Test Database

- **SQLite in-memory** for fast tests
- **Isolated sessions** per test
- **Auto-cleanup** after tests
- **Fixture support** for common setup

### Test Examples

```python
@pytest.mark.asyncio
async def test_create_case(db_session, setup_db):
    case_repo = CaseRepository(db_session)
    case = await case_repo.create_case(case_data)
    assert case.id is not None
```

## Usage Examples

### Creating a Case

```python
from backend.data.repository import CaseRepository
from backend.data.schemas import CaseCreate

case_data = CaseCreate(
    external_id="CLAIM-001",
    case_type=CaseType.AUTO_INSURANCE,
    title="Auto Accident Claim",
    description="Vehicle damage from collision",
    urgency_level=UrgencyLevel.HIGH,
    risk_level=RiskLevel.MEDIUM,
    risk_score=0.7
)

case_repo = CaseRepository(db_session)
case = await case_repo.create_case(case_data)
await db_session.commit()
```

### Listing Cases with Filters

```python
cases = await case_repo.list_cases(
    status=CaseStatus.PENDING,
    case_type=CaseType.AUTO_INSURANCE,
    urgency_level=UrgencyLevel.HIGH,
    skip=0,
    limit=50
)
```

### Updating a Case

```python
case_update = CaseUpdate(
    status=CaseStatus.IN_PROGRESS,
    assigned_team_id=team_id,
    priority_score=0.8
)

updated_case = await case_repo.update_case(case_id, case_update)
```

## Performance Considerations

### Indexing

- **Primary keys** are automatically indexed
- **Foreign keys** have indexes for joins
- **Composite indexes** for common query patterns
- **JSON indexes** for metadata queries

### Query Optimization

- **Selective loading** with selectinload
- **Pagination** to limit result sets
- **Filtering** to reduce data transfer
- **Connection pooling** for reuse

## Security

### Data Protection

- **UUID primary keys** prevent enumeration
- **Audit logging** for compliance
- **Hash chain integrity** for audit logs
- **Role-based access** control

### SQL Injection Prevention

- **Parameterized queries** via SQLAlchemy
- **Input validation** with Pydantic
- **Type safety** with enums
- **Escaping** of user inputs

## Monitoring

### Health Checks

```python
# Database health check
async def check_db_health():
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
```

### Metrics

- **Connection pool** utilization
- **Query performance** monitoring
- **Error rates** tracking
- **Transaction** metrics

## Troubleshooting

### Common Issues

1. **Connection timeouts**: Increase pool size or timeout values
2. **Migration conflicts**: Check for conflicting schema changes
3. **Performance issues**: Review indexes and query patterns
4. **Memory leaks**: Ensure proper session cleanup

### Debug Mode

```python
# Enable SQL query logging
DATABASE_ECHO=true

# Enable detailed error messages
DEBUG=true
```

## Future Enhancements

- **Read replicas** for scaling reads
- **Sharding** for horizontal scaling
- **Caching layer** with Redis
- **Event sourcing** for audit trails
- **GraphQL** support for flexible queries
