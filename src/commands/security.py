import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.commands.base import BaseCommand
from src.services.security_functions import SecurityService

logger = logging.getLogger("watchman")


class ConnectionsCommand(BaseCommand):
    """Command to show active TCP connections."""

    name = "connections"
    description = "🌐 Muestra conexiones TCP activas del sistema"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List active connections."""
        success, message = await SecurityService.get_active_connections()
        await self.send_message(update, context, message)
        logger.info(f"Active connections check executed. Success: {success}")


class OpenPortsCommand(BaseCommand):
    """Command to list open ports."""

    name = "openports"
    description = "🔓 Lista puertos abiertos y servicios escuchando"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List open ports."""
        success, message = await SecurityService.get_open_ports()
        await self.send_message(update, context, message)
        logger.info(f"Open ports check executed. Success: {success}")


class NetworkProcessesCommand(BaseCommand):
    """Command to show processes with network connections."""

    name = "networkproc"
    description = "🔗 Muestra procesos que tienen conexiones de red abiertas"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show network processes."""
        success, message = await SecurityService.get_network_processes()
        await self.send_message(update, context, message)
        logger.info(f"Network processes check executed. Success: {success}")


class FirewallStatusCommand(BaseCommand):
    """Command to check firewall status."""

    name = "firewall"
    description = "🔥 Verifica el estado del firewall del sistema"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Check firewall status."""
        success, message = await SecurityService.check_firewall()
        await self.send_message(update, context, message)
        logger.info(f"Firewall status checked. Success: {success}")


class FirewallRulesCommand(BaseCommand):
    """Command to list firewall rules."""

    name = "fwrules"
    description = "📋 Muestra las reglas activas del firewall"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List firewall rules."""
        success, message = await SecurityService.get_firewall_rules()
        await self.send_message(update, context, message)
        logger.info(f"Firewall rules check executed. Success: {success}")


class FailedLoginsCommand(BaseCommand):
    """Command to check failed login attempts."""

    name = "failedlogins"
    description = "🔐 Muestra intentos recientes de login fallidos"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Check failed login attempts."""
        success, message = await SecurityService.get_failed_logins()
        await self.send_message(update, context, message)
        logger.info(f"Failed logins check executed. Success: {success}")


class SessionsCommand(BaseCommand):
    """Command to list active user sessions."""

    name = "sessions"
    description = "👥 Lista usuarios actualmente conectados al sistema"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List active sessions."""
        success, message = await SecurityService.get_active_sessions()
        await self.send_message(update, context, message)
        logger.info(f"Active sessions check executed. Success: {success}")


class SSHKeysCommand(BaseCommand):
    """Command to audit SSH keys."""

    name = "sshkeys"
    description = "🔑 Audita claves SSH configuradas en el sistema"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Audit SSH keys."""
        success, message = await SecurityService.audit_ssh_keys()
        await self.send_message(update, context, message)
        logger.info(f"SSH keys audit executed. Success: {success}")


class SudoersCheckCommand(BaseCommand):
    """Command to check sudoers configuration."""

    name = "sudoers"
    description = "👤 Lista usuarios con privilegios sudo"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Check sudoers configuration."""
        success, message = await SecurityService.check_sudoers()
        await self.send_message(update, context, message)
        logger.info(f"Sudoers check executed. Success: {success}")


class TopProcessesCommand(BaseCommand):
    """Command to show top CPU/memory consuming processes."""

    name = "topproc"
    description = "⚙️ Muestra procesos con mayor consumo de CPU o memoria"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show top processes."""
        success, message = await SecurityService.get_top_processes()
        await self.send_message(update, context, message)
        logger.info(f"Top processes check executed. Success: {success}")


class ServiceSecurityCommand(BaseCommand):
    """Command to check running services."""

    name = "services"
    description = "🚀 Lista servicios activos en el sistema"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Check running services."""
        success, message = await SecurityService.check_services()
        await self.send_message(update, context, message)
        logger.info(f"Services check executed. Success: {success}")


class SSLCertificateCommand(BaseCommand):
    """Command to check SSL certificate validity."""

    name = "sslcheck"
    description = "🔐 Verifica el certificado SSL de un dominio"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Check SSL certificates."""
        if not context.args:
            await self.send_message(
                update,
                context,
                "❌ Uso: /sslcheck <dominio>\nEjemplo: /sslcheck example.com",
            )
            return

        domain = context.args[0]
        success, message = await SecurityService.check_ssl_certificate(domain)
        await self.send_message(update, context, message)
        logger.info(f"SSL check for {domain}. Success: {success}")


class SuidFilesCommand(BaseCommand):
    """Command to find SUID files."""

    name = "suidfiles"
    description = "⚠️ Busca archivos con bit SUID activo (posible escalada)"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Find SUID files."""
        success, message = await SecurityService.find_suid_files()
        await self.send_message(update, context, message)
        logger.info(f"SUID files check executed. Success: {success}")


class CronJobsCommand(BaseCommand):
    """Command to list cron jobs."""

    name = "cronjobs"
    description = "⏰ Lista tareas programadas del sistema (posible persistencia)"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List cron jobs."""
        success, message = await SecurityService.get_cron_jobs()
        await self.send_message(update, context, message)
        logger.info(f"Cron jobs check executed. Success: {success}")


class SystemAuditCommand(BaseCommand):
    """Command to run a comprehensive security audit."""

    name = "audit"
    description = "🔒 Ejecuta una auditoría básica de seguridad del sistema"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Run comprehensive security audit."""
        await self.send_message(
            update,
            context,
            "🔒 Iniciando auditoría de seguridad...\n⏳ Esto puede tomar unos momentos...",
        )
        success, message = await SecurityService.run_security_audit()
        await self.send_message(update, context, message)
        logger.info(f"Security audit executed. Success: {success}")


class ThreatsCommand(BaseCommand):
    """Command to analyze potential threats and indicators of compromise."""

    name = "threats"
    description = "🚨 Analiza el sistema para detectar posibles amenazas y compromisos"

    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Analyze system for threats."""
        await self.send_message(
            update,
            context,
            "🔍 Analizando sistema en busca de amenazas...\n⏳ Por favor, espera...",
        )
        success, message = await SecurityService.analyze_threats()
        await self.send_message(update, context, message)
        logger.info(f"Threat analysis executed. Success: {success}")
