import asyncio
import logging
from typing import Callable

from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.commands.maintenance import RemountCommand, UpdateCommand
from src.commands.security import (
    ConnectionsCommand,
    CronJobsCommand,
    FailedLoginsCommand,
    FirewallRulesCommand,
    FirewallStatusCommand,
    NetworkProcessesCommand,
    OpenPortsCommand,
    ServiceSecurityCommand,
    SessionsCommand,
    SSHKeysCommand,
    SSLCertificateCommand,
    SudoersCheckCommand,
    SuidFilesCommand,
    SystemAuditCommand,
    ThreatsCommand,
    TopProcessesCommand,
)
from src.commands.system import RebootCommand, StatusCommand, TemperatureCommand
from src.config import settings
from src.utils.menus import (
    CALLBACK_TO_COMMAND,
    MENU_CALLBACKS,
    MainMenu,
    SecurityMenu,
)
from src.utils.rate_limiter import RateLimiter

logger = logging.getLogger("watchman")

# Initialize rate limiter
rate_limiter = RateLimiter(
    max_calls=settings.RATE_LIMIT_CALLS, time_window=settings.RATE_LIMIT_WINDOW
)


class CommandMetadata:
    """Metadata for commands that require arguments."""

    def __init__(self, name: str, example: str, prompt: str):
        self.name = name
        self.example = example
        self.prompt = prompt


COMMANDS_NEEDING_ARGS = {
    "sslcheck": CommandMetadata(
        name="dominio",
        example="example.com",
        prompt="¿Qué dominio quieres verificar?",
    ),
}


class CommandHandlerManager:
    """Manages command registration and execution."""

    def __init__(self):
        """Initialize command handler with all available commands."""
        self.commands = {
            # System commands
            "status": StatusCommand(),
            "temp": TemperatureCommand(),
            "reboot": RebootCommand(),
            "update": UpdateCommand(),
            "remount": RemountCommand(),
            # Security commands
            "connections": ConnectionsCommand(),
            "openports": OpenPortsCommand(),
            "networkproc": NetworkProcessesCommand(),
            "firewall": FirewallStatusCommand(),
            "fwrules": FirewallRulesCommand(),
            "failedlogins": FailedLoginsCommand(),
            "sessions": SessionsCommand(),
            "sshkeys": SSHKeysCommand(),
            "sudoers": SudoersCheckCommand(),
            "topproc": TopProcessesCommand(),
            "services": ServiceSecurityCommand(),
            "sslcheck": SSLCertificateCommand(),
            "suidfiles": SuidFilesCommand(),
            "cronjobs": CronJobsCommand(),
            "audit": SystemAuditCommand(),
            "threats": ThreatsCommand(),
        }

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command - show main menu."""
        menu = MainMenu()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=menu.get_text(),
            reply_markup=menu.get_keyboard(),
            parse_mode="Markdown",
        )
        logger.info("Start command executed - main menu shown")

    async def menu_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        user_id = update.effective_user.id
        if user_id != settings.TG_USER_ID:
            logger.warning(
                f"SECURITY: Unauthorized callback attempt from user {user_id}"
            )
            return

        query = update.callback_query
        await query.answer()
        callback_data = query.data
        logger.debug(f"Menu callback received: {callback_data} from user {user_id}")

        if callback_data in MENU_CALLBACKS:
            menu_class = MENU_CALLBACKS[callback_data]
            menu = menu_class()
            await query.edit_message_text(
                text=menu.get_text(),
                reply_markup=menu.get_keyboard(),
                parse_mode="Markdown",
            )
            logger.info(f"Menu navigation: {callback_data}")

        elif callback_data in CALLBACK_TO_COMMAND:
            cmd_name = CALLBACK_TO_COMMAND.get(callback_data)
            if not cmd_name:
                logger.warning(f"Invalid callback data: {callback_data}")
                await query.answer("Error: Comando no disponible", show_alert=True)
                return

            if cmd_name not in self.commands:
                logger.warning(f"Command not registered: {cmd_name}")
                await query.answer("Error: Comando no registrado", show_alert=True)
                return

            # Rate limiting check
            user_id = update.effective_user.id
            if not rate_limiter.is_allowed(user_id):
                wait_time = rate_limiter.get_wait_time(user_id)
                logger.warning(
                    f"SECURITY: Rate limit exceeded for user {user_id}: {cmd_name}"
                )
                await query.answer(
                    f"⏱️ Demasiados comandos. Espera {wait_time}s", show_alert=False
                )
                return

            logger.info(f"AUDIT: Executing command: {cmd_name} by user {user_id}")

            if cmd_name in COMMANDS_NEEDING_ARGS:
                arg_info = COMMANDS_NEEDING_ARGS[cmd_name]
                prompt = f"Por favor escribe el {arg_info.name}:\n\nEjemplo: {arg_info.example}"
                await query.edit_message_text(text=prompt)
                context.user_data["waiting_for_arg"] = cmd_name
                return

            try:
                await query.edit_message_text(text="⏳ Ejecutando comando...")
                await self.commands[cmd_name].execute(update, context)
                logger.info(
                    f"AUDIT: Command {cmd_name} completed successfully by user {user_id}"
                )

                security_menu = SecurityMenu()
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=security_menu.get_text(),
                    reply_markup=security_menu.get_keyboard(),
                    parse_mode="Markdown",
                )
            except asyncio.TimeoutError:
                logger.error(
                    f"SECURITY: Command timeout for {cmd_name} from user {user_id}"
                )
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="⏱️ El comando tardó demasiado. Intenta de nuevo.",
                    parse_mode="Markdown",
                )
            except PermissionError:
                logger.error(
                    f"SECURITY: Permission denied for command {cmd_name} from user {user_id}"
                )
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="🔒 Permiso denegado. Algunos comandos requieren sudo.",
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error(
                    f"ERROR: Command {cmd_name} failed for user {user_id}: {e}",
                    exc_info=True,
                )
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Error al ejecutar comando. Verifica los logs.",
                    parse_mode="Markdown",
                )
            finally:
                security_menu = SecurityMenu()
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=security_menu.get_text(),
                    reply_markup=security_menu.get_keyboard(),
                    parse_mode="Markdown",
                )

    async def handle_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        user_id = update.effective_user.id
        if "waiting_for_arg" not in context.user_data:
            return

        cmd_name = context.user_data.get("waiting_for_arg")
        if not cmd_name:
            return

        arg_value = update.message.text.strip()
        context.args = [arg_value]
        context.user_data["waiting_for_arg"] = None

        logger.info(
            f"AUDIT: Executing command {cmd_name} with argument from user {user_id}"
        )

        if cmd_name in self.commands:
            try:
                await self.commands[cmd_name].execute(update, context)
                logger.info(
                    f"AUDIT: Command {cmd_name} completed successfully with argument from user {user_id}"
                )
                security_menu = SecurityMenu()
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=security_menu.get_text(),
                    reply_markup=security_menu.get_keyboard(),
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error(
                    f"ERROR: Command {cmd_name} failed for user {user_id}: {e}",
                    exc_info=True,
                )
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Error al ejecutar comando.",
                    parse_mode="Markdown",
                )

    def _get_command_handler(self, cmd_name: str) -> Callable:
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            user_id = update.effective_user.id
            if cmd_name in self.commands:
                logger.info(
                    f"AUDIT: Direct command /{cmd_name} executed by user {user_id}"
                )
                await self.commands[cmd_name].execute(update, context)
            else:
                logger.warning(
                    f"SECURITY: Unknown command attempted: /{cmd_name} by user {user_id}"
                )
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"❌ Comando desconocido: /{cmd_name}",
                )

        return wrapper

    def register_handlers(self, application) -> None:
        start_handler = CommandHandler(
            "start",
            self.start,
            filters=filters.User(settings.TG_USER_ID),
        )
        application.add_handler(start_handler)

        callback_handler = CallbackQueryHandler(self.menu_callback)
        application.add_handler(callback_handler)

        message_handler = MessageHandler(
            filters.TEXT & filters.User(settings.TG_USER_ID),
            self.handle_message,
        )
        application.add_handler(message_handler)

        for cmd_name in self.commands:
            handler = CommandHandler(
                cmd_name,
                self._get_command_handler(cmd_name),
                filters=filters.User(settings.TG_USER_ID),
            )
            application.add_handler(handler)
