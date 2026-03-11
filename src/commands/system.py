import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.commands.base import BaseCommand
from src.services import SystemService

logger = logging.getLogger("watchman")


class StatusCommand(BaseCommand):
    """Command to check system status."""

    name = "status"
    description = "Muestra si el home lab está encendido"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Check and report system status."""
        is_online, message = await SystemService.check_status()
        await self.send_message(update, context, message)
        logger.info(f"Status command executed. Online: {is_online}")


class TemperatureCommand(BaseCommand):
    """Command to check CPU temperature."""

    name = "temp"
    description = "Muestra la temperatura de la CPU"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Check and report CPU temperature."""
        success, message, temp = await SystemService.get_temperature()
        await self.send_message(update, context, message)
        logger.info(f"Temperature command executed. Temp: {temp}°C")


class RebootCommand(BaseCommand):
    """Command to schedule a system reboot."""

    name = "reboot"
    description = "Reinicia el home lab"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Schedule system reboot."""
        await self.send_message(update, context, "Solicitando reinicio del home lab...")
        success, message = await SystemService.reboot()
        await self.send_message(update, context, message)
        logger.warning(f"Reboot command executed. Success: {success}")
