from enum import Enum
from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class MenuCategory(Enum):
    SYSTEM = "SISTEMA"
    SECURITY = "SEGURIDAD"
    MAINTENANCE = "MANTENIMIENTO"


class MenuButton:
    def __init__(self, label: str, callback_data: str, emoji: str = ""):
        self.label = f"{emoji} {label}".strip()
        self.callback_data = callback_data

    def to_inline_button(self) -> InlineKeyboardButton:
        return InlineKeyboardButton(text=self.label, callback_data=self.callback_data)


class Menu:
    def __init__(self, title: str = ""):
        self.title = title
        self.buttons: List[List[MenuButton]] = []

    def add_button(self, button: MenuButton, row: int = 0):
        while len(self.buttons) <= row:
            self.buttons.append([])
        self.buttons[row].append(button)
        return self

    def add_row(self, buttons: List[MenuButton]):
        self.buttons.append(buttons)
        return self

    def get_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = [[btn.to_inline_button() for btn in row] for row in self.buttons]
        return InlineKeyboardMarkup(keyboard)

    def get_text(self) -> str:
        return self.title


class MainMenu(Menu):
    def __init__(self):
        title = (
            "🤖 *WATCHMAN v1.0*\n"
            "Home Lab Security Monitor\n\n"
            "Selecciona una categoría:\n\n"
            "_Monitorea tu home lab de forma segura_"
        )
        super().__init__(title=title)
        self._build_menu()

    def _build_menu(self):
        self.add_button(MenuButton("Sistema", "menu_system"), row=0)
        self.add_button(MenuButton("Seguridad", "menu_security"), row=0)
        self.add_button(MenuButton("Mantenimiento", "menu_maintenance"), row=1)
        self.add_button(MenuButton("Ayuda", "menu_help"), row=2)


class SystemMenu(Menu):
    def __init__(self):
        title = "📊 *SISTEMA*\n_Monitoreo y control del hardware_"
        super().__init__(title=title)
        self._build_menu()

    def _build_menu(self):
        self.add_button(MenuButton("📈 Estado", "cmd_status"), row=0)
        self.add_button(MenuButton("🌡️ Temperatura", "cmd_temp"), row=0)
        self.add_button(MenuButton("⬆️ Actualizar", "cmd_update"), row=1)
        self.add_button(MenuButton("🔄 Reiniciar", "cmd_reboot"), row=1)
        self.add_button(MenuButton("💾 Remontar", "cmd_remount"), row=2)
        self.add_button(MenuButton("← Atras", "menu_main"), row=3)


class SecurityMenu(Menu):
    def __init__(self):
        title = "🔒 *SEGURIDAD*\n_Auditoría y análisis de seguridad_"
        super().__init__(title=title)
        self._build_menu()

    def _build_menu(self):
        self.add_button(MenuButton("🌐 Conexiones", "cmd_connections"), row=0)
        self.add_button(MenuButton("🔓 Puertos", "cmd_openports"), row=0)

        self.add_button(MenuButton("🔗 Procesos Red", "cmd_networkproc"), row=1)
        self.add_button(MenuButton("🔥 Firewall", "cmd_firewall"), row=1)

        self.add_button(MenuButton("📋 Reglas FW", "cmd_fwrules"), row=2)
        self.add_button(MenuButton("❌ Login Fallido", "cmd_failedlogins"), row=2)

        self.add_button(MenuButton("👥 Sesiones", "cmd_sessions"), row=3)
        self.add_button(MenuButton("🔑 SSH Keys", "cmd_sshkeys"), row=3)

        self.add_button(MenuButton("👤 Sudoers", "cmd_sudoers"), row=4)
        self.add_button(MenuButton("⚙️ Top Proc", "cmd_topproc"), row=4)

        self.add_button(MenuButton("🚀 Servicios", "cmd_services"), row=5)
        self.add_button(MenuButton("🔐 SSL Check", "cmd_sslcheck"), row=5)

        self.add_button(MenuButton("⚠️ SUID", "cmd_suidfiles"), row=6)
        self.add_button(MenuButton("⏰ Cron", "cmd_cronjobs"), row=6)

        self.add_button(MenuButton("📊 Auditoria", "cmd_audit"), row=7)
        self.add_button(MenuButton("🚨 Amenazas", "cmd_threats"), row=7)

        self.add_button(MenuButton("🔙 Volver", "menu_main"), row=8)


class MaintenanceMenu(Menu):
    def __init__(self):
        title = "🔧 *MANTENIMIENTO*\n_Actualización y mantenimiento del sistema_"
        super().__init__(title=title)
        self._build_menu()

    def _build_menu(self):
        self.add_button(MenuButton("⬆️ Actualizar", "cmd_update"), row=0)
        self.add_button(MenuButton("🔄 Reiniciar", "cmd_reboot"), row=1)
        self.add_button(MenuButton("💾 Remontar FS", "cmd_remount"), row=2)
        self.add_button(MenuButton("🔙 Volver", "menu_main"), row=3)


class HelpMenu(Menu):
    def __init__(self):
        title = (
            "ℹ️ *AYUDA*\n\n"
            "*WATCHMAN v1.0* - Monitor de Seguridad\n\n"
            "*Funcionalidades principales:*\n"
            "🌐 Monitorear conexiones de red\n"
            "🔥 Verificar estado del firewall\n"
            "🔐 Auditar intentos de acceso\n"
            "⚙️ Revisar servicios y procesos\n"
            "⚠️ Buscar vectores de escalada\n"
            "📜 Verificar certificados SSL\n"
            "🚨 Analizar amenazas del sistema\n\n"
            "*Nota:* Algunos comandos requieren permisos sudo.\n"
            "*Security:* Solo el usuario autorizado puede usar este bot."
        )
        super().__init__(title=title)
        self._build_menu()

    def _build_menu(self):
        self.add_button(MenuButton("🔙 Volver", "menu_main"), row=0)


CALLBACK_TO_COMMAND = {
    "cmd_status": "status",
    "cmd_temp": "temp",
    "cmd_reboot": "reboot",
    "cmd_update": "update",
    "cmd_remount": "remount",
    "cmd_connections": "connections",
    "cmd_openports": "openports",
    "cmd_networkproc": "networkproc",
    "cmd_firewall": "firewall",
    "cmd_fwrules": "fwrules",
    "cmd_sslcheck": "sslcheck",
    "cmd_failedlogins": "failedlogins",
    "cmd_sessions": "sessions",
    "cmd_sshkeys": "sshkeys",
    "cmd_sudoers": "sudoers",
    "cmd_topproc": "topproc",
    "cmd_services": "services",
    "cmd_suidfiles": "suidfiles",
    "cmd_cronjobs": "cronjobs",
    "cmd_audit": "audit",
    "cmd_threats": "threats",
}

MENU_CALLBACKS = {
    "menu_main": MainMenu,
    "menu_system": SystemMenu,
    "menu_security": SecurityMenu,
    "menu_maintenance": MaintenanceMenu,
    "menu_help": HelpMenu,
}
