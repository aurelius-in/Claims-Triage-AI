"""
Core configuration and utilities for the Claims Triage AI platform.

This module contains:
- Configuration management
- Logging setup
- Monitoring and telemetry
- Authentication and authorization
- Database connections
- Redis client and caching
"""

from .config import Settings, get_settings
from .logging import setup_logging
from .monitoring import setup_monitoring
from .auth import get_current_user, create_access_token
from .redis import (
    get_redis_client, init_redis, close_redis,
    cache_get, cache_set, cache_delete, cache_get_json, cache_set_json,
    enqueue_job, dequeue_job, get_queue_length,
    check_rate_limit, set_session, get_session, delete_session,
    redis_health_check
)

from .vector_store import (
    init_vector_store,
    close_vector_store,
    vector_store_health_check,
    add_knowledge_base_entry,
    search_knowledge_base,
    add_document_embedding,
    find_similar_documents,
    get_decision_support
)

__all__ = [
    "Settings",
    "get_settings", 
    "setup_logging",
    "setup_monitoring",
    "get_current_user",
    "create_access_token",
    # Redis exports
    "get_redis_client",
    "init_redis", 
    "close_redis",
    "cache_get",
    "cache_set", 
    "cache_delete",
    "cache_get_json",
    "cache_set_json",
    "enqueue_job",
    "dequeue_job",
    "get_queue_length", 
    "check_rate_limit",
    "set_session",
    "get_session",
    "delete_session",
    "redis_health_check",
    # Vector store exports
    "init_vector_store",
    "close_vector_store",
    "vector_store_health_check",
    "add_knowledge_base_entry",
    "search_knowledge_base",
    "add_document_embedding",
    "find_similar_documents",
    "get_decision_support"
]
