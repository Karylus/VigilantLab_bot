import logging
import subprocess
from typing import Tuple

from src.config import settings

logger = logging.getLogger("watchman")

# Whitelist of allowed commands for security
ALLOWED_COMMANDS = {
    # Networking
    "ss",
    "netstat",
    "ip",
    "ping",
    "curl",
    "wget",
    # Process management
    "ps",
    "top",
    "systemctl",
    "service",
    # File operations
    "find",
    "cat",
    "ls",
    "grep",
    "mount",
    # System
    "sudo",
    "apt",
    "systemd-tmpfiles",
    # Security
    "openssl",
    "lastb",
    "who",
    "w",
    # Bash for piped commands
    "bash",
}

# Maximum output size (1MB)
MAX_OUTPUT_SIZE = 1024 * 1024


class CommandExecutor:
    """Executes shell commands with security restrictions and output limits."""

    @staticmethod
    async def execute(
        cmd: list[str],
        timeout: int = settings.COMMAND_TIMEOUT,
        max_output_size: int = MAX_OUTPUT_SIZE,
    ) -> Tuple[bool, str]:
        """
        Execute a shell command and return success status and output.

        Args:
            cmd: List of command arguments
            timeout: Command timeout in seconds
            max_output_size: Maximum output size in bytes (default: 1MB)

        Returns:
            Tuple of (success: bool, output: str)

        Raises:
            ValueError: If command is not in whitelist
        """
        # Validate first command in list
        if not cmd:
            return False, "Error: Empty command"

        main_cmd = cmd[0]
        if main_cmd not in ALLOWED_COMMANDS:
            logger.warning(f"Command not in whitelist: {main_cmd}")
            return False, f"Error: Command '{main_cmd}' is not allowed"

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                stdin=subprocess.DEVNULL,  # No input allowed
            )

            output = (result.stdout or "") + (result.stderr or "")

            # Truncate if too large
            if len(output) > max_output_size:
                output = (
                    output[:max_output_size]
                    + "\n\n[Output truncated - exceeded max size]"
                )
                logger.warning(
                    f"Command output truncated: {len(output)} > {max_output_size}"
                )

            success = result.returncode == 0
            return success, output.strip()

        except subprocess.TimeoutExpired:
            return False, f"Command timed out after {timeout} seconds"
        except Exception as e:
            logger.error(f"Error executing {main_cmd}: {str(e)}")
            return False, "Error executing command"
