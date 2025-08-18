"""
Tests for observability and monitoring components.

This module tests:
- OpenTelemetry telemetry setup and instrumentation
- Prometheus metrics collection and exposure
- Monitoring setup and health checks
- Distributed tracing functionality
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from backend.core.telemetry import (
    setup_telemetry, instrument_fastapi, instrument_sqlalchemy,
    instrument_redis, instrument_httpx, instrument_logging,
    trace_span, record_request_metric, record_triage_metric,
    record_agent_execution_metric, get_current_trace_id,
    get_current_span_id, add_span_event, set_span_attribute,
    trace_function, shutdown_telemetry
)

from backend.core.prometheus import (
    start_prometheus_server, get_metrics, get_metrics_content_type,
    get_metrics_collector, track_request, track_agent_execution,
    track_triage_request, update_system_metrics, reset_metrics,
    track_metrics
)

from backend.core.monitoring import (
    setup_monitoring, instrument_application, shutdown_monitoring,
    get_health_status, system_metrics_updater
)


class TestTelemetry:
    """Test OpenTelemetry telemetry functionality."""
    
    def test_setup_telemetry(self):
        """Test telemetry setup."""
        with patch('backend.core.telemetry.trace') as mock_trace:
            with patch('backend.core.telemetry.metrics') as mock_metrics:
                setup_telemetry(
                    service_name="test-service",
                    service_version="1.0.0",
                    environment="test"
                )
                
                # Verify trace provider was set
                mock_trace.set_tracer_provider.assert_called_once()
                mock_trace.get_tracer.assert_called_once()
    
    def test_trace_span_context_manager(self):
        """Test trace span context manager."""
        with patch('backend.core.telemetry.tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span
            
            with trace_span("test_operation") as span:
                assert span == mock_span
                span.set_attribute.assert_not_called()
    
    def test_trace_span_with_exception(self):
        """Test trace span with exception handling."""
        with patch('backend.core.telemetry.tracer') as mock_tracer:
            mock_span = Mock()
            mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span
            
            with pytest.raises(ValueError):
                with trace_span("test_operation"):
                    raise ValueError("Test error")
            
            # Verify exception was recorded
            mock_span.record_exception.assert_called_once()
            mock_span.set_status.assert_called_once()
    
    def test_record_request_metric(self):
        """Test request metric recording."""
        with patch('backend.core.telemetry.request_counter') as mock_counter:
            with patch('backend.core.telemetry.request_duration') as mock_duration:
                record_request_metric(
                    method="GET",
                    path="/test",
                    status_code=200,
                    duration=1.5,
                    success=True
                )
                
                mock_counter.add.assert_called_once_with(1, attributes={
                    "http.method": "GET",
                    "http.route": "/test",
                    "http.status_code": 200,
                    "success": True
                })
                
                mock_duration.record.assert_called_once_with(1.5, attributes={
                    "http.method": "GET",
                    "http.route": "/test",
                    "http.status_code": 200,
                    "success": True
                })
    
    def test_record_triage_metric(self):
        """Test triage metric recording."""
        with patch('backend.core.telemetry.triage_counter') as mock_counter:
            with patch('backend.core.telemetry.triage_duration') as mock_duration:
                record_triage_metric(
                    case_type="insurance",
                    duration=2.5,
                    success=True,
                    risk_score=0.7
                )
                
                mock_counter.add.assert_called_once_with(1, attributes={
                    "case.type": "insurance",
                    "success": True,
                    "risk_score": 0.7
                })
                
                mock_duration.record.assert_called_once_with(2.5, attributes={
                    "case.type": "insurance",
                    "success": True
                })
    
    def test_record_agent_execution_metric(self):
        """Test agent execution metric recording."""
        with patch('backend.core.telemetry.agent_execution_counter') as mock_counter:
            with patch('backend.core.telemetry.agent_execution_duration') as mock_duration:
                record_agent_execution_metric(
                    agent_name="classifier",
                    duration=1.0,
                    success=True,
                    confidence=0.9
                )
                
                mock_counter.add.assert_called_once_with(1, attributes={
                    "agent.name": "classifier",
                    "success": True,
                    "confidence": 0.9
                })
                
                mock_duration.record.assert_called_once_with(1.0, attributes={
                    "agent.name": "classifier",
                    "success": True
                })
    
    def test_trace_function_decorator(self):
        """Test trace function decorator."""
        with patch('backend.core.telemetry.trace_span') as mock_trace_span:
            mock_span = Mock()
            mock_trace_span.return_value.__enter__.return_value = mock_span
            
            @trace_function("test_function")
            def test_func():
                return "success"
            
            result = test_func()
            assert result == "success"
            mock_trace_span.assert_called_once()
            mock_span.set_attribute.assert_called_with("duration", pytest.approx(0, abs=0.1))
    
    def test_get_current_trace_id(self):
        """Test getting current trace ID."""
        with patch('backend.core.telemetry.trace') as mock_trace:
            mock_span = Mock()
            mock_span.get_span_context.return_value.trace_id = "test-trace-id"
            mock_trace.get_current_span.return_value = mock_span
            
            trace_id = get_current_trace_id()
            assert trace_id == "test-trace-id"
    
    def test_get_current_span_id(self):
        """Test getting current span ID."""
        with patch('backend.core.telemetry.trace') as mock_trace:
            mock_span = Mock()
            mock_span.get_span_context.return_value.span_id = "test-span-id"
            mock_trace.get_current_span.return_value = mock_span
            
            span_id = get_current_span_id()
            assert span_id == "test-span-id"
    
    def test_add_span_event(self):
        """Test adding span event."""
        with patch('backend.core.telemetry.trace') as mock_trace:
            mock_span = Mock()
            mock_trace.get_current_span.return_value = mock_span
            
            add_span_event("test_event", {"key": "value"})
            mock_span.add_event.assert_called_once_with("test_event", attributes={"key": "value"})
    
    def test_set_span_attribute(self):
        """Test setting span attribute."""
        with patch('backend.core.telemetry.trace') as mock_trace:
            mock_span = Mock()
            mock_trace.get_current_span.return_value = mock_span
            
            set_span_attribute("test_key", "test_value")
            mock_span.set_attribute.assert_called_once_with("test_key", "test_value")


class TestPrometheus:
    """Test Prometheus metrics functionality."""
    
    def test_get_metrics_collector(self):
        """Test getting metrics collector."""
        collector = get_metrics_collector()
        assert collector is not None
        assert hasattr(collector, 'record_triage_request')
        assert hasattr(collector, 'record_agent_execution')
    
    def test_metrics_collector_record_triage_request(self):
        """Test metrics collector triage request recording."""
        collector = get_metrics_collector()
        
        with patch('backend.core.prometheus.TRIAGE_REQUESTS_TOTAL') as mock_counter:
            with patch('backend.core.prometheus.TRIAGE_DURATION_SECONDS') as mock_duration:
                collector.record_triage_request(
                    case_type="insurance",
                    status="success",
                    priority="high",
                    duration=2.0
                )
                
                mock_counter.labels.assert_called_once_with(
                    case_type="insurance",
                    status="success",
                    priority="high"
                )
                mock_counter.labels.return_value.inc.assert_called_once()
                
                mock_duration.labels.assert_called_once_with(
                    case_type="insurance",
                    status="success"
                )
                mock_duration.labels.return_value.observe.assert_called_once_with(2.0)
    
    def test_metrics_collector_record_agent_execution(self):
        """Test metrics collector agent execution recording."""
        collector = get_metrics_collector()
        
        with patch('backend.core.prometheus.AGENT_EXECUTIONS_TOTAL') as mock_counter:
            with patch('backend.core.prometheus.AGENT_EXECUTION_DURATION_SECONDS') as mock_duration:
                with patch('backend.core.prometheus.CONFIDENCE_SCORES') as mock_confidence:
                    collector.record_agent_execution(
                        agent_name="classifier",
                        status="success",
                        case_type="insurance",
                        duration=1.5,
                        confidence=0.9
                    )
                    
                    mock_counter.labels.assert_called_once_with(
                        agent_name="classifier",
                        status="success",
                        case_type="insurance"
                    )
                    mock_counter.labels.return_value.inc.assert_called_once()
                    
                    mock_duration.labels.assert_called_once_with(
                        agent_name="classifier",
                        status="success"
                    )
                    mock_duration.labels.return_value.observe.assert_called_once_with(1.5)
                    
                    mock_confidence.labels.assert_called_once_with(
                        agent_name="classifier",
                        case_type="insurance"
                    )
                    mock_confidence.labels.return_value.observe.assert_called_once_with(0.9)
    
    def test_track_request_context_manager(self):
        """Test track request context manager."""
        with patch('backend.core.prometheus.ACTIVE_REQUESTS') as mock_active:
            with track_request("test_endpoint"):
                mock_active.labels.assert_called_once_with(endpoint="test_endpoint")
                mock_active.labels.return_value.inc.assert_called_once()
            
            mock_active.labels.return_value.dec.assert_called_once()
    
    def test_track_agent_execution_context_manager(self):
        """Test track agent execution context manager."""
        collector = get_metrics_collector()
        
        with patch.object(collector, 'record_agent_execution') as mock_record:
            with track_agent_execution("classifier", "insurance"):
                pass
            
            mock_record.assert_called_once()
            call_args = mock_record.call_args
            assert call_args[1]['agent_name'] == "classifier"
            assert call_args[1]['case_type'] == "insurance"
            assert call_args[1]['status'] == "success"
    
    def test_track_triage_request_context_manager(self):
        """Test track triage request context manager."""
        collector = get_metrics_collector()
        
        with patch.object(collector, 'record_triage_request') as mock_record:
            with patch.object(collector, 'record_case_processed') as mock_case:
                with patch.object(collector, 'record_processing_time') as mock_time:
                    with track_triage_request("insurance", "high"):
                        pass
                    
                    mock_record.assert_called_once()
                    mock_case.assert_called_once()
                    mock_time.assert_called_once()
    
    def test_get_metrics(self):
        """Test getting metrics in Prometheus format."""
        metrics = get_metrics()
        assert isinstance(metrics, bytes)
        assert len(metrics) > 0
    
    def test_get_metrics_content_type(self):
        """Test getting metrics content type."""
        content_type = get_metrics_content_type()
        assert content_type == "text/plain; version=0.0.4; charset=utf-8"
    
    def test_update_system_metrics(self):
        """Test updating system metrics."""
        with patch('backend.core.prometheus.psutil') as mock_psutil:
            mock_memory = Mock()
            mock_memory.used = 1024 * 1024 * 100  # 100MB
            mock_psutil.virtual_memory.return_value = mock_memory
            mock_psutil.cpu_percent.return_value = 25.5
            
            collector = get_metrics_collector()
            with patch.object(collector, 'set_memory_usage') as mock_memory_set:
                with patch.object(collector, 'set_cpu_usage') as mock_cpu_set:
                    update_system_metrics()
                    
                    mock_memory_set.assert_called_once_with(1024 * 1024 * 100, "app")
                    mock_cpu_set.assert_called_once_with(25.5, "app")
    
    def test_reset_metrics(self):
        """Test resetting metrics."""
        with patch('backend.core.prometheus.registry') as mock_registry:
            mock_metric = Mock()
            mock_metric.samples = [Mock(value=10)]
            mock_registry.collect.return_value = [mock_metric]
            
            reset_metrics()
            # Verify that metrics were reset (value set to 0)
            assert mock_metric.samples[0].value == 0


class TestMonitoring:
    """Test monitoring setup and functionality."""
    
    def test_setup_monitoring(self):
        """Test monitoring setup."""
        with patch('backend.core.monitoring.setup_telemetry') as mock_telemetry:
            with patch('backend.core.monitoring.start_prometheus_server') as mock_prometheus:
                with patch('backend.core.monitoring.asyncio.create_task') as mock_task:
                    setup_monitoring(
                        enable_telemetry=True,
                        enable_prometheus=True,
                        prometheus_port=9090
                    )
                    
                    mock_telemetry.assert_called_once()
                    mock_prometheus.assert_called_once_with(port=9090)
                    mock_task.assert_called_once()
    
    def test_setup_monitoring_disabled(self):
        """Test monitoring setup with disabled components."""
        with patch('backend.core.monitoring.setup_telemetry') as mock_telemetry:
            with patch('backend.core.monitoring.start_prometheus_server') as mock_prometheus:
                setup_monitoring(
                    enable_telemetry=False,
                    enable_prometheus=False
                )
                
                mock_telemetry.assert_not_called()
                mock_prometheus.assert_not_called()
    
    def test_instrument_application(self):
        """Test application instrumentation."""
        mock_app = Mock()
        mock_engine = Mock()
        
        with patch('backend.core.monitoring.instrument_fastapi') as mock_fastapi:
            with patch('backend.core.monitoring.instrument_sqlalchemy') as mock_sqlalchemy:
                with patch('backend.core.monitoring.instrument_redis') as mock_redis:
                    with patch('backend.core.monitoring.instrument_httpx') as mock_httpx:
                        with patch('backend.core.monitoring.instrument_logging') as mock_logging:
                            instrument_application(mock_app, mock_engine)
                            
                            mock_fastapi.assert_called_once_with(mock_app)
                            mock_sqlalchemy.assert_called_once_with(mock_engine)
                            mock_redis.assert_called_once()
                            mock_httpx.assert_called_once()
                            mock_logging.assert_called_once()
    
    def test_get_health_status(self):
        """Test getting health status."""
        status = get_health_status()
        
        assert "status" in status
        assert "timestamp" in status
        assert "monitoring" in status
        assert "metrics" in status
        assert status["monitoring"]["telemetry_initialized"] in [True, False]
        assert status["monitoring"]["prometheus_server"] in [True, False]
    
    @pytest.mark.asyncio
    async def test_system_metrics_updater(self):
        """Test system metrics updater task."""
        with patch('backend.core.monitoring.update_system_metrics') as mock_update:
            with patch('backend.core.monitoring.asyncio.sleep') as mock_sleep:
                # Create a task that will run for a short time
                task = asyncio.create_task(system_metrics_updater())
                
                # Let it run for a moment
                await asyncio.sleep(0.1)
                
                # Cancel the task
                task.cancel()
                
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
                # Verify that update was called
                mock_update.assert_called()
                mock_sleep.assert_called()


class TestObservabilityIntegration:
    """Test integration between observability components."""
    
    def test_telemetry_and_prometheus_integration(self):
        """Test integration between telemetry and prometheus."""
        # Setup telemetry
        setup_telemetry(enable_console_export=True, enable_otlp_export=False)
        
        # Get metrics collector
        collector = get_metrics_collector()
        
        # Record some metrics
        collector.record_triage_request("insurance", "success", "normal", 1.5)
        collector.record_agent_execution("classifier", "success", "insurance", 0.8, 0.9)
        
        # Verify metrics are available
        metrics = get_metrics()
        assert isinstance(metrics, bytes)
        assert len(metrics) > 0
        
        # Cleanup
        shutdown_telemetry()
    
    def test_monitoring_full_setup(self):
        """Test full monitoring setup."""
        with patch('backend.core.monitoring.setup_telemetry') as mock_telemetry:
            with patch('backend.core.monitoring.start_prometheus_server') as mock_prometheus:
                with patch('backend.core.monitoring.asyncio.create_task') as mock_task:
                    # Setup monitoring
                    setup_monitoring(
                        enable_telemetry=True,
                        enable_prometheus=True,
                        prometheus_port=9090
                    )
                    
                    # Verify all components were initialized
                    mock_telemetry.assert_called_once()
                    mock_prometheus.assert_called_once_with(port=9090)
                    mock_task.assert_called_once()
                    
                    # Test health status
                    status = get_health_status()
                    assert status["status"] in ["healthy", "degraded"]
                    
                    # Cleanup
                    shutdown_monitoring()


if __name__ == "__main__":
    pytest.main([__file__])
