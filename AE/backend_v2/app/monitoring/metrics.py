"""Application metrics collection using Prometheus."""

import logging
import time
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Dict, Optional

from fastapi import FastAPI, Request, Response
from prometheus_client import (
    REGISTRY,
    Counter,
    Gauge,
    Histogram,
    Summary,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Default metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total count of HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0],
)

REQUEST_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "endpoint"],
)

DATABASE_QUERY_LATENCY = Histogram(
    "database_query_duration_seconds",
    "Database query latency in seconds",
    ["query_type"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0],
)

CACHE_HIT_COUNT = Counter(
    "cache_hits_total", "Total count of cache hits", ["cache_type"]
)

CACHE_MISS_COUNT = Counter(
    "cache_misses_total", "Total count of cache misses", ["cache_type"]
)

ERROR_COUNT = Counter("error_total", "Total count of errors", ["error_type"])

ACTIVE_USERS = Gauge("active_users", "Number of active users")


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to track HTTP request metrics."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Parse the request path to get a proper endpoint identifier
        path = request.url.path
        method = request.method
        endpoint = path

        # For paths with IDs, replace the ID with a placeholder to avoid high cardinality
        # Example: /api/users/123 -> /api/users/:id
        # This simple version handles numeric IDs and UUIDs at the end of the path
        parts = path.split("/")
        if (
            len(parts) > 2
            and parts[-1].isdigit()
            or (len(parts[-1]) > 30 and "-" in parts[-1])
        ):
            parts[-1] = ":id"
            endpoint = "/".join(parts)

        # Track in-progress requests
        REQUEST_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()

        # Track request latency
        start_time = time.time()
        try:
            response = await call_next(request)

            # Record metrics
            status_code = response.status_code
            latency = time.time() - start_time

            REQUEST_COUNT.labels(
                method=method, endpoint=endpoint, status_code=status_code
            ).inc()

            REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)

            return response
        except Exception as e:
            # Track exceptions
            latency = time.time() - start_time
            ERROR_COUNT.labels(error_type=type(e).__name__).inc()
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)
            REQUEST_COUNT.labels(
                method=method, endpoint=endpoint, status_code=500
            ).inc()
            raise
        finally:
            # Decrement in-progress gauge
            REQUEST_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()


@contextmanager
def track_database_query(query_type: str = "generic"):
    """Context manager to track database query latency."""
    start_time = time.time()
    try:
        yield
    finally:
        latency = time.time() - start_time
        DATABASE_QUERY_LATENCY.labels(query_type=query_type).observe(latency)


def track_cache_access(hit: bool, cache_type: str = "generic"):
    """Track cache hits and misses."""
    if hit:
        CACHE_HIT_COUNT.labels(cache_type=cache_type).inc()
    else:
        CACHE_MISS_COUNT.labels(cache_type=cache_type).inc()


def track_active_user(increment: bool = True):
    """Track active user count."""
    if increment:
        ACTIVE_USERS.inc()
    else:
        ACTIVE_USERS.dec()


def timer(name: str, description: str, labels: Optional[list] = None):
    """
    Decorator for timing function execution.

    Args:
        name: Metric name
        description: Metric description
        labels: Optional labels for the timer
    """
    if labels is None:
        labels = []

    timer_metric = Summary(name, description, labels)

    def decorator(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            # Extract label values from arguments if needed
            label_values = {}
            # Example: if you want to extract labels from kwargs
            for label in labels:
                if label in kwargs:
                    label_values[label] = kwargs[label]

            # Use the timer as a context manager
            with timer_metric.labels(**label_values).time():
                return func(*args, **kwargs)

        return wrapped_func

    return decorator


def setup_metrics(app: FastAPI) -> None:
    """
    Setup metrics collection for the FastAPI application.

    Args:
        app: FastAPI application
    """
    # Add metrics middleware
    app.add_middleware(MetricsMiddleware)

    # Add metrics endpoint
    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        return Response(content=generate_latest(), media_type="text/plain")

    logger.info("Metrics collection configured")


def reset_metrics() -> None:
    """
    Reset all metrics (mainly for testing).
    """
    # Clear Prometheus registry
    for collector in list(REGISTRY._collector_to_names.keys()):
        REGISTRY.unregister(collector)

    # Re-register default metrics
    global REQUEST_COUNT, REQUEST_LATENCY, REQUEST_IN_PROGRESS
    global DATABASE_QUERY_LATENCY, CACHE_HIT_COUNT, CACHE_MISS_COUNT, ERROR_COUNT, ACTIVE_USERS

    REQUEST_COUNT = Counter(
        "http_requests_total",
        "Total count of HTTP requests",
        ["method", "endpoint", "status_code"],
    )

    REQUEST_LATENCY = Histogram(
        "http_request_duration_seconds",
        "HTTP request latency in seconds",
        ["method", "endpoint"],
    )

    REQUEST_IN_PROGRESS = Gauge(
        "http_requests_in_progress",
        "Number of HTTP requests in progress",
        ["method", "endpoint"],
    )

    DATABASE_QUERY_LATENCY = Histogram(
        "database_query_duration_seconds",
        "Database query latency in seconds",
        ["query_type"],
    )

    CACHE_HIT_COUNT = Counter(
        "cache_hits_total", "Total count of cache hits", ["cache_type"]
    )

    CACHE_MISS_COUNT = Counter(
        "cache_misses_total", "Total count of cache misses", ["cache_type"]
    )

    ERROR_COUNT = Counter("error_total", "Total count of errors", ["error_type"])

    ACTIVE_USERS = Gauge("active_users", "Number of active users")


def get_metrics() -> Dict:
    """
    Get current metrics values (for internal use or tests).

    Returns:
        Dictionary with metrics data
    """
    return {
        "request_count": REQUEST_COUNT._value,
        "request_latency": REQUEST_LATENCY._sum,
        "request_in_progress": REQUEST_IN_PROGRESS._value,
        "database_query_latency": DATABASE_QUERY_LATENCY._sum,
        "cache_hit_count": CACHE_HIT_COUNT._value,
        "cache_miss_count": CACHE_MISS_COUNT._value,
        "error_count": ERROR_COUNT._value,
        "active_users": ACTIVE_USERS._value,
    }
