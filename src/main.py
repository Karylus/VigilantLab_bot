import signal
import sys

from src.config import settings
from src.handlers import TelegramHandler
from src.utils import logger

# Global application instance for signal handling
_application = None


def _signal_handler(signum, frame):
    """Handle termination signals gracefully."""
    global _application
    signal_name = signal.Signals(signum).name
    logger.info(
        f"Received signal {signal_name}({signum}), initiating graceful shutdown..."
    )

    if _application:
        try:
            _application.stop()
            logger.info("Application stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping application: {e}")

    sys.exit(0)


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""
    try:
        # Handle SIGTERM (termination signal)
        signal.signal(signal.SIGTERM, _signal_handler)
        # Handle SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, _signal_handler)
        logger.debug("Signal handlers registered")
    except Exception as e:
        logger.warning(f"Could not setup signal handlers: {e}")


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
    global _application

    try:
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers()

        # Validate configuration
        if not validate_config():
            sys.exit(1)

        # Create and setup application
        _application = TelegramHandler.create_application()
        TelegramHandler.setup_handlers(_application)

        # Start polling - this is blocking and runs indefinitely
        logger.info("WATCHMAN bot starting...")
        logger.info("Bot is now polling for updates... (Press Ctrl+C to stop)")
        _application.run_polling()

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
