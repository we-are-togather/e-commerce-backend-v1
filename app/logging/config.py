"""
Logging configuration.

This module defines the logging configuration used by the
logging subsystem.

It does not read environment variables directly.
Instead, it consumes values from the application's Settings
instance (app.core.config.settings).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.core.config import settings
from app.logging.constants import DEFAULT_EXCLUDED_PATHS


@dataclass(slots=True, frozen=True)
class LoggingConfig:
    """
    Immutable logging configuration.

    All values are loaded from the global application settings.
    """

    # =========================================================================
    # General
    # =========================================================================

    app_name: str = settings.APP_NAME

    environment: str = settings.APP_ENV

    logger_name: str = settings.APP_NAME

    level: str = settings.LOG_LEVEL.upper()

    json_logs: bool = settings.LOG_JSON

    # =========================================================================
    # Output
    # =========================================================================

    console_enabled: bool = settings.LOG_TO_CONSOLE

    file_enabled: bool = settings.LOG_TO_FILE

    log_directory: Path = Path(settings.LOG_DIRECTORY)

    # =========================================================================
    # Rotation
    # =========================================================================

    max_file_size_mb: int = settings.LOG_MAX_FILE_SIZE_MB

    backup_count: int = settings.LOG_BACKUP_COUNT

    retention_days: int = settings.LOG_RETENTION_DAYS

    # =========================================================================
    # Performance
    # =========================================================================

    slow_request_threshold_ms: int = settings.SLOW_REQUEST_THRESHOLD_MS

    # =========================================================================
    # Request Logging
    # =========================================================================

    excluded_paths: frozenset[str] = field(
        default_factory=lambda: frozenset(
            settings.LOG_EXCLUDED_PATHS
            if settings.LOG_EXCLUDED_PATHS
            else DEFAULT_EXCLUDED_PATHS
        )
    )

    # =========================================================================
    # Sensitive Data
    # =========================================================================

    mask_sensitive_headers: bool = True

    mask_sensitive_payload: bool = True


logging_config = LoggingConfig()