import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from src.config import settings


def configure_logging(
    level: Optional[int] = None,
    format_str: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Configure logging for the application with rotation support.

    Args:
        level: Logging level (default: settings.LOG_LEVEL)
        format_str: Log format string (default: settings.LOG_FORMAT)
        log_file: Optional file to write logs to

    Returns:
        Configured logger instance
    """
    level = level or settings.LOG_LEVEL
    format_str = format_str or settings.LOG_FORMAT

    # Create logger
    logger = logging.getLogger("watchman")
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers = []

    # Create formatter
    formatter = logging.Formatter(format_str)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation (if specified)
    actual_log_file = log_file or settings.LOG_FILE
    if actual_log_file:
        try:
            # Use RotatingFileHandler for automatic rotation
            file_handler = RotatingFileHandler(
                actual_log_file,
                maxBytes=settings.LOG_MAX_BYTES,  # Default: 10MB
                backupCount=settings.LOG_BACKUP_COUNT,  # Default: keep 5 files
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.info(
                f"Logging to file: {actual_log_file} "
                f"(max {settings.LOG_MAX_BYTES} bytes, "
                f"backup count: {settings.LOG_BACKUP_COUNT})"
            )
        except Exception as e:
            logger.warning(f"Could not setup file logging: {e}")

    # Reduce noise from python-telegram-bot
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("telegram.vendor.ptb_urllib3.urllib3.connectionpool").setLevel(
        logging.WARNING
    )

    return logger


# Create module-level logger
logger = configure_logging()
