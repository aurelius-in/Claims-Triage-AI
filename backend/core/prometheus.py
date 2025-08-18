"""
Prometheus metrics for the Claims Triage AI platform.

This module provides:
- Custom business metrics for triage operations
- Agent performance metrics
- System health metrics
- Integration with Prometheus client library
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from contextlib import contextmanager

from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info,
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, multiprocess, start_http_server
)

logger = logging.getLogger(__name__)

# Create a custom registry for multiprocess support
registry = CollectorRegistry()

# Business Metrics
TRIAGE_REQUESTS_TOTAL = Counter(
    'triage_requests_total',
    'Total number of triage requests',
    ['case_type', 'status', 'priority'],
    registry=registry
)

TRIAGE_DURATION_SECONDS = Histogram(
    'triage_duration_seconds',
    'Time spent processing triage requests',
    ['case_type', 'status'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
    registry=registry
)

AGENT_EXECUTIONS_TOTAL = Counter(
    'agent_executions_total',
    'Total number of agent executions',
    ['agent_name', 'status', 'case_type'],
    registry=registry
)

AGENT_EXECUTION_DURATION_SECONDS = Histogram(
    'agent_execution_duration_seconds',
    'Time spent executing agents',
    ['agent_name', 'status'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
    registry=registry
)

RISK_SCORES = Histogram(
    'risk_scores',
    'Distribution of risk scores',
    ['case_type', 'risk_level'],
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    registry=registry
)

CONFIDENCE_SCORES = Histogram(
    'confidence_scores',
    'Distribution of confidence scores',
    ['agent_name', 'case_type'],
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    registry=registry
)

# System Metrics
ACTIVE_REQUESTS = Gauge(
    'active_requests',
    'Number of active requests being processed',
    ['endpoint'],
    registry=registry
)

QUEUE_SIZE = Gauge(
    'queue_size',
    'Number of items in processing queues',
    ['queue_name'],
    registry=registry
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections',
    'Number of active database connections',
    ['database'],
    registry=registry
)

REDIS_CONNECTIONS = Gauge(
    'redis_connections',
    'Number of active Redis connections',
    ['redis_instance'],
    registry=registry
)

# Error Metrics
ERRORS_TOTAL = Counter(
    'errors_total',
    'Total number of errors',
    ['error_type', 'component', 'severity'],
    registry=registry
)

# Performance Metrics
MEMORY_USAGE_BYTES = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes',
    ['component'],
    registry=registry
)

CPU_USAGE_PERCENT = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage',
    ['component'],
    registry=registry
)

# Business KPIs
CASES_PROCESSED_TODAY = Counter(
    'cases_processed_today',
    'Number of cases processed today',
    ['case_type', 'status'],
    registry=registry
)

SLA_VIOLATIONS = Counter(
    'sla_violations',
    'Number of SLA violations',
    ['case_type', 'sla_type'],
    registry=registry
)

AVERAGE_PROCESSING_TIME = Summary(
    'average_processing_time_seconds',
    'Average processing time for cases',
    ['case_type'],
    registry=registry
)

# Application Info
APP_INFO = Info(
    'claims_triage_ai',
    'Claims Triage AI application information',
    registry=registry
)


class MetricsCollector:
    """Collector for custom business metrics."""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self._setup_app_info()
    
    def _setup_app_info(self):
        """Setup application information."""
        APP_INFO.info({
            'version': '1.0.0',
            'environment': 'development',
            'start_time': self.start_time.isoformat()
        })
    
    def record_triage_request(
        self,
        case_type: str,
        status: str = "success",
        priority: str = "normal",
        duration: Optional[float] = None
    ):
        """Record a triage request."""
        TRIAGE_REQUESTS_TOTAL.labels(
            case_type=case_type,
            status=status,
            priority=priority
        ).inc()
        
        if duration is not None:
            TRIAGE_DURATION_SECONDS.labels(
                case_type=case_type,
                status=status
            ).observe(duration)
    
    def record_agent_execution(
        self,
        agent_name: str,
        status: str = "success",
        case_type: str = "unknown",
        duration: Optional[float] = None,
        confidence: Optional[float] = None
    ):
        """Record an agent execution."""
        AGENT_EXECUTIONS_TOTAL.labels(
            agent_name=agent_name,
            status=status,
            case_type=case_type
        ).inc()
        
        if duration is not None:
            AGENT_EXECUTION_DURATION_SECONDS.labels(
                agent_name=agent_name,
                status=status
            ).observe(duration)
        
        if confidence is not None:
            CONFIDENCE_SCORES.labels(
                agent_name=agent_name,
                case_type=case_type
            ).observe(confidence)
    
    def record_risk_score(
        self,
        risk_score: float,
        case_type: str = "unknown",
        risk_level: str = "medium"
    ):
        """Record a risk score."""
        RISK_SCORES.labels(
            case_type=case_type,
            risk_level=risk_level
        ).observe(risk_score)
    
    def record_error(
        self,
        error_type: str,
        component: str = "unknown",
        severity: str = "error"
    ):
        """Record an error."""
        ERRORS_TOTAL.labels(
            error_type=error_type,
            component=component,
            severity=severity
        ).inc()
    
    def set_active_requests(self, count: int, endpoint: str = "unknown"):
        """Set the number of active requests."""
        ACTIVE_REQUESTS.labels(endpoint=endpoint).set(count)
    
    def set_queue_size(self, size: int, queue_name: str):
        """Set the queue size."""
        QUEUE_SIZE.labels(queue_name=queue_name).set(size)
    
    def set_database_connections(self, count: int, database: str = "postgres"):
        """Set the number of database connections."""
        DATABASE_CONNECTIONS.labels(database=database).set(count)
    
    def set_redis_connections(self, count: int, redis_instance: str = "default"):
        """Set the number of Redis connections."""
        REDIS_CONNECTIONS.labels(redis_instance=redis_instance).set(count)
    
    def record_case_processed(
        self,
        case_type: str,
        status: str = "completed"
    ):
        """Record a processed case."""
        CASES_PROCESSED_TODAY.labels(
            case_type=case_type,
            status=status
        ).inc()
    
    def record_sla_violation(
        self,
        case_type: str,
        sla_type: str = "processing_time"
    ):
        """Record an SLA violation."""
        SLA_VIOLATIONS.labels(
            case_type=case_type,
            sla_type=sla_type
        ).inc()
    
    def record_processing_time(
        self,
        duration: float,
        case_type: str = "unknown"
    ):
        """Record processing time."""
        AVERAGE_PROCESSING_TIME.labels(case_type=case_type).observe(duration)
    
    def set_memory_usage(self, bytes_used: int, component: str = "app"):
        """Set memory usage."""
        MEMORY_USAGE_BYTES.labels(component=component).set(bytes_used)
    
    def set_cpu_usage(self, percent: float, component: str = "app"):
        """Set CPU usage."""
        CPU_USAGE_PERCENT.labels(component=component).set(percent)


# Global metrics collector instance
metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector."""
    return metrics_collector


