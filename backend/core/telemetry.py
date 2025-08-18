"""
OpenTelemetry telemetry setup for the Claims Triage AI platform.

This module provides:
- Distributed tracing with spans and context propagation
- Metrics collection for business and technical metrics
- Log correlation with trace IDs
- Automatic instrumentation for FastAPI, SQLAlchemy, Redis, and HTTP clients
"""

import logging
import os
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
from datetime import datetime
import time

# OpenTelemetry imports
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    OTLPSpanExporter
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    OTLPMetricExporter,
    PeriodicExportingMetricReader
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as GRPCSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter as GRPCMetricExporter

logger = logging.getLogger(__name__)

# Global tracer and meter
tracer: Optional[trace.Tracer] = None
meter: Optional[metrics.Meter] = None

# Metrics
request_counter: Optional[metrics.Counter] = None
request_duration: Optional[metrics.Histogram] = None
triage_counter: Optional[metrics.Counter] = None
triage_duration: Optional[metrics.Histogram] = None
agent_execution_counter: Optional[metrics.Counter] = None
agent_execution_duration: Optional[metrics.Histogram] = None
error_counter: Optional[metrics.Counter] = None
active_requests: Optional[metrics.UpDownCounter] = None


def setup_telemetry(
    service_name: str = "claims-triage-ai",
    service_version: str = "1.0.0",
    environment: str = "development",
    otlp_endpoint: Optional[str] = None,
    enable_console_export: bool = True,
    enable_otlp_export: bool = False
) -> None:
    """
    Setup OpenTelemetry telemetry with tracing and metrics.
    
    Args:
        service_name: Name of the service
        service_version: Version of the service
        environment: Environment (development, staging, production)
        otlp_endpoint: OTLP endpoint for exporting telemetry data
        enable_console_export: Enable console export for development
        enable_otlp_export: Enable OTLP export for production
    """
    global tracer, meter, request_counter, request_duration, triage_counter
    global triage_duration, agent_execution_counter, agent_execution_duration
    global error_counter, active_requests
    
    try:
        # Create resource with service information
        resource = Resource.create({
            "service.name": service_name,
            "service.version": service_version,
            "service.instance.id": os.getenv("HOSTNAME", "unknown"),
            "deployment.environment": environment,
        })
        
        # Setup tracing
        trace_provider = TracerProvider(resource=resource)
        
        # Add span processors
        if enable_console_export:
            trace_provider.add_span_processor(
                BatchSpanProcessor(ConsoleSpanExporter())
            )
        
        if enable_otlp_export and otlp_endpoint:
            trace_provider.add_span_processor(
                BatchSpanProcessor(
                    OTLPSpanExporter(endpoint=otlp_endpoint)
                )
            )
        
        # Set the global trace provider
        trace.set_tracer_provider(trace_provider)
        tracer = trace.get_tracer(__name__)
        
        # Setup metrics
        metric_readers = []
        
        if enable_console_export:
            metric_readers.append(
                PeriodicExportingMetricReader(
                    ConsoleMetricExporter(),
                    export_interval_millis=5000
                )
            )
        
        if enable_otlp_export and otlp_endpoint:
            metric_readers.append(
                PeriodicExportingMetricReader(
                    OTLPMetricExporter(endpoint=otlp_endpoint),
                    export_interval_millis=10000
                )
            )
        
        if metric_readers:
            meter_provider = MeterProvider(
                resource=resource,
                metric_readers=metric_readers
            )
            metrics.set_meter_provider(meter_provider)
            meter = metrics.get_meter(__name__)
            
            # Create metrics
            request_counter = meter.create_counter(
                name="http_requests_total",
                description="Total number of HTTP requests",
                unit="1"
            )
            
            request_duration = meter.create_histogram(
                name="http_request_duration_seconds",
                description="HTTP request duration in seconds",
                unit="s"
            )
            
            triage_counter = meter.create_counter(
                name="triage_requests_total",
                description="Total number of triage requests",
                unit="1"
            )
            
            triage_duration = meter.create_histogram(
                name="triage_duration_seconds",
                description="Triage processing duration in seconds",
                unit="s"
            )
            
            agent_execution_counter = meter.create_counter(
                name="agent_executions_total",
                description="Total number of agent executions",
                unit="1"
            )
            
            agent_execution_duration = meter.create_histogram(
                name="agent_execution_duration_seconds",
                description="Agent execution duration in seconds",
                unit="s"
            )
            
            error_counter = meter.create_counter(
                name="errors_total",
                description="Total number of errors",
                unit="1"
            )
            
            active_requests = meter.create_up_down_counter(
                name="active_requests",
                description="Number of active requests",
                unit="1"
            )
        
        logger.info(f"Telemetry setup completed for {service_name} v{service_version}")
        
    except Exception as e:
        logger.error(f"Failed to setup telemetry: {str(e)}")
        raise


def instrument_fastapi(app) -> None:
    """Instrument FastAPI application with OpenTelemetry."""
    try:
        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI instrumentation enabled")
    except Exception as e:
        logger.error(f"Failed to instrument FastAPI: {str(e)}")


def instrument_sqlalchemy(engine) -> None:
    """Instrument SQLAlchemy engine with OpenTelemetry."""
    try:
        SQLAlchemyInstrumentor().instrument(engine=engine)
        logger.info("SQLAlchemy instrumentation enabled")
    except Exception as e:
        logger.error(f"Failed to instrument SQLAlchemy: {str(e)}")


