import logging
import sys
import time
from contextvars import ContextVar
from typing import Any

from pythonjsonlogger import jsonlogger

# Context variables for request tracking
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="unknown")
user_id_ctx: ContextVar[str | None] = ContextVar("user_id", default=None)
operation_ctx: ContextVar[str | None] = ContextVar("operation", default=None)


class StructuredJsonFormatter(jsonlogger.JsonFormatter):
    """Enhanced JSON formatter with consistent structured logging."""

    def add_fields(
        self, log_record: dict[str, Any], record: logging.LogRecord, message_dict: dict[str, Any]
    ) -> None:
        super().add_fields(log_record, record, message_dict)

        # Timestamp in ISO 8601 format
        log_record["timestamp"] = self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        log_record["level"] = record.levelname

        # Service context
        log_record["service"] = getattr(record, "service", "unknown")
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno

        # Request context from contextvars
        log_record["request_id"] = request_id_ctx.get()
        if user_id := user_id_ctx.get():
            log_record["user_id"] = user_id
        if operation := operation_ctx.get():
            log_record["operation"] = operation

        # Additional context from extra
        if hasattr(record, "duration_ms"):
            log_record["duration_ms"] = record.duration_ms
        if hasattr(record, "status_code"):
            log_record["status_code"] = record.status_code
        if hasattr(record, "error_type"):
            log_record["error_type"] = record.error_type


def setup_logging(service_name: str, log_level: str = "INFO") -> logging.Logger:
    """Setup structured JSON logging for a service.

    Args:
        service_name: Name of the service (e.g. 'products', 'inventory')
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, log_level.upper()))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = StructuredJsonFormatter(
            "%(timestamp)s %(level)s %(service)s %(request_id)s %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Add service name to all records
    old_factory = logging.getLogRecordFactory()

    def record_factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
        record = old_factory(*args, **kwargs)
        record.service = service_name
        return record

    logging.setLogRecordFactory(record_factory)
    logger.propagate = False
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance by name."""
    return logging.getLogger(name)


class LogContext:
    """Context manager for adding structured context to logs."""

    def __init__(
        self,
        request_id: str | None = None,
        user_id: str | None = None,
        operation: str | None = None,
    ):
        self.request_id = request_id
        self.user_id = user_id
        self.operation = operation
        self.tokens = {}

    def __enter__(self) -> "LogContext":
        if self.request_id:
            self.tokens["request_id"] = request_id_ctx.set(self.request_id)
        if self.user_id:
            self.tokens["user_id"] = user_id_ctx.set(self.user_id)
        if self.operation:
            self.tokens["operation"] = operation_ctx.set(self.operation)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        for token in self.tokens.values():
            token.var.reset(token)


class LogTimer:
    """Context manager for timing operations and logging duration."""

    def __init__(self, logger: logging.Logger, operation: str, level: int = logging.INFO):
        self.logger = logger
        self.operation = operation
        self.level = level
        self.start_time = 0.0

    def __enter__(self) -> "LogTimer":
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        duration_ms = (time.time() - self.start_time) * 1000
        extra = {"duration_ms": round(duration_ms, 2), "operation": self.operation}

        if exc_type:
            extra["error_type"] = exc_type.__name__
            self.logger.error(f"{self.operation} failed", extra=extra, exc_info=True)
        else:
            self.logger.log(self.level, f"{self.operation} completed", extra=extra)

