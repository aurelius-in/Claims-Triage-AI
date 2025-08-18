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
from .monitoring import setup_monitoring, instrument_application, shutdown_monitoring, get_health_status
from .telemetry import (
    setup_telemetry, instrument_fastapi, instrument_sqlalchemy, instrument_redis, 
    instrument_httpx, instrument_logging, shutdown_telemetry, trace_span, 
    record_request_metric, record_triage_metric, record_agent_execution_metric,
    get_current_trace_id, get_current_span_id, add_span_event, set_span_attribute,
    trace_function
)
from .prometheus import (
    start_prometheus_server, get_metrics, get_metrics_content_type,
    get_metrics_collector, track_request, track_agent_execution, track_triage_request,
    update_system_metrics, reset_metrics, track_metrics
)
from .auth import get_current_user, create_access_token
from .redis import (
    get_redis_client, init_redis, close_redis,
    cache_get, cache_set, cache_delete, cache_get_json, cache_set_json,
    enqueue_job, dequeue_job, get_queue_length,
    check_rate_limit, set_session, get_session, delete_session,
    redis_health_check, cache_result, clear_cache_pattern, get_cache_stats,
    set_idempotency_key, check_idempotency_key
)

from .background_jobs import (
    start_background_processor,
    stop_background_processor,
    enqueue_document_processing,
    enqueue_notification,
    enqueue_report_generation,
    enqueue_analytics_update,
    enqueue_cleanup
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

from .opa import (
    init_opa,
    close_opa,
    opa_health_check,
    evaluate_routing_policy,
    evaluate_compliance_policy,
    evaluate_access_control_policy,
    evaluate_data_governance_policy,
    create_policy,
    update_policy,
    delete_policy,
    list_policies,
    validate_policy
)

__all__ = [
    "Settings",
    "get_settings", 
    "setup_logging",
    "setup_monitoring",
    "instrument_application",
    "shutdown_monitoring",
    "get_health_status",
    # Telemetry exports
    "setup_telemetry",
    "instrument_fastapi",
    "instrument_sqlalchemy",
    "instrument_redis",
    "instrument_httpx",
    "instrument_logging",
    "shutdown_telemetry",
    "trace_span",
    "record_request_metric",
    "record_triage_metric",
    "record_agent_execution_metric",
    "get_current_trace_id",
    "get_current_span_id",
    "add_span_event",
    "set_span_attribute",
    "trace_function",
    # Prometheus exports
    "start_prometheus_server",
    "get_metrics",
    "get_metrics_content_type",
    "get_metrics_collector",
    "track_request",
    "track_agent_execution",
    "track_triage_request",
    "update_system_metrics",
    "reset_metrics",
    "track_metrics",
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
    "cache_result",
    "clear_cache_pattern",
    "get_cache_stats",
    "set_idempotency_key",
    "check_idempotency_key",
    # Background job exports
    "start_background_processor",
    "stop_background_processor",
    "enqueue_document_processing",
    "enqueue_notification",
    "enqueue_report_generation",
    "enqueue_analytics_update",
    "enqueue_cleanup",
    # Vector store exports
    "init_vector_store",
    "close_vector_store",
    "vector_store_health_check",
    "add_knowledge_base_entry",
    "search_knowledge_base",
    "add_document_embedding",
    "find_similar_documents",
    "get_decision_support",
    # OPA exports
    "init_opa",
    "close_opa",
    "opa_health_check",
    "evaluate_routing_policy",
    "evaluate_compliance_policy",
    "evaluate_access_control_policy",
    "evaluate_data_governance_policy",
    "create_policy",
    "update_policy",
    "delete_policy",
    "list_policies",
    "validate_policy"
]
