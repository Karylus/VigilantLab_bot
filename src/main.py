import sys

from src.config import settings
from src.handlers import TelegramHandler
from src.utils import logger


def validate_config() -> bool:
    """Validate configuration before starting."""
    valid, error = settings.validate()
    if not valid:
        logger.error(f"Configuration error: {error}")
        return False
    logger.info("Configuration validated successfully")
    return True


def main() -> None:
    """Main entry point for the bot."""
    try:
        # Validate configuration
        if not validate_config():
            sys.exit(1)

        # Create and setup application
        application = TelegramHandler.create_application()
        TelegramHandler.setup_handlers(application)

        # Start polling - this is blocking and runs indefinitely
        logger.info("WATCHMAN bot starting...")
        logger.info("Bot is now polling for updates... (Press Ctrl+C to stop)")
        application.run_polling()

    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        sys.exit(1)
