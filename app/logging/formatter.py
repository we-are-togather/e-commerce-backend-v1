"""
Production-grade JSON log formatter.

This module defines a custom JSON formatter built on top of
python-json-logger.

Responsibilities:
- Standardize JSON log output
- Add timestamp
- Include request/correlation IDs
- Remove unnecessary default fields
- Ensure ISO-8601 UTC timestamps
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from pythonjsonlogger.json import JsonFormatter

from app.core.context import (
    request_id_ctx,
    correlation_id_ctx,
)


class CustomJsonFormatter(JsonFormatter):
    """
    Custom JSON formatter for production logging.
    """

    def add_fields(
        self,
        log_record: dict,
        record: logging.LogRecord,
        message_dict: dict,
    ) -> None:
        super().add_fields(log_record, record, message_dict)

        log_record["timestamp"] = datetime.now(
            timezone.utc
        ).isoformat()

        log_record["level"] = record.levelname

        log_record["logger"] = record.name

        log_record["request_id"] = request_id_ctx.get()

        log_record["correlation_id"] = correlation_id_ctx.get()

        log_record["module"] = record.module

        log_record["function"] = record.funcName

        log_record["line"] = record.lineno

        log_record["process"] = record.process

        log_record["thread"] = record.thread

        if record.exc_info:
            log_record["exception"] = self.formatException(
                record.exc_info
            )

        # Remove duplicated default fields

        log_record.pop("message", None)
        log_record["message"] = record.getMessage()