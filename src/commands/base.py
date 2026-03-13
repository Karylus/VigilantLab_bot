from abc import ABC, abstractmethod

from telegram import Update
from telegram.ext import ContextTypes

from src.utils.formatters import OutputFormatter


class BaseCommand(ABC):
    """Base class for all bot commands."""

    name: str
    description: str

    @abstractmethod
    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Execute the command.

        Args:
            update: Telegram update object
            context: Telegram context object
        """
        pass

    async def send_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
        format_code: bool = True,
        title: str = None,
        emoji: str = None,
    ) -> None:
        """
        Send a message to the user with optional formatting.

        Args:
            update: Telegram update object
            context: Telegram context object
            text: Message text
            format_code: Whether to format as code block (default: True for large outputs)
            title: Optional title for the message
            emoji: Optional emoji to prepend to title
        """
        # Auto-detect if we should format as code block
        # If text is long or contains multiple lines, format it
        should_format = format_code and (len(text) > 100 or "\n" in text)

        if should_format:
            formatted_text = OutputFormatter.format_output(
                text, title=title, emoji=emoji, language="text"
            )
        else:
            if title:
                header = f"{emoji} {title}".strip() if emoji else title
                formatted_text = f"{header}\n{text}"
            else:
                formatted_text = text

        # Truncate if necessary
        formatted_text = OutputFormatter.truncate_output(formatted_text)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=formatted_text,
            parse_mode="Markdown",
        )

    async def send_plain_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
        title: str = None,
        emoji: str = None,
    ) -> None:
        """
        Send a message to the user without Markdown parsing (plain text).

        Args:
            update: Telegram update object
            context: Telegram context object
            text: Message text
            title: Optional title for the message
            emoji: Optional emoji to prepend to title
        """
        if title:
            header = f"{emoji} {title}".strip() if emoji else title
            formatted_text = f"{header}\n{text}"
        else:
            formatted_text = text

        # Truncate if necessary
        formatted_text = OutputFormatter.truncate_output(formatted_text)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=formatted_text,
            parse_mode=None,
        )

    async def send_formatted_output(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        output: str,
        title: str = None,
        emoji: str = None,
    ) -> None:
        """
        Send a formatted code block output.

        Args:
            update: Telegram update object
            context: Telegram context object
            output: The output text
            title: Optional title
            emoji: Optional emoji for title
        """
        formatted_text = OutputFormatter.format_output(
            output, title=title, emoji=emoji, language="text"
        )
        formatted_text = OutputFormatter.truncate_output(formatted_text)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=formatted_text,
            parse_mode="Markdown",
        )

    async def send_multiline_output(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        sections: dict,
        title: str = None,
        emoji: str = None,
    ) -> None:
        """
        Send output with multiple sections.

        Args:
            update: Telegram update object
            context: Telegram context object
            sections: Dictionary of {section_name: section_content}
            title: Optional main title
            emoji: Optional emoji for title
        """
        formatted_text = OutputFormatter.format_multiline_output(
            sections, title=title, emoji=emoji
        )
        formatted_text = OutputFormatter.truncate_output(formatted_text)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=formatted_text,
            parse_mode="Markdown",
        )

    async def request_argument(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        argument_name: str,
        example: str = None,
    ) -> None:
        """
        Request an argument from the user via message.

        Args:
            update: Telegram update object
            context: Telegram context object
            argument_name: Name of the argument (e.g., "dominio")
            example: Optional example value
        """
        message = f"❌ Este comando requiere un argumento.\n\n"
        message += f"*Argumento requerido:* {argument_name}\n"

        if example:
            message += f"*Ejemplo:* `/{self.name} {example}`"

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode="Markdown",
        )