@contextmanager
def track_request(endpoint: str = "unknown"):
    """Context manager to track request processing."""
    start_time = time.time()
    ACTIVE_REQUESTS.labels(endpoint=endpoint).inc()
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        ACTIVE_REQUESTS.labels(endpoint=endpoint).dec()


@contextmanager
def track_agent_execution(agent_name: str, case_type: str = "unknown"):
    """Context manager to track agent execution."""
    start_time = time.time()
    
    try:
        yield
        duration = time.time() - start_time
        metrics_collector.record_agent_execution(
            agent_name=agent_name,
            status="success",
            case_type=case_type,
            duration=duration
        )
    except Exception as e:
        duration = time.time() - start_time
        metrics_collector.record_agent_execution(
            agent_name=agent_name,
            status="error",
            case_type=case_type,
            duration=duration
        )
        metrics_collector.record_error(
            error_type=type(e).__name__,
            component=f"agent.{agent_name}",
            severity="error"
        )
        raise


@contextmanager
def track_triage_request(case_type: str, priority: str = "normal"):
    """Context manager to track triage request processing."""
    start_time = time.time()
    
    try:
        yield
        duration = time.time() - start_time
        metrics_collector.record_triage_request(
            case_type=case_type,
            status="success",
            priority=priority,
            duration=duration
        )
        metrics_collector.record_case_processed(case_type, "completed")
        metrics_collector.record_processing_time(duration, case_type)
    except Exception as e:
        duration = time.time() - start_time
        metrics_collector.record_triage_request(
            case_type=case_type,
            status="error",
            priority=priority,
            duration=duration
        )
        metrics_collector.record_error(
            error_type=type(e).__name__,
            component="triage",
            severity="error"
        )
        raise


def start_prometheus_server(port: int = 9090, addr: str = "0.0.0.0"):
    """Start the Prometheus metrics server."""
    try:
        start_http_server(port, addr, registry=registry)
        logger.info(f"Prometheus metrics server started on {addr}:{port}")
    except Exception as e:
        logger.error(f"Failed to start Prometheus server: {str(e)}")
        raise


def get_metrics():
    """Get the current metrics in Prometheus format."""
    try:
        return generate_latest(registry)
    except Exception as e:
        logger.error(f"Failed to generate metrics: {str(e)}")
        return b""


def get_metrics_content_type():
    """Get the content type for metrics."""
    return CONTENT_TYPE_LATEST


def update_system_metrics():
    """Update system-level metrics."""
    try:
        import psutil
        
        # Memory usage
        memory = psutil.virtual_memory()
        metrics_collector.set_memory_usage(memory.used, "app")
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics_collector.set_cpu_usage(cpu_percent, "app")
        
        logger.debug(f"System metrics updated - CPU: {cpu_percent}%, Memory: {memory.used} bytes")
        
    except ImportError:
        logger.warning("psutil not available - system metrics not updated")
    except Exception as e:
        logger.error(f"Failed to update system metrics: {str(e)}")


def reset_metrics():
    """Reset all metrics (useful for testing)."""
    try:
        # Reset counters
        for metric in registry.collect():
            if hasattr(metric, 'samples'):
                for sample in metric.samples:
                    if hasattr(sample, 'value'):
                        sample.value = 0
        
        logger.info("Metrics reset completed")
        
    except Exception as e:
        logger.error(f"Failed to reset metrics: {str(e)}")


# Decorator for automatic metrics collection
def track_metrics(metric_type: str = "function", **labels):
    """Decorator to automatically track metrics for functions."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record success metric
                if metric_type == "triage":
                    metrics_collector.record_triage_request(
                        case_type=labels.get("case_type", "unknown"),
                        status="success",
                        duration=duration
                    )
                elif metric_type == "agent":
                    metrics_collector.record_agent_execution(
                        agent_name=labels.get("agent_name", "unknown"),
                        status="success",
                        duration=duration
                    )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Record error metric
                if metric_type == "triage":
                    metrics_collector.record_triage_request(
                        case_type=labels.get("case_type", "unknown"),
                        status="error",
                        duration=duration
                    )
                elif metric_type == "agent":
                    metrics_collector.record_agent_execution(
                        agent_name=labels.get("agent_name", "unknown"),
                        status="error",
                        duration=duration
                    )
                
                metrics_collector.record_error(
                    error_type=type(e).__name__,
                    component=labels.get("component", "unknown"),
                    severity="error"
                )
                
                raise
        
        return wrapper
    return decorator
