import logging
import re
import subprocess
from typing import Tuple

from src.config import settings
from src.services.command_executor import CommandExecutor

logger = logging.getLogger("watchman")


class SystemService:
    """Handles system-related operations like reboot, status, temperature, etc."""

    @staticmethod
    async def reboot(delay_seconds: int = settings.REBOOT_DELAY) -> Tuple[bool, str]:
        """
        Schedule a system reboot after a delay.

        Args:
            delay_seconds: Delay before reboot in seconds

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            cmd = ["bash", "-lc", f"(sleep {delay_seconds} && sudo reboot) &"]
            success, output = await CommandExecutor.execute(cmd)

            if success:
                message = f"Reinicio programado en {delay_seconds} segundos."
            else:
                message = f"No se pudo programar el reinicio. Detalles: {output}"

            return success, message
        except Exception as e:
            logger.error(f"Error in reboot: {str(e)}")
            return False, f"Error al programar reinicio: {str(e)}"

    @staticmethod
    async def check_status() -> Tuple[bool, str]:
        """
        Check system status with a simple ping.

        Returns:
            Tuple of (is_online: bool, message: str)
        """
        try:
            cmd = ["ping", "127.0.0.1", "-c", "3"]
            success, output = await CommandExecutor.execute(cmd)

            if success:
                message = "El home lab está funcionando correctamente."
            else:
                message = f"El home lab no está funcionando. Detalles: {output}"

            return success, message
        except Exception as e:
            logger.error(f"Error checking status: {str(e)}")
            return False, f"Error al verificar estado: {str(e)}"

    @staticmethod
    async def get_temperature() -> Tuple[bool, str, float]:
        """
        Read CPU temperature from thermal zone.

        Returns:
            Tuple of (success: bool, message: str, temperature: float)
        """
        try:
            cmd = ["cat", settings.TEMP_THERMAL_ZONE]
            success, output = await CommandExecutor.execute(cmd)

            if not success or not output:
                return False, "No se pudo leer la temperatura", 0.0

            # Parse temperature value
            try:
                temp_milli = int(output.strip())
            except ValueError:
                match = re.search(r"-?\d+", output)
                if match:
                    temp_milli = int(match.group())
                else:
                    return False, f"Valor de temperatura inválido: {output}", 0.0

            temp_c = temp_milli / 1000.0

            # Check if critical
            is_critical = temp_c > settings.TEMP_CRITICAL_THRESHOLD
            critical_msg = (
                f" ⚠️ CRÍTICA: supera {settings.TEMP_CRITICAL_THRESHOLD}°C"
                if is_critical
                else ""
            )

            message = f"Temperatura actual: {temp_c:.1f}°C{critical_msg}"
            return True, message, temp_c
        except Exception as e:
            logger.error(f"Error reading temperature: {str(e)}")
            return False, f"Error al obtener temperatura: {str(e)}", 0.0

    @staticmethod
    async def update_packages() -> Tuple[bool, str]:
        """
        Update system packages using apt.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # First update package lists
            update_cmd = ["sudo", "apt", "update"]
            update_success, update_output = await CommandExecutor.execute(
                update_cmd, timeout=None
            )

            if not update_success:
                return False, f"Error al actualizar repositorios: {update_output}"

            # Then upgrade packages
            upgrade_cmd = ["sudo", "apt", "upgrade", "-y"]
            upgrade_success, upgrade_output = await CommandExecutor.execute(
                upgrade_cmd, timeout=None
            )

            if not upgrade_success:
                return False, f"Error al actualizar paquetes: {upgrade_output}"

            return True, "Actualización de paquetes completada exitosamente."
        except Exception as e:
            logger.error(f"Error updating packages: {str(e)}")
            return False, f"Error al actualizar paquetes: {str(e)}"

    @staticmethod
    async def remount_disks() -> Tuple[bool, str]:
        """
        Remount all filesystems using mount -a.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            cmd = ["sudo", "mount", "-a"]
            success, output = await CommandExecutor.execute(cmd)

            if success:
                message = "Los discos se han montado correctamente."
            else:
                message = f"Error al montar los discos: {output}"

            return success, message
        except Exception as e:
            logger.error(f"Error remounting disks: {str(e)}")
            return False, f"Error al montar discos: {str(e)}"
