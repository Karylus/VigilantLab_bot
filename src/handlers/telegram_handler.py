import logging

from telegram.ext import ApplicationBuilder

from src.commands.handler import CommandHandlerManager
from src.config import settings

logger = logging.getLogger("watchman")


class TelegramHandler:
    """Handles Telegram bot initialization and setup."""

    @staticmethod
    def create_application():
        """
        Create and configure the Telegram bot application.

        Returns:
            Configured Application instance
        """
        application = ApplicationBuilder().token(settings.BOT_TOKEN).build()
        logger.info("Telegram application created")
        return application

    @staticmethod
    def setup_handlers(application) -> None:
        """
        Set up all command handlers for the application.

        Args:
            application: Telegram application object
        """
        cmd_handler = CommandHandlerManager()
        cmd_handler.register_handlers(application)
        logger.info("Command handlers registered")
