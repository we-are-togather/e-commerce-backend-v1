"""
Logging filters.

Responsibilities
----------------
- Skip noisy endpoints (health checks, docs, etc.)
- Mask sensitive information
- Attach request context to every LogRecord

These filters are designed to be used by Python's logging module.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable

from app.core.context import (
    correlation_id_ctx,
    request_id_ctx,
)


class RequestContextFilter(logging.Filter):
    """
    Inject request context into every log record.

    This makes request_id and correlation_id available
    to formatters without requiring every logging call
    to pass them manually.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        record.correlation_id = correlation_id_ctx.get()

        return True


class SensitiveDataFilter(logging.Filter):
    """
    Mask sensitive values stored in the LogRecord.

    NOTE:
    This filter only masks attributes already attached
    to the LogRecord.

    It does NOT inspect request bodies.
    """

    MASK = "********"

    SENSITIVE_FIELDS = {
        "authorization",
        "cookie",
        "set_cookie",
        "password",
        "access_token",
        "refresh_token",
        "secret",
        "api_key",
        "otp",
        "cvv",
        "credit_card",
    }

    def filter(self, record: logging.LogRecord) -> bool:

        for field in self.SENSITIVE_FIELDS:
            if hasattr(record, field):
                setattr(record, field, self.MASK)

        return True


class EndpointFilter(logging.Filter):
    """
    Skip logging for noisy endpoints.

    Typical examples:

    - /health
    - /metrics
    - /docs
    - /redoc
    - /openapi.json
    """

    EXCLUDED_PATHS = {
        "/health",
        "/metrics",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico",
    }

    def filter(self, record: logging.LogRecord) -> bool:

        path = getattr(record, "path", None)

        if path in self.EXCLUDED_PATHS:
            return False

        return True


class MinimumLevelFilter(logging.Filter):
    """
    Example custom level filter.

    Useful when different handlers
    require different minimum levels.
    """

    def __init__(self, level: int):
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= self.level