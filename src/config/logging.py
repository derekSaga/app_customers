"""
This module configures the logging for the application using Loguru.

It intercepts logs from the standard `logging` library to ensure consistent
formatting across all libraries (e.g., Uvicorn, SQLAlchemy). It also
injects a correlation ID into the logs if available.
"""
import logging
import sys
from types import FrameType
from typing import TYPE_CHECKING

from asgi_correlation_id import correlation_id
from loguru import logger

if TYPE_CHECKING:
    from loguru import Record


from src.config.settings import settings


class InterceptHandler(logging.Handler):
    """
    Intercepts logs from the standard `logging` library and
    redirects them to `loguru`.
    This ensures that logs from libraries
    (like Uvicorn, SQLAlchemy) are formatted consistently.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emits a log record.

        Args:
            record: The log record to emit.
        """
        # Tries to get the corresponding level in Loguru
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Finds the origin of the call to maintain the correct stack trace
        frame: FrameType | None = logging.currentframe()
        depth = 2
        while frame:
            filename = frame.f_code.co_filename
            module_name = frame.f_globals.get("__name__", "")

            is_logging = (
                filename == logging.__file__
                or module_name == "logging"
                or module_name.startswith("logging.")
            )
            is_this_file = filename == __file__

            if is_logging or is_this_file:
                frame = frame.f_back
                depth += 1
            else:
                break

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def configure_logging() -> None:
    """
    Configures Loguru and intercepts system logs.
    Should be called at the beginning of execution (Main and Worker).
    """
    # Sets the log level (defaults to INFO if not in settings)
    log_level = settings.LOG_LEVEL

    # Removes default Loguru handlers
    logger.remove()

    # Intercepts logs from the root and sets the level
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(log_level)

    # Removes handlers from existing loggers to avoid duplication
    # and ensures they propagate to the root (which is intercepted)
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # Filter to inject Correlation ID (if available)
    def correlation_id_filter(record: "Record") -> bool:
        """
        Filter to inject the correlation ID into the log record.

        Args:
            record: The log record.

        Returns:
            True if the record should be logged, False otherwise.
        """
        cid = correlation_id.get()
        record["extra"]["correlation_id"] = cid if cid else "N/A"
        return True

    log_format = (
        "<level>{level: <8}</level> | "
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<magenta>{extra[correlation_id]}</magenta> - "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stderr,
        level=log_level,
        format=log_format,
        filter=correlation_id_filter,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )
