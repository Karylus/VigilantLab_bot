"""
Formatting utilities for command output.

This module provides functions to format command results in a more readable way,
with proper code blocks, styling, and structure for Telegram messages.
"""

from typing import Optional


class OutputFormatter:
    """Formats command output for better readability in Telegram."""

    @staticmethod
    def format_code_block(content: str, language: str = "text") -> str:
        """
        Wrap content in a code block for Telegram.

        Args:
            content: The text to wrap
            language: Programming language for syntax highlighting (default: "text")

        Returns:
            Formatted code block
        """
        # Escape backticks and limit content length
        content = content.replace("`", "'")

        # If content is very long, truncate and add indicator
        if len(content) > 4000:
            content = content[:3900] + "\n\n... (salida truncada)"

        return f"```{language}\n{content}\n```"

    @staticmethod
    def format_section(title: str, content: str, emoji: str = "") -> str:
        """
        Format a section with title and content.

        Args:
            title: Section title
            content: Section content
            emoji: Optional emoji to prepend

        Returns:
            Formatted section
        """
        header = f"{emoji} {title}".strip()
        separator = "=" * len(header)
        return f"{header}\n{separator}\n{content}"

    @staticmethod
    def format_key_value(key: str, value: str, indent: int = 0) -> str:
        """
        Format a key-value pair.

        Args:
            key: The key
            value: The value
            indent: Indentation level

        Returns:
            Formatted key-value pair
        """
        prefix = "  " * indent
        return f"{prefix}{key}: {value}"

    @staticmethod
    def format_list(items: list, bullet: str = "•", indent: int = 0) -> str:
        """
        Format a list of items.

        Args:
            items: List of items to format
            bullet: Bullet character
            indent: Indentation level

        Returns:
            Formatted list
        """
        prefix = "  " * indent
        return "\n".join(f"{prefix}{bullet} {item}" for item in items)

    @staticmethod
    def format_table(headers: list, rows: list, border: bool = False) -> str:
        """
        Format a simple table.

        Args:
            headers: Column headers
            rows: List of rows (each row is a list of values)
            border: Whether to add borders

        Returns:
            Formatted table
        """
        if not headers or not rows:
            return ""

        # Calculate column widths
        widths = [len(str(h)) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(str(cell)))

        # Format header
        header_row = " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers))
        separator = "-+-".join("-" * w for w in widths)

        lines = [header_row, separator]

        # Format rows
        for row in rows:
            row_str = " | ".join(
                str(cell).ljust(widths[i]) for i, cell in enumerate(row)
            )
            lines.append(row_str)

        return "\n".join(lines)

    @staticmethod
    def format_status(status: str, success: bool = True) -> str:
        """
        Format a status indicator.

        Args:
            status: Status text
            success: Whether the status is positive

        Returns:
            Formatted status with emoji
        """
        emoji = "✅" if success else "❌"
        return f"{emoji} {status}"

    @staticmethod
    def format_warning(message: str) -> str:
        """
        Format a warning message.

        Args:
            message: Warning message

        Returns:
            Formatted warning
        """
        return f"⚠️ {message}"

    @staticmethod
    def format_info(message: str) -> str:
        """
        Format an info message.

        Args:
            message: Info message

        Returns:
            Formatted info
        """
        return f"ℹ️ {message}"

    @staticmethod
    def format_error(message: str) -> str:
        """
        Format an error message.

        Args:
            message: Error message

        Returns:
            Formatted error
        """
        return f"❌ {message}"

    @staticmethod
    def format_output(
        output: str,
        title: Optional[str] = None,
        emoji: Optional[str] = None,
        language: str = "text",
    ) -> str:
        """
        Format complete command output with optional title.

        Args:
            output: The raw output text
            title: Optional title for the output
            emoji: Optional emoji for the title
            language: Language for code block syntax highlighting

        Returns:
            Formatted output ready for Telegram
        """
        # Clean up output
        output = output.strip()

        # Start with title if provided
        result_parts = []
        if title:
            header = f"{emoji} {title}".strip() if emoji else title
            result_parts.append(f"{header}\n{'=' * len(header)}\n")

        # Add formatted code block
        result_parts.append(OutputFormatter.format_code_block(output, language))

        return "".join(result_parts)

    @staticmethod
    def format_multiline_output(
        sections: dict,
        title: Optional[str] = None,
        emoji: Optional[str] = None,
    ) -> str:
        """
        Format output with multiple sections.

        Args:
            sections: Dictionary of {section_name: section_content}
            title: Optional main title
            emoji: Optional emoji for title

        Returns:
            Formatted multi-section output
        """
        result_parts = []

        # Add main title if provided
        if title:
            header = f"{emoji} {title}".strip() if emoji else title
            result_parts.append(f"{header}\n{'=' * len(header)}\n")

        # Add each section
        for section_name, section_content in sections.items():
            result_parts.append(f"\n{section_name}\n{'-' * len(section_name)}")
            result_parts.append(section_content)

        return "\n".join(result_parts)

    @staticmethod
    def truncate_output(text: str, max_length: int = 4000) -> str:
        """
        Truncate output if it's too long for Telegram.

        Telegram messages have a limit of ~4096 characters.

        Args:
            text: Text to truncate
            max_length: Maximum length

        Returns:
            Truncated text with indicator if truncated
        """
        if len(text) <= max_length:
            return text

        truncated = text[: max_length - 50]
        return truncated + "\n\n... (salida truncada)"

    @staticmethod
    def format_with_menu(output: str, title: Optional[str] = None) -> str:
        """
        Format output that will be shown with a menu button below.

        This helps structure the message so the menu appears nicely below the output.

        Args:
            output: The output text
            title: Optional title

        Returns:
            Formatted output
        """
        result = ""

        if title:
            result += f"*{title}*\n"
            result += "=" * len(title) + "\n\n"

        result += OutputFormatter.format_code_block(output, "text")

        return result
