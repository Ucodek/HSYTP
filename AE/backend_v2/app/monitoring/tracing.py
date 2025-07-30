"""Distributed tracing setup using OpenTelemetry."""

import logging
from functools import wraps
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, StatusCode, get_current_span

from app.core.config.base import settings

logger = logging.getLogger(__name__)

# Global tracer provider
_tracer_provider: Optional[TracerProvider] = None
_is_tracing_enabled = False


def setup_tracing(
    app: FastAPI,
    service_name: str = None,
    exporter_endpoint: str = None,
    export_traces: bool = True,
) -> None:
    """
    Setup distributed tracing for the application.

    Args:
        app: FastAPI application
        service_name: Name of the service (default: from settings)
        exporter_endpoint: OpenTelemetry exporter endpoint
        export_traces: Whether to export traces (default: True)
    """
    global _tracer_provider, _is_tracing_enabled

    # If tracing is already set up, return
    if _tracer_provider is not None:
        return

    # If we're in testing mode or explicitly disabled, don't set up tracing
    if not export_traces:
        logger.info("Tracing is disabled")
        return

    try:
        # Create a resource with service info
        service_name = service_name or settings.PROJECT_NAME
        resource = Resource.create({"service.name": service_name})

        # Set up trace provider
        _tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(_tracer_provider)

        # Configure exporter if endpoint is provided
        if exporter_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=exporter_endpoint)
            _tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            logger.info(f"Configured OTLP trace exporter to {exporter_endpoint}")

        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app)

        # Instrument other libraries
        RequestsInstrumentor().instrument()

        # Flag that tracing is enabled
        _is_tracing_enabled = True

        logger.info(f"Distributed tracing configured for service: {service_name}")
    except Exception as e:
        logger.error(f"Failed to set up tracing: {e}")


def instrument_sqlalchemy(engine):
    """
    Instrument SQLAlchemy for tracing.

    Args:
        engine: SQLAlchemy engine
    """
    if _is_tracing_enabled:
        try:
            SQLAlchemyInstrumentor().instrument(engine=engine)
            logger.info("SQLAlchemy instrumented for tracing")
        except Exception as e:
            logger.error(f"Failed to instrument SQLAlchemy: {e}")


def instrument_redis(client):
    """
    Instrument Redis for tracing.

    Args:
        client: Redis client
    """
    if _is_tracing_enabled:
        try:
            RedisInstrumentor().instrument(client=client)
            logger.info("Redis instrumented for tracing")
        except Exception as e:
            logger.error(f"Failed to instrument Redis: {e}")


def get_tracer(name: str = None):
    """
    Get a tracer for creating spans.

    Args:
        name: Name of the tracer (default: __name__)

    Returns:
        Tracer instance
    """
    name = name or __name__
    return trace.get_tracer(name)


def trace_function(
    name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None
):
    """
    Decorator to trace a function execution.

    Args:
        name: Name of the span (default: function name)
        attributes: Attributes to add to the span
    """

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not _is_tracing_enabled:
                return await func(*args, **kwargs)

            span_name = name or func.__name__
            tracer = get_tracer(func.__module__)

            with tracer.start_as_current_span(span_name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                try:
                    result = await func(*args, **kwargs)
                    span.set_status(StatusCode.OK)
                    return result
                except Exception as e:
                    span.set_status(StatusCode.ERROR, str(e))
                    span.record_exception(e)
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not _is_tracing_enabled:
                return func(*args, **kwargs)

            span_name = name or func.__name__
            tracer = get_tracer(func.__module__)

            with tracer.start_as_current_span(span_name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                try:
                    result = func(*args, **kwargs)
                    span.set_status(StatusCode.OK)
                    return result
                except Exception as e:
                    span.set_status(StatusCode.ERROR, str(e))
                    span.record_exception(e)
                    raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def add_span_attribute(key: str, value: Any) -> None:
    """
    Add an attribute to the current span.

    Args:
        key: Attribute key
        value: Attribute value
    """
    if _is_tracing_enabled:
        current_span = get_current_span()
        if current_span:
            current_span.set_attribute(key, value)


def start_span(name: str, attributes: Optional[Dict[str, Any]] = None) -> Span:
    """
    Start a new span.

    Args:
        name: Span name
        attributes: Optional span attributes

    Returns:
        New span
    """
    tracer = get_tracer()
    span = tracer.start_span(name)

    if attributes:
        for key, value in attributes.items():
            span.set_attribute(key, value)

    return span


def extract_span_context(request: Request) -> Dict[str, str]:
    """
    Extract tracing context from a request.

    Args:
        request: FastAPI request

    Returns:
        Dictionary with span context information
    """
    if not _is_tracing_enabled:
        return {}

    try:
        current_span = get_current_span()
        if not current_span:
            return {}

        span_context = current_span.get_span_context()
        return {
            "trace_id": format(span_context.trace_id, "032x"),
            "span_id": format(span_context.span_id, "016x"),
            "trace_flags": str(span_context.trace_flags),
        }
    except Exception as e:
        logger.error(f"Failed to extract span context: {e}")
        return {}


# Import asyncio for the trace_function decorator
import asyncio
