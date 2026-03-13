import logging
import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)


class Settings:
    """Centralized configuration for the WATCHMAN bot."""

    # Telegram Configuration
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

    # Handle TG_USER_ID with proper error handling
    _tg_user_id_str = os.getenv("TG_USER_ID", "0")
    try:
        TG_USER_ID: int = int(_tg_user_id_str)
    except ValueError:
        TG_USER_ID = 0

    # System Configuration
    REBOOT_DELAY: int = int(os.getenv("REBOOT_DELAY", "10"))
    TEMP_CRITICAL_THRESHOLD: float = float(
        os.getenv("TEMP_CRITICAL_THRESHOLD", "110.0")
    )
    TEMP_THERMAL_ZONE: str = os.getenv(
        "TEMP_THERMAL_ZONE", "/sys/class/thermal/thermal_zone0/temp"
    )

    # Logging Configuration
    LOG_LEVEL: int = getattr(logging, os.getenv("LOG_LEVEL", "INFO"))
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", None)
    LOG_MAX_BYTES: int = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    # Command timeouts
    COMMAND_TIMEOUT: int = int(os.getenv("COMMAND_TIMEOUT", "30"))
    MAX_OUTPUT_SIZE: int = int(os.getenv("MAX_OUTPUT_SIZE", "1048576"))  # 1MB

    # SSL Configuration
    SSL_TIMEOUT: int = int(os.getenv("SSL_TIMEOUT", "15"))

    # Rate Limiting
    RATE_LIMIT_CALLS: int = int(os.getenv("RATE_LIMIT_CALLS", "10"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        """Validate that all required settings are properly configured."""
        if not cls.BOT_TOKEN:
            return False, "BOT_TOKEN not set in environment variables"
        if cls.TG_USER_ID == 0:
            return False, "TG_USER_ID not set or invalid in environment variables"
        return True, None


# Create a singleton instance
settings = Settings()