def instrument_redis() -> None:
    """Instrument Redis with OpenTelemetry."""
    try:
        RedisInstrumentor().instrument()
        logger.info("Redis instrumentation enabled")
    except Exception as e:
        logger.error(f"Failed to instrument Redis: {str(e)}")


def instrument_httpx() -> None:
    """Instrument HTTPX client with OpenTelemetry."""
    try:
        HTTPXClientInstrumentor().instrument()
        logger.info("HTTPX instrumentation enabled")
    except Exception as e:
        logger.error(f"Failed to instrument HTTPX: {str(e)}")


def instrument_logging() -> None:
    """Instrument logging with OpenTelemetry."""
    try:
        LoggingInstrumentor().instrument(
            set_logging_format=True,
            log_level=logging.INFO
        )
        logger.info("Logging instrumentation enabled")
    except Exception as e:
        logger.error(f"Failed to instrument logging: {str(e)}")


@contextmanager
def trace_span(
    name: str,
    attributes: Optional[Dict[str, Any]] = None,
    kind: trace.SpanKind = trace.SpanKind.INTERNAL
):
    """
    Context manager for creating spans.
    
    Args:
        name: Name of the span
        attributes: Span attributes
        kind: Span kind
    """
    if not tracer:
        yield
        return
    
    with tracer.start_as_current_span(
        name,
        attributes=attributes or {},
        kind=kind
    ) as span:
        try:
            yield span
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise


def record_request_metric(
    method: str,
    path: str,
    status_code: int,
    duration: float,
    success: bool = True
) -> None:
    """Record HTTP request metrics."""
    if not request_counter or not request_duration:
        return
    
    attributes = {
        "http.method": method,
        "http.route": path,
        "http.status_code": status_code,
        "success": success
    }
    
    request_counter.add(1, attributes=attributes)
    request_duration.record(duration, attributes=attributes)


def record_triage_metric(
    case_type: str,
    duration: float,
    success: bool = True,
    risk_score: Optional[float] = None
) -> None:
    """Record triage processing metrics."""
    if not triage_counter or not triage_duration:
        return
    
    attributes = {
        "case.type": case_type,
        "success": success
    }
    
    if risk_score is not None:
        attributes["risk_score"] = risk_score
    
    triage_counter.add(1, attributes=attributes)
    triage_duration.record(duration, attributes=attributes)


def record_agent_execution_metric(
    agent_name: str,
    duration: float,
    success: bool = True,
    confidence: Optional[float] = None
) -> None:
    """Record agent execution metrics."""
    if not agent_execution_counter or not agent_execution_duration:
        return
    
    attributes = {
        "agent.name": agent_name,
        "success": success
    }
    
    if confidence is not None:
        attributes["confidence"] = confidence
    
    agent_execution_counter.add(1, attributes=attributes)
    agent_execution_duration.record(duration, attributes=attributes)


def record_error_metric(
    error_type: str,
    error_message: str,
    component: str = "unknown"
) -> None:
    """Record error metrics."""
    if not error_counter:
        return
    
    attributes = {
        "error.type": error_type,
        "error.message": error_message,
        "component": component
    }
    
    error_counter.add(1, attributes=attributes)


def increment_active_requests(delta: int = 1) -> None:
    """Increment active requests counter."""
    if not active_requests:
        return
    
    active_requests.add(delta)


def get_current_trace_id() -> Optional[str]:
    """Get current trace ID."""
    if not tracer:
        return None
    
    current_span = trace.get_current_span()
    if current_span:
        return current_span.get_span_context().trace_id
    return None


def get_current_span_id() -> Optional[str]:
    """Get current span ID."""
    if not tracer:
        return None
    
    current_span = trace.get_current_span()
    if current_span:
        return current_span.get_span_context().span_id
    return None


def add_span_event(name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
    """Add event to current span."""
    if not tracer:
        return
    
    current_span = trace.get_current_span()
    if current_span:
        current_span.add_event(name, attributes=attributes or {})


def set_span_attribute(key: str, value: Any) -> None:
    """Set attribute on current span."""
    if not tracer:
        return
    
    current_span = trace.get_current_span()
    if current_span:
        current_span.set_attribute(key, value)


def trace_function(name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None):
    """
    Decorator to trace function execution.
    
    Args:
        name: Span name (defaults to function name)
        attributes: Span attributes
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            span_name = name or f"{func.__module__}.{func.__name__}"
            
            with trace_span(span_name, attributes=attributes) as span:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    span.set_attribute("duration", duration)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    span.set_attribute("duration", duration)
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    raise
        return wrapper
    return decorator


def shutdown_telemetry() -> None:
    """Shutdown telemetry providers."""
    try:
        # Shutdown trace provider
        trace_provider = trace.get_tracer_provider()
        if hasattr(trace_provider, 'shutdown'):
            trace_provider.shutdown()
        
        # Shutdown meter provider
        meter_provider = metrics.get_meter_provider()
        if hasattr(meter_provider, 'shutdown'):
            meter_provider.shutdown()
        
        logger.info("Telemetry shutdown completed")
        
    except Exception as e:
        logger.error(f"Failed to shutdown telemetry: {str(e)}")
