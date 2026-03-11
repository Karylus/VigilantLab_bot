import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.commands.base import BaseCommand
from src.services import SystemService

logger = logging.getLogger("watchman")


class UpdateCommand(BaseCommand):
    """Command to update system packages."""

    name = "update"
    description = "Actualiza los paquetes del sistema"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Update system packages."""
        await self.send_message(
            update,
            context,
            "Se van a actualizar los paquetes del sistema. Por favor espera...",
        )
        success, message = await SystemService.update_packages()
        await self.send_message(update, context, message)
        logger.warning(f"Update command executed. Success: {success}")


class RemountCommand(BaseCommand):
    """Command to remount filesystems."""

    name = "remount"
    description = "Remonta todos los sistemas de archivos"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Remount filesystems."""
        success, message = await SystemService.remount_disks()
        await self.send_message(update, context, message)
        logger.info(f"Remount command executed. Success: {success}")
