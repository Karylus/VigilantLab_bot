import logging
import sys
from typing import Optional

from src.config import settings


def configure_logging(
    level: Optional[int] = None,
    format_str: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Configure logging for the application.

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

    # Create formatters and handlers
    formatter = logging.Formatter(format_str)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Reduce noise from python-telegram-bot
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("telegram.vendor.ptb_urllib3.urllib3.connectionpool").setLevel(
        logging.WARNING
    )

    return logger


# Create module-level logger
logger = configure_logging()
