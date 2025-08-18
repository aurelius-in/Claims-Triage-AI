"""
Monitoring and telemetry setup for the Claims Triage AI platform.
"""

import logging
import asyncio
from typing import Dict, Any
from datetime import datetime
import time

from .telemetry import setup_telemetry, instrument_fastapi, instrument_sqlalchemy, instrument_redis, instrument_httpx, instrument_logging, shutdown_telemetry
from .prometheus import start_prometheus_server, get_metrics_collector, update_system_metrics

logger = logging.getLogger(__name__)

# Global monitoring state
monitoring_initialized = False
prometheus_server_started = False


def setup_monitoring(
    enable_telemetry: bool = True,
    enable_prometheus: bool = True,
    prometheus_port: int = 9090,
    otlp_endpoint: str = None,
    environment: str = "development"
):
    """Setup monitoring and telemetry."""
    global monitoring_initialized, prometheus_server_started
    
    try:
        if enable_telemetry:
            # Setup OpenTelemetry
            setup_telemetry(
                service_name="claims-triage-ai",
                service_version="1.0.0",
                environment=environment,
                otlp_endpoint=otlp_endpoint,
                enable_console_export=True,
                enable_otlp_export=bool(otlp_endpoint)
            )
            logger.info("OpenTelemetry setup completed")
        
        if enable_prometheus:
            # Start Prometheus metrics server
            start_prometheus_server(port=prometheus_port)
            prometheus_server_started = True
            logger.info(f"Prometheus metrics server started on port {prometheus_port}")
        
        # Start system metrics update task
        asyncio.create_task(system_metrics_updater())
        
        monitoring_initialized = True
        logger.info("Monitoring setup completed")
        
    except Exception as e:
        logger.error(f"Monitoring setup failed: {str(e)}")
        raise


async def system_metrics_updater():
    """Background task to update system metrics."""
    while True:
        try:
            update_system_metrics()
            await asyncio.sleep(30)  # Update every 30 seconds
        except Exception as e:
            logger.error(f"Failed to update system metrics: {str(e)}")
            await asyncio.sleep(60)  # Wait longer on error


def instrument_application(app, engine=None):
    """Instrument the application with OpenTelemetry."""
    try:
        # Instrument FastAPI
        instrument_fastapi(app)
        
        # Instrument SQLAlchemy if engine is provided
        if engine:
            instrument_sqlalchemy(engine)
        
        # Instrument Redis
        instrument_redis()
        
        # Instrument HTTPX
        instrument_httpx()
        
        # Instrument logging
        instrument_logging()
        
        logger.info("Application instrumentation completed")
        
    except Exception as e:
        logger.error(f"Application instrumentation failed: {str(e)}")


def shutdown_monitoring():
    """Shutdown monitoring and telemetry."""
    global monitoring_initialized, prometheus_server_started
    
    try:
        if monitoring_initialized:
            shutdown_telemetry()
            monitoring_initialized = False
            logger.info("Monitoring shutdown completed")
        
    except Exception as e:
        logger.error(f"Monitoring shutdown failed: {str(e)}")


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
        """Record agent execution."""
        if agent_name not in self.metrics["agent_executions"]:
            self.metrics["agent_executions"][agent_name] = {
                "total": 0,
                "success": 0,
                "errors": 0,
                "total_duration": 0
            }
        
        self.metrics["agent_executions"][agent_name]["total"] += 1
        self.metrics["agent_executions"][agent_name]["total_duration"] += duration_ms
        
        if success:
            self.metrics["agent_executions"][agent_name]["success"] += 1
        else:
            self.metrics["agent_executions"][agent_name]["errors"] += 1
    
    def record_processing_time(self, duration_ms: int):
        """Record processing time."""
        self.metrics["processing_times"].append(duration_ms)
        # Keep only last 1000 times
        if len(self.metrics["processing_times"]) > 1000:
            self.metrics["processing_times"] = self.metrics["processing_times"][-1000:]
    
    def record_error(self, error_type: str):
        """Record error."""
        if error_type not in self.metrics["error_counts"]:
            self.metrics["error_counts"][error_type] = 0
        self.metrics["error_counts"][error_type] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        metrics = self.metrics.copy()
        
        # Calculate averages
        if metrics["processing_times"]:
            metrics["avg_processing_time"] = sum(metrics["processing_times"]) / len(metrics["processing_times"])
        else:
            metrics["avg_processing_time"] = 0
        
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


# Global metrics collector instance
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


def get_health_status() -> Dict[str, Any]:
    """Get comprehensive health status."""
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "monitoring": {
            "telemetry_initialized": monitoring_initialized,
            "prometheus_server": prometheus_server_started
        },
        "metrics": {
            "requests_total": metrics_collector.metrics["requests_total"],
            "triage_requests": metrics_collector.metrics["triage_requests"],
            "avg_processing_time": 0
        }
    }
    
    # Calculate average processing time
    if metrics_collector.metrics["processing_times"]:
        status["metrics"]["avg_processing_time"] = sum(metrics_collector.metrics["processing_times"]) / len(metrics_collector.metrics["processing_times"])
    
    # Check for errors
    if metrics_collector.metrics["requests_error"] > 0 or metrics_collector.metrics["triage_errors"] > 0:
        status["status"] = "degraded"
    
    return status
