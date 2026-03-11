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
    TG_USER_ID: int = int(os.getenv("TG_USERNAME", "0"))

    # System Configuration
    REBOOT_DELAY: int = 10  # seconds
    TEMP_CRITICAL_THRESHOLD: float = 110.0  # Celsius
    TEMP_THERMAL_ZONE: str = "/sys/class/thermal/thermal_zone0/temp"

    # Logging Configuration
    LOG_LEVEL: int = logging.INFO
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Command timeouts
    COMMAND_TIMEOUT: int = 30  # seconds

    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        """Validate that all required settings are properly configured."""
        if not cls.BOT_TOKEN:
            return False, "BOT_TOKEN not set in environment variables"
        if cls.TG_USER_ID == 0:
            return False, "TG_USERNAME not set in environment variables"
        return True, None


# Create a singleton instance
settings = Settings()
