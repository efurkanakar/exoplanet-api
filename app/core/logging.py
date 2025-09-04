"""
Custom logging configuration for the Exoplanet Database API.

This module configures both console and rotating file logging with support for
per-request correlation IDs (`request_id`). Each log entry includes a request ID,
log level, logger name, and timestamp for easier debugging and traceability.

"""

import logging
from logging.config import dictConfig
import os
import uuid
from app.core.config import settings


class RequestIdFilter(logging.Filter):
    """
    Logging filter that attaches a request_id to each log record.

    If the record does not already have a `request_id` attribute, it is set to
    a default value ('-'). This allows log entries to be correlated per request
    for debugging and monitoring purposes.

    Attributes:
        request_id (str): The correlation ID to tag log messages with.
    """

    def __init__(self, name: str = "") -> None:
        """Initialize the filter with a default request_id of '-'. """
        super().__init__(name)
        self.request_id = "-"

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Inject the request_id into the log record if missing.

        Args:
            record (logging.LogRecord): The log record being processed.

        Returns:
            bool: Always True to allow the log record to proceed.
        """
        if not hasattr(record, "request_id"):
            record.request_id = self.request_id
        return True


# Global request ID filter (injected into all handlers)
REQUEST_ID_FILTER = RequestIdFilter()


def setup_logging() -> None:
    """
    Configure logging for the application.

    Sets up both console and file handlers with a unified log format.
    The file handler uses `RotatingFileHandler` to limit log size and
    keep backup logs. Adds the global `REQUEST_ID_FILTER` to all handlers.

    Log format:
        timestamp | LEVEL | logger_name | rid=<request_id> | message

    Raises:
        OSError: If the log directory cannot be created.
    """
    log_level = settings.LOG_LEVEL
    log_file = settings.LOG_FILE

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "request_id": {
                "()": RequestIdFilter
            }
        },
        "formatters": {
            "console": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | rid=%(request_id)s | %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
                "level": log_level,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_file,
                "maxBytes": 10_000_000,   # ~10MB
                "backupCount": 5,
                "formatter": "console",
                "level": log_level,
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": log_level
        },
        "loggers": {
            "uvicorn": {"level": log_level},
            "uvicorn.error": {"level": log_level},
            "uvicorn.access": {"level": log_level},
            "watchfiles": {"level": "WARNING"},
            "watchfiles.main": {"level": "WARNING"},
        }
    })

    root = logging.getLogger()
    for h in root.handlers:
        h.addFilter(REQUEST_ID_FILTER)


def new_request_id() -> str:
    """
    Generate a new random request ID.

    Returns:
        str: A short 8-character hex string suitable for tagging logs.
    """
    return uuid.uuid4().hex[:8]
