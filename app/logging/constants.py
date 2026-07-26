"""
Logging constants.

This module contains immutable constants used throughout the
logging subsystem.

Environment-specific values (e.g. log level, excluded paths)
should be configured in settings.py instead of here.
"""

from __future__ import annotations

from typing import Final

# ============================================================================
# Logger
# ============================================================================

LOGGER_NAME: Final[str] = "app"

# ============================================================================
# Date & Time
# ============================================================================

ISO8601_DATETIME_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%S.%fZ"

# ============================================================================
# Request Headers
# ============================================================================

REQUEST_ID_HEADER: Final[str] = "X-Request-ID"

CORRELATION_ID_HEADER: Final[str] = "X-Correlation-ID"

# ============================================================================
# Request State Keys
# ============================================================================

REQUEST_ID_STATE_KEY: Final[str] = "request_id"

CORRELATION_ID_STATE_KEY: Final[str] = "correlation_id"

USER_STATE_KEY: Final[str] = "user"

TENANT_STATE_KEY: Final[str] = "tenant"

LOCALE_STATE_KEY: Final[str] = "locale"

# ============================================================================
# Log Record Attributes
# ============================================================================

LOG_REQUEST_ID: Final[str] = "request_id"

LOG_CORRELATION_ID: Final[str] = "correlation_id"

LOG_USER_ID: Final[str] = "user_id"

LOG_METHOD: Final[str] = "method"

LOG_PATH: Final[str] = "path"

LOG_QUERY: Final[str] = "query"

LOG_STATUS_CODE: Final[str] = "status_code"

LOG_CLIENT_IP: Final[str] = "client_ip"

LOG_USER_AGENT: Final[str] = "user_agent"

LOG_DURATION: Final[str] = "duration_ms"

LOG_REQUEST_SIZE: Final[str] = "request_size"

LOG_RESPONSE_SIZE: Final[str] = "response_size"

LOG_EXCEPTION: Final[str] = "exception"

# ============================================================================
# Sensitive Headers
# ============================================================================

SENSITIVE_HEADERS: Final[frozenset[str]] = frozenset(
    {
        "authorization",
        "cookie",
        "set-cookie",
        "proxy-authorization",
        "x-api-key",
        "api-key",
        "access-token",
        "refresh-token",
    }
)

# ============================================================================
# Sensitive Payload Fields
# ============================================================================

SENSITIVE_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "password",
        "old_password",
        "new_password",
        "confirm_password",
        "token",
        "access_token",
        "refresh_token",
        "otp",
        "secret",
        "client_secret",
        "api_key",
        "credit_card",
        "card_number",
        "cvv",
        "pin",
    }
)

MASK_VALUE: Final[str] = "********"

# ============================================================================
# Default Excluded Paths
# ============================================================================

DEFAULT_EXCLUDED_PATHS: Final[frozenset[str]] = frozenset(
    {
        "/health",
        "/metrics",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico",
    }
)

# ============================================================================
# HTTP Methods
# ============================================================================

HTTP_GET: Final[str] = "GET"

HTTP_POST: Final[str] = "POST"

HTTP_PUT: Final[str] = "PUT"

HTTP_PATCH: Final[str] = "PATCH"

HTTP_DELETE: Final[str] = "DELETE"

HTTP_OPTIONS: Final[str] = "OPTIONS"

HTTP_HEAD: Final[str] = "HEAD"

# ============================================================================
# Common Log Messages
# ============================================================================

LOG_REQUEST_STARTED: Final[str] = "Request started"

LOG_REQUEST_COMPLETED: Final[str] = "Request completed"

LOG_REQUEST_FAILED: Final[str] = "Request failed"

LOG_UNHANDLED_EXCEPTION: Final[str] = "Unhandled exception"

LOG_SLOW_REQUEST: Final[str] = "Slow request detected"