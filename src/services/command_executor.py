import logging
import subprocess
from typing import Tuple

from src.config import settings

logger = logging.getLogger("watchman")


class CommandExecutor:
    """Executes shell commands and returns output and status."""

    @staticmethod
    async def execute(
        cmd: list[str],
        timeout: int = settings.COMMAND_TIMEOUT,
    ) -> Tuple[bool, str]:
        """
        Execute a shell command and return success status and output.

        Args:
            cmd: List of command arguments
            timeout: Command timeout in seconds

        Returns:
            Tuple of (success: bool, output: str)
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output = (result.stdout or "") + (result.stderr or "")
            success = result.returncode == 0
            return success, output.strip()
        except subprocess.TimeoutExpired:
            return False, f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, f"Error executing command: {str(e)}"
