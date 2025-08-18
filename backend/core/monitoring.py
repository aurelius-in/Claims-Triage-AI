"""
Monitoring and telemetry setup for the Claims Triage AI platform.
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def setup_monitoring():
    """Setup monitoring and telemetry."""
    try:
        # TODO: Setup OpenTelemetry
        # TODO: Setup Prometheus metrics
        # TODO: Setup distributed tracing
        
        logger.info("Monitoring setup initialized")
        
    except Exception as e:
        logger.warning(f"Monitoring setup failed: {str(e)}")


class MetricsCollector:
    """Simple metrics collector for the application."""
    
    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "triage_requests": 0,
            "triage_success": 0,
            "triage_errors": 0,
            "agent_executions": {},
            "processing_times": [],
            "error_counts": {}
        }
    
    def increment_request(self, success: bool = True):
        """Increment request counter."""
        self.metrics["requests_total"] += 1
        if success:
            self.metrics["requests_success"] += 1
        else:
            self.metrics["requests_error"] += 1
    
    def increment_triage(self, success: bool = True):
        """Increment triage counter."""
        self.metrics["triage_requests"] += 1
        if success:
            self.metrics["triage_success"] += 1
        else:
            self.metrics["triage_errors"] += 1
    
    def record_agent_execution(self, agent_name: str, success: bool = True, duration_ms: int = 0):
        """Record agent execution metrics."""
        if agent_name not in self.metrics["agent_executions"]:
            self.metrics["agent_executions"][agent_name] = {
                "total": 0,
                "success": 0,
                "errors": 0,
                "avg_duration_ms": 0
            }
        
        agent_metrics = self.metrics["agent_executions"][agent_name]
        agent_metrics["total"] += 1
        
        if success:
            agent_metrics["success"] += 1
        else:
            agent_metrics["errors"] += 1
        
        # Update average duration
        if duration_ms > 0:
            current_avg = agent_metrics["avg_duration_ms"]
            total_executions = agent_metrics["total"]
            agent_metrics["avg_duration_ms"] = (
                (current_avg * (total_executions - 1) + duration_ms) / total_executions
            )
    
    def record_processing_time(self, duration_ms: int):
        """Record processing time."""
        self.metrics["processing_times"].append(duration_ms)
        # Keep only last 1000 measurements
        if len(self.metrics["processing_times"]) > 1000:
            self.metrics["processing_times"] = self.metrics["processing_times"][-1000:]
    
    def record_error(self, error_type: str):
        """Record error occurrence."""
        if error_type not in self.metrics["error_counts"]:
            self.metrics["error_counts"][error_type] = 0
        self.metrics["error_counts"][error_type] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        metrics = self.metrics.copy()
        
        # Calculate additional metrics
        if metrics["processing_times"]:
            metrics["avg_processing_time_ms"] = sum(metrics["processing_times"]) / len(metrics["processing_times"])
            metrics["min_processing_time_ms"] = min(metrics["processing_times"])
            metrics["max_processing_time_ms"] = max(metrics["processing_times"])
        else:
            metrics["avg_processing_time_ms"] = 0
            metrics["min_processing_time_ms"] = 0
            metrics["max_processing_time_ms"] = 0
        
        # Calculate success rates
        if metrics["requests_total"] > 0:
            metrics["request_success_rate"] = metrics["requests_success"] / metrics["requests_total"]
        else:
            metrics["request_success_rate"] = 0
        
        if metrics["triage_requests"] > 0:
            metrics["triage_success_rate"] = metrics["triage_success"] / metrics["triage_requests"]
        else:
            metrics["triage_success_rate"] = 0
        
        return metrics
    
    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "triage_requests": 0,
            "triage_success": 0,
            "triage_errors": 0,
            "agent_executions": {},
            "processing_times": [],
            "error_counts": {}
        }


# Global metrics collector
metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector."""
    return metrics_collector


class PerformanceMonitor:
    """Performance monitoring context manager."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (datetime.utcnow() - self.start_time).total_seconds() * 1000
            metrics_collector.record_processing_time(int(duration))
            
            if exc_type:
                metrics_collector.record_error(f"{self.operation_name}_error")
                logger.error(f"Operation {self.operation_name} failed after {duration:.2f}ms: {str(exc_val)}")
            else:
                logger.debug(f"Operation {self.operation_name} completed in {duration:.2f}ms")


def monitor_performance(operation_name: str):
    """Decorator for monitoring function performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with PerformanceMonitor(operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator
