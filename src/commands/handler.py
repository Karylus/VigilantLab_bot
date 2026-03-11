import logging

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

logger = logging.getLogger("watchman")

COMMANDS_NEEDING_ARGS = {
    "sslcheck": {
        "arg_name": "dominio",
        "example": "example.com",
        "prompt": "¿Qué dominio quieres verificar?",
    }
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
        if update.effective_user.id != settings.TG_USER_ID:
            logger.warning(
                f"Unauthorized callback attempt from user {update.effective_user.id}"
            )
            return

        query = update.callback_query
        await query.answer()
        callback_data = query.data

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
            cmd_name = CALLBACK_TO_COMMAND[callback_data]
            if cmd_name in self.commands:
                if cmd_name in COMMANDS_NEEDING_ARGS:
                    arg_info = COMMANDS_NEEDING_ARGS[cmd_name]
                    prompt = f"Por favor escribe el {arg_info['arg_name']}:\n\nEjemplo: {arg_info['example']}"
                    await query.edit_message_text(text=prompt)
                    context.user_data["waiting_for_arg"] = cmd_name
                    return

                try:
                    await query.edit_message_text(text="⏳ Ejecutando comando...")
                    await self.commands[cmd_name].execute(update, context)

                    security_menu = SecurityMenu()
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=security_menu.get_text(),
                        reply_markup=security_menu.get_keyboard(),
                        parse_mode="Markdown",
                    )
                except Exception as e:
                    logger.error(f"Error executing command {cmd_name}: {str(e)}")
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"❌ Error al ejecutar comando:\n`{str(e)}`",
                        parse_mode="Markdown",
                    )
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
        if "waiting_for_arg" not in context.user_data:
            return

        cmd_name = context.user_data.get("waiting_for_arg")
        if not cmd_name:
            return

        arg_value = update.message.text.strip()
        context.args = [arg_value]
        context.user_data["waiting_for_arg"] = None

        if cmd_name in self.commands:
            try:
                await self.commands[cmd_name].execute(update, context)
                security_menu = SecurityMenu()
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=security_menu.get_text(),
                    reply_markup=security_menu.get_keyboard(),
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.error(f"Error executing {cmd_name}: {str(e)}")
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"❌ Error: {str(e)}",
                    parse_mode="Markdown",
                )

    def _get_command_handler(self, cmd_name: str):
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            if cmd_name in self.commands:
                await self.commands[cmd_name].execute(update, context)
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"❌ Comando desconocido: /{cmd_name}",
                )
                logger.warning(f"Unknown command: {cmd_name}")

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
