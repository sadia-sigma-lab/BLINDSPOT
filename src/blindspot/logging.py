"""Logging configuration for the benchmark framework."""

from __future__ import annotations

import logging
import logging.config
from typing import Any


_REDACTION_PATTERNS: list[str] = []


def add_redaction_pattern(pattern: str) -> None:
    """Register a string pattern to be redacted from log output."""
    _REDACTION_PATTERNS.append(pattern)


class RedactingFilter(logging.Filter):
    """Log filter that replaces registered sensitive patterns with [REDACTED]."""

    def filter(self, record: logging.LogRecord) -> bool:
        if _REDACTION_PATTERNS:
            msg = record.getMessage()
            for pattern in _REDACTION_PATTERNS:
                msg = msg.replace(pattern, "[REDACTED]")
            record.msg = msg
            record.args = ()
        return True


def configure_logging(level: str = "INFO", json_logs: bool = False) -> None:
    """Set up the root logger for the benchmark package."""
    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "redacting": {"()": RedactingFilter},
        },
        "formatters": {
            "default": {
                "format": "%(asctime)s %(levelname)-8s %(name)s %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "filters": ["redacting"],
            },
        },
        "loggers": {
            "blindspot": {
                "level": level,
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }
    logging.config.dictConfig(config)
