import asyncio
import ipaddress
import logging
import re
import shlex
import shutil
import socket
import ssl
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple, cast

from src.services.command_executor import CommandExecutor
from src.utils.formatters import OutputFormatter

logger = logging.getLogger("watchman")


class SecurityService:
    """Handles security-related operations and auditing."""

    @staticmethod
    async def get_active_connections() -> Tuple[bool, str]:
        """List active TCP network connections in readable format."""

        try:
            if shutil.which("ss"):
                cmd = ["ss", "-tan", "state", "established"]
            elif shutil.which("netstat"):
                cmd = ["netstat", "-tan"]
            else:
                return False, "❌ Ni 'ss' ni 'netstat' están disponibles en el sistema"

            success, output = await CommandExecutor.execute(cmd)

            if not success or not output:
                return True, "ℹ️ No se pudieron obtener conexiones activas"

            lines = output.strip().split("\n")

            # eliminar cabecera
            if lines and ("State" in lines[0] or "Proto" in lines[0]):
                lines = lines[1:]

            # filtrar conexiones establecidas
            lines = [line for line in lines if "ESTAB" in line or "ESTABLISHED" in line]

            if not lines:
                return True, "ℹ️ No hay conexiones establecidas actualmente"

            connections_list = []
            for line in lines[:10]:
                parts = line.split()

                # ss: local peer en columnas finales
                local = parts[-2]
                remote = parts[-1]

                try:
                    local_ip, local_port = local.rsplit(":", 1)
                except ValueError:
                    # Fallback para formatos especiales (IPv6, etc.)
                    local_ip = local
                    local_port = "?"

                try:
                    remote_ip, remote_port = remote.rsplit(":", 1)
                except ValueError:
                    remote_ip = remote
                    remote_port = "?"

                # Obtener nombre del servicio usando socket.getservbyport()
                try:
                    service = socket.getservbyport(int(local_port)).upper()
                except (ValueError, OSError):
                    service = f"PORT {local_port}"

                connections_list.append(
                    f"{service:10} {remote_ip:20} → {local_ip}:{local_port}"
                )

            if len(lines) > 10:
                connections_list.append(f"\n... y {len(lines) - 10} conexiones más")

            message = "🌐 CONEXIONES TCP ACTIVAS\n"
            message += "=" * 50 + "\n\n"
            message += OutputFormatter.format_list(connections_list, bullet="→")

            return True, message

        except Exception as e:
            logger.error(f"Error getting connections: {str(e)}")
            return False, "❌ Error al obtener conexiones del sistema"

    @staticmethod
    async def get_open_ports() -> Tuple[bool, str]:
        """List open ports and listening services."""
        try:
            if shutil.which("ss"):
                cmd = ["ss", "-tulpn"]
            elif shutil.which("netstat"):
                cmd = ["netstat", "-tulpn"]
            else:
                return False, "❌ Ni 'ss' ni 'netstat' están disponibles en el sistema"

            success, output = await CommandExecutor.execute(cmd)

            if not success or not output:
                return True, "ℹ️ No se encontraron puertos abiertos"

            lines = output.strip().split("\n")

            # eliminar cabecera
            if lines and ("State" in lines[0] or "Proto" in lines[0]):
                lines = lines[1:]

            # filtrar solo LISTEN
            lines = [line for line in lines if "LISTEN" in line]

            if not lines:
                return True, "ℹ️ No hay puertos en estado LISTEN"

            ports_list = []
            for line in lines[:15]:
                ports_list.append(line.strip())

            if len(lines) > 15:
                ports_list.append(f"... y {len(lines) - 15} puertos más")

            message = "🔓 PUERTOS ABIERTOS\n"
            message += "=" * 50 + "\n\n"
            message += OutputFormatter.format_list(ports_list, bullet="📌")

            return True, message

        except Exception as e:
            logger.error(f"Error getting open ports: {str(e)}")
            return False, "❌ Error al obtener puertos del sistema"

    @staticmethod
    async def get_network_processes() -> Tuple[bool, str]:
        """Show processes with open network connections."""
        try:
            if not shutil.which("lsof"):
                return False, "❌ 'lsof' no está disponible en el sistema"

            cmd = ["lsof", "-i", "-n", "-P"]
            success, output = await CommandExecutor.execute(cmd)

            if not success or not output:
                return True, "ℹ️ No hay procesos con conexiones de red abiertas"

            lines = output.strip().split("\n")

            # eliminar cabecera
            if lines and "COMMAND" in lines[0]:
                lines = lines[1:]

            if not lines:
                return True, "ℹ️ No hay procesos de red activos"

            procs_list = []
            for line in lines[:20]:
                procs_list.append(line.strip())

            if len(lines) > 20:
                procs_list.append(f"... y {len(lines) - 20} procesos más")

            message = "🔗 PROCESOS CON CONEXIONES DE RED\n"
            message += "=" * 50 + "\n\n"
            message += OutputFormatter.format_list(procs_list, bullet="⚙️")

            return True, message

        except Exception as e:
            logger.error(f"Error getting network processes: {str(e)}")
            return False, "❌ Error al obtener procesos de red"

    @staticmethod
    async def check_firewall() -> Tuple[bool, str]:
        """Check firewall status."""
        try:
            if shutil.which("ufw"):
                cmd = ["sudo", "ufw", "status"]
            elif shutil.which("iptables"):
                cmd = ["sudo", "iptables", "-L"]
            else:
                return (
                    False,
                    "❌ Ni 'ufw' ni 'iptables' están disponibles en el sistema",
                )

            success, output = await CommandExecutor.execute(cmd)

            if success:
                if "ufw" in cmd[1]:
                    if "Status: active" in output:
                        status = "✅ ACTIVO"
                    else:
                        status = "❌ INACTIVO"
                    message = "🔥 ESTADO DEL FIREWALL (UFW)\n"
                    message += "=" * 50 + "\n\n"
                    message += f"Estado: {status}\n\n"
                else:
                    message = "🔥 ESTADO DEL FIREWALL (iptables)\n"
                    message += "=" * 50 + "\n\n"
                message += "```\n" + output[:500] + "\n```"
                if len(output) > 500:
                    message += "\n\n... (salida truncada)"
            else:
                message = "❌ No se pudo obtener estado del firewall"

            return success, message
        except Exception as e:
            logger.error(f"Error checking firewall: {str(e)}")
            return False, "❌ Error al verificar firewall"

    @staticmethod
    async def get_firewall_rules() -> Tuple[bool, str]:
        """Get active firewall rules."""
        try:
            if shutil.which("ufw"):
                cmd = ["sudo", "ufw", "status", "numbered"]
            elif shutil.which("iptables"):
                cmd = ["sudo", "iptables", "-L", "-n", "-v"]
            else:
                return (
                    False,
                    "❌ Ni 'ufw' ni 'iptables' están disponibles en el sistema",
                )

            success, output = await CommandExecutor.execute(cmd)

            if success and output:
                message = "📋 REGLAS DEL FIREWALL\n"
                message += "=" * 50 + "\n\n"
                message += "```\n" + output[:1000] + "\n```"
                if len(output) > 1000:
                    message += "\n\n... (salida truncada)"
            else:
                return False, "❌ No se pudieron obtener reglas del firewall"

            return True, message
        except Exception as e:
            logger.error(f"Error getting firewall rules: {str(e)}")
            return False, "❌ Error al obtener reglas del firewall"

    @staticmethod
    async def get_failed_logins() -> Tuple[bool, str]:
        """Get recent failed login attempts."""
        try:
            if shutil.which("lastb"):
                cmd = ["sudo", "lastb", "-n", "10"]
            else:
                # Use grep directly without bash piping for security
                cmd = ["grep", "-i", "failed password", "/var/log/auth.log"]

            success, output = await CommandExecutor.execute(cmd, timeout=10)

            if success and output:
                lines = output.strip().split("\n")
                # Limit to last 10 entries
                failed_list = [line.strip() for line in lines[-10:] if line.strip()]

                if failed_list:
                    message = "🔐 INTENTOS DE LOGIN FALLIDOS\n"
                    message += "=" * 50 + "\n\n"
                    message += OutputFormatter.format_list(failed_list, bullet="❌")
                    return True, message

            return True, "ℹ️ No hay intentos de login fallidos registrados"
        except Exception as e:
            logger.error(f"Error getting failed logins: {str(e)}")
            return False, "❌ Error al obtener intentos de login"

    @staticmethod
    async def get_active_sessions() -> Tuple[bool, str]:
        """List currently active user sessions."""
        try:
            if shutil.which("w"):
                cmd = ["w"]
            elif shutil.which("who"):
                cmd = ["who"]
            else:
                return False, "❌ Ni 'w' ni 'who' están disponibles en el sistema"

            success, output = await CommandExecutor.execute(cmd)

            if success and output:
                message = "👥 SESIONES ACTIVAS DE USUARIOS\n"
                message += "=" * 50 + "\n\n"
                message += "```\n" + output + "\n```"
            else:
                return True, "ℹ️ No hay usuarios conectados actualmente"

            return True, message
        except Exception as e:
            logger.error(f"Error getting active sessions: {str(e)}")
            return False, "❌ Error al obtener sesiones"

    @staticmethod
    def _is_valid_domain(domain: str) -> bool:
        """
        Validate domain name according to RFC 1123.

        Args:
            domain: Domain to validate

        Returns:
            True if valid domain, False otherwise
        """
        if not domain or len(domain) > 253:
            return False

        # Check for leading/trailing dots or dashes
        if domain.startswith(".") or domain.startswith("-"):
            return False
        if domain.endswith(".") or domain.endswith("-"):
            return False

        # No consecutive dots or dashes
        if ".." in domain or "--" in domain:
            return False

        # Ensure it's not an IP address (IPs should not be checked as domains)
        try:
            ipaddress.ip_address(domain)
            return False
        except ValueError:
            pass  # Not an IP, which is good

        # RFC 1123 compliant pattern
        # Domain labels: 1-63 chars, alphanumeric and hyphens
        # TLD: 2+ chars, alphabetic only
        pattern = r"^(?!-)([a-zA-Z0-9-]{1,63}(?<!-)\.)*[a-zA-Z]{2,}$"

        return bool(re.match(pattern, domain))

    @staticmethod
    async def check_ssl_certificate(domain: str) -> Tuple[bool, str]:
        """Check SSL certificate validity for a domain with timeout."""

        if not SecurityService._is_valid_domain(domain):
            return False, "❌ Dominio inválido"

        def _check():
            context = ssl.create_default_context()

            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    tls_version = ssock.version()
                    cipher = ssock.cipher()

            if not cert:
                return False, f"❌ No se pudo obtener certificado SSL para {domain}"

            subject = {
                name: value
                for name, value in (item[0] for item in cert.get("subject", ()))
            }

            issuer = {
                name: value
                for name, value in (item[0] for item in cert.get("issuer", ()))
            }

            common_name = subject.get("commonName", "N/A")
            issuer_name = issuer.get(
                "organizationName", issuer.get("commonName", "N/A")
            )

            not_after = cert.get("notAfter")

            if not not_after:
                return False, f"❌ No se pudo obtener fecha de expiración para {domain}"

            expiry_date = datetime.strptime(
                cast(str, not_after), "%b %d %H:%M:%S %Y %Z"
            ).replace(tzinfo=timezone.utc)

            now = datetime.now(timezone.utc)
            days_remaining = (expiry_date - now).days

            message = f"🔐 SSL para {domain}\n\n"
            message += f"Dominio: {common_name}\n"
            message += f"Emisor: {issuer_name}\n"
            message += f"Expira: {not_after}\n"
            message += f"Días restantes: {days_remaining}\n"
            message += f"TLS: {tls_version}\n"
            cipher_name = cipher[0] if cipher else "N/A"
            message += f"Cipher: {cipher_name}\n"

            if days_remaining < 0:
                return False, f"❌ Certificado SSL expirado\n\n{message}"

            if days_remaining < 30:
                message = "⚠️ Certificado expira pronto\n\n" + message
            else:
                message = "✅ Certificado SSL válido\n\n" + message

            return True, message

        try:
            return await asyncio.to_thread(_check)

        except socket.gaierror:
            return False, f"❌ No se puede resolver el dominio: {domain}"

        except socket.timeout:
            return False, f"❌ Timeout conectando a {domain}"

        except ssl.SSLError as e:
            return False, f"❌ Error SSL: {str(e)}"

        except Exception as e:
            logger.error(f"Error checking SSL: {str(e)}")
            return False, f"❌ Error al verificar SSL: {str(e)}"

    @staticmethod
    async def find_suid_files() -> Tuple[bool, str]:
        """Find files with SUID bit set (potential privilege escalation vectors)."""
        try:
            # Limit find to common directories to avoid excessive scanning
            cmd = [
                "find",
                "/usr",
                "/bin",
                "/sbin",
                "/opt",
                "-perm",
                "-4000",
                "-type",
                "f",
            ]
            success, output = await CommandExecutor.execute(cmd, timeout=15)

            if success and output:
                lines = output.strip().split("\n")
                suid_files = []
                for line in lines[:20]:
                    if line.strip():
                        suid_files.append(line.strip())
                if len(lines) > 20:
                    suid_files.append(f"... y {len(lines) - 20} más")

                message = "⚠️ ARCHIVOS CON BIT SUID ACTIVO\n"
                message += "=" * 50 + "\n\n"
                message += "Potencial vector de escalada de privilegios:\n\n"
                message += OutputFormatter.format_list(suid_files, bullet="⚡")
            else:
                message = "ℹ️ No se encontraron archivos con SUID"

            return True, message
        except Exception as e:
            logger.error(f"Error finding SUID files: {str(e)}")
            return False, f"❌ Error al buscar archivos SUID: {str(e)}"

    @staticmethod
    async def get_cron_jobs() -> Tuple[bool, str]:
        """List scheduled cron jobs (potential persistence mechanism)."""
        try:
            # Use separate commands for better security instead of piping
            cmd = ["bash", "-c", "crontab -l 2>/dev/null"]
            success, output = await CommandExecutor.execute(cmd, timeout=10)

            cron_output = output if success else ""

            # List system cron directories
            cmd2 = ["bash", "-c", "ls -la /etc/cron* 2>/dev/null"]
            success2, output2 = await CommandExecutor.execute(cmd2, timeout=10)

            if success2:
                cron_output += "\n\n" + output2

            if success and output and "no crontab" not in output:
                message = "⏰ TAREAS PROGRAMADAS (CRON)\n"
                message += "=" * 50 + "\n\n"
                message += "Posible vector de persistencia:\n\n"
                message += "```\n" + output[:800] + "\n```"
                if len(output) > 800:
                    message += "\n... (salida truncada)"
            else:
                message = "ℹ️ No hay tareas programadas registradas"

            return True, message
        except Exception as e:
            logger.error(f"Error getting cron jobs: {str(e)}")
            return False, f"❌ Error al obtener tareas cron: {str(e)}"

    @staticmethod
    async def get_top_processes() -> Tuple[bool, str]:
        """Show processes with highest CPU or memory usage."""
        try:
            cmd = ["bash", "-c", "ps aux --sort=-%cpu | head -11"]
            success, output = await CommandExecutor.execute(cmd)

            if success and output:
                message = "⚙️ PROCESOS CON MAYOR CONSUMO\n"
                message += "=" * 50 + "\n\n"
                message += "```\n" + output + "\n```"
            else:
                return False, "❌ Error al obtener procesos"

            return True, message
        except Exception as e:
            logger.error(f"Error getting top processes: {str(e)}")
            return False, f"❌ Error al obtener procesos: {str(e)}"

    @staticmethod
    async def check_services() -> Tuple[bool, str]:
        """List active services in the system."""
        try:
            if shutil.which("systemctl"):
                cmd = ["systemctl", "list-units", "--type=service", "--state=running"]
            else:
                cmd = ["bash", "-c", "service --status-all"]

            success, output = await CommandExecutor.execute(cmd)

            if success and output:
                lines = output.strip().split("\n")
                services_list = []
                for line in lines[:20]:
                    if line.strip():
                        services_list.append(line.strip())
                if len(lines) > 20:
                    services_list.append(f"... y {len(lines) - 20} más")

                message = "🚀 SERVICIOS ACTIVOS\n"
                message += "=" * 50 + "\n\n"
                message += OutputFormatter.format_list(services_list, bullet="▶️")
            else:
                message = "ℹ️ No se encontraron servicios activos"

            return True, message
        except Exception as e:
            logger.error(f"Error checking services: {str(e)}")
            return False, f"❌ Error al verificar servicios: {str(e)}"

    @staticmethod
    async def check_sudoers() -> Tuple[bool, str]:
        """List users with sudo privileges."""
        try:
            # Intentar getent primero, luego cat /etc/sudoers
            cmd = [
                "bash",
                "-c",
                "getent group sudo 2>/dev/null || cat /etc/sudoers 2>/dev/null | grep -E '^[a-zA-Z]'",
            ]
            success, output = await CommandExecutor.execute(cmd)

            if output and "Sin acceso" not in output:
                message = "👤 USUARIOS CON PRIVILEGIOS SUDO\n"
                message += "=" * 50 + "\n\n"
                message += "```\n" + output[:500] + "\n```"
                if len(output) > 500:
                    message += "\n... (truncado)"
            else:
                message = (
                    "ℹ️ No se pudo acceder a sudoers o no hay usuarios configurados"
                )

            return True, message
        except Exception as e:
            logger.error(f"Error checking sudoers: {str(e)}")
            return False, f"❌ Error al verificar sudoers: {str(e)}"

    @staticmethod
    async def audit_ssh_keys() -> Tuple[bool, str]:
        """Audit SSH keys on the system."""
        try:
            cmd = [
                "bash",
                "-c",
                "cat ~/.ssh/authorized_keys 2>/dev/null || find /home -name authorized_keys 2>/dev/null",
            ]
            success, output = await CommandExecutor.execute(cmd)

            if output:
                lines = output.strip().split("\n")
                ssh_keys = []
                for line in lines[:10]:
                    if line.strip():
                        ssh_keys.append(line.strip()[:80])
                if len(lines) > 10:
                    ssh_keys.append(f"... y {len(lines) - 10} más")

                message = "🔑 CLAVES SSH AUTORIZADAS\n"
                message += "=" * 50 + "\n\n"
                message += OutputFormatter.format_list(ssh_keys, bullet="🔐")
            else:
                message = "ℹ️ No se encontraron claves SSH configuradas"

            return True, message
        except Exception as e:
            logger.error(f"Error auditing SSH keys: {str(e)}")
            return False, f"❌ Error al auditar SSH: {str(e)}"

    @staticmethod
    async def run_security_audit() -> Tuple[bool, str]:
        """Run comprehensive security audit."""
        try:
            audit_results = []

            conn_success, _ = await SecurityService.get_active_connections()
            audit_results.append(("Conexiones", conn_success))

            ports_success, _ = await SecurityService.get_open_ports()
            audit_results.append(("Puertos abiertos", ports_success))

            login_success, _ = await SecurityService.get_failed_logins()
            audit_results.append(("Intentos de login", login_success))

            services_success, _ = await SecurityService.check_services()
            audit_results.append(("Servicios", services_success))

            message = "🔒 AUDITORÍA DE SEGURIDAD COMPLETA\n"
            message += "=" * 50 + "\n\n"

            message += "📊 RESULTADOS:\n"
            message += "-" * 50 + "\n"
            for check, status in audit_results:
                status_icon = "✅" if status else "⚠️"
                message += f"{status_icon} {check}\n"

            message += "\n📋 RECOMENDACIONES:\n"
            message += "-" * 50 + "\n"
            recommendations = [
                "Revisar conexiones activas regularmemnte",
                "Verificar puertos innecesarios y cerrarlos",
                "Monitorear intentos de login fallidos",
                "Auditar servicios activos y desactivar innecesarios",
                "Revisar claves SSH autorizadas",
                "Verificar archivos SUID potencialmente peligrosos",
                "Revisar tareas cron sospechosas",
            ]
            message += OutputFormatter.format_list(recommendations, bullet="→")

            return True, message
        except Exception as e:
            logger.error(f"Error running audit: {str(e)}")
            return False, f"❌ Error en auditoría: {str(e)}"

    @staticmethod
    def _is_private_ip(ip: str) -> bool:
        """Check if IP is private or loopback."""
        if ip in ("127.0.0.1", "::1"):
            return True

        try:
            parts = ip.split(".")
            if len(parts) == 4:
                first = int(parts[0])
                if first == 10:
                    return True
                if first == 172:
                    second = int(parts[1])
                    if 16 <= second <= 31:
                        return True
                if first == 192 and int(parts[1]) == 168:
                    return True
        except (ValueError, IndexError):
            pass

        return False

    @staticmethod
    async def _count_failed_logins() -> int:
        """Count failed login attempts directly from system without parsing messages."""
        try:
            if shutil.which("lastb"):
                cmd = ["sudo", "lastb", "-n", "100"]
                success, output = await CommandExecutor.execute(cmd, timeout=10)
            else:
                # Count lines in auth.log with "Failed password"
                cmd = [
                    "bash",
                    "-c",
                    "grep -c 'Failed password' /var/log/auth.log 2>/dev/null || echo 0",
                ]
                success, output = await CommandExecutor.execute(cmd, timeout=10)

            if success:
                try:
                    # Extract number from output
                    count_str = output.strip().split("\n")[-1]
                    count = int(count_str)
                    return count
                except (ValueError, IndexError):
                    return 0
            return 0
        except Exception as e:
            logger.warning(f"Error counting failed logins: {e}")
            return 0

    @staticmethod
    def _extract_ip_port_from_connection_line(line: str) -> Tuple[str, str, str, str]:
        """Extract local_ip, local_port, remote_ip, remote_port from connection line."""
        parts = line.split()
        if len(parts) < 2:
            return "", "", "", ""

        local = parts[-2]
        remote = parts[-1]

        try:
            local_ip, local_port = local.rsplit(":", 1)
        except ValueError:
            local_ip, local_port = local, ""

        try:
            remote_ip, remote_port = remote.rsplit(":", 1)
        except ValueError:
            remote_ip, remote_port = remote, ""

        return local_ip, local_port, remote_ip, remote_port

    @staticmethod
    async def analyze_threats() -> Tuple[bool, str]:
        """Analyze system for potential indicators of compromise and suspicious behavior."""
        try:
            threats = []
            score = 0

            # 1. Check failed logins (brute force attacks)
            # Count directly from system, not from formatted message
            failed_login_count = await SecurityService._count_failed_logins()

            if failed_login_count > 0:
                risk_level = "BAJO"
                threat_score = 1
                if failed_login_count > 5:
                    risk_level = "MEDIO"
                    threat_score = 2
                if failed_login_count > 20:
                    risk_level = "ALTO"
                    threat_score = 3

                threats.append(
                    {
                        "title": f"⚠️ {failed_login_count} intentos de login fallidos detectados",
                        "level": risk_level,
                        "score": threat_score,
                        "details": f"Se detectaron {failed_login_count} intentos fallidos de acceso al sistema",
                    }
                )
                score += threat_score

            # 2. Check suspicious external connections
            _, connections_msg = await SecurityService.get_active_connections()

            # Parse connections to detect external IPs
            suspicious_ips = {}
            if "CONEXIONES TCP ACTIVAS" in connections_msg:
                try:
                    if shutil.which("ss"):
                        cmd = ["ss", "-tan", "state", "established"]
                    elif shutil.which("netstat"):
                        cmd = ["netstat", "-tan"]
                    else:
                        cmd = None

                    if cmd:
                        success, output = await CommandExecutor.execute(cmd)

                        if success and output:
                            lines = output.strip().split("\n")
                            if lines and ("State" in lines[0] or "Proto" in lines[0]):
                                lines = lines[1:]

                            for line in lines:
                                if "ESTAB" not in line and "ESTABLISHED" not in line:
                                    continue

                                local_ip, local_port, remote_ip, remote_port = (
                                    SecurityService._extract_ip_port_from_connection_line(
                                        line
                                    )
                                )

                                if not local_port or not remote_ip:
                                    continue

                                # Check if external IP
                                if not SecurityService._is_private_ip(remote_ip):
                                    # Sensitive ports: 22, 3306, 5432, 6379, 27017
                                    sensitive_ports = [
                                        "22",
                                        "3306",
                                        "5432",
                                        "6379",
                                        "27017",
                                    ]
                                    if local_port in sensitive_ports:
                                        if remote_ip not in suspicious_ips:
                                            suspicious_ips[remote_ip] = []
                                        suspicious_ips[remote_ip].append(
                                            (local_port, "sensible")
                                        )
                                    else:
                                        if remote_ip not in suspicious_ips:
                                            suspicious_ips[remote_ip] = []
                                        suspicious_ips[remote_ip].append(
                                            (local_port, "normal")
                                        )
                except Exception as e:
                    logger.warning(f"Error analyzing connections for threats: {e}")

            # Add suspicious external connection threats
            if suspicious_ips:
                for remote_ip, ports in suspicious_ips.items():
                    risk_level = "BAJO"
                    threat_score = 1

                    # Check if any connection to sensitive port
                    has_sensitive = any(p[1] == "sensible" for p in ports)
                    if has_sensitive or len(ports) > 2:
                        risk_level = "MEDIO"
                        threat_score = 2

                    port_list = ", ".join([p[0] for p in ports])
                    threats.append(
                        {
                            "title": f"🌍 Conexión externa detectada desde {remote_ip}",
                            "level": risk_level,
                            "score": threat_score,
                            "details": f"Puertos locales: {port_list}",
                        }
                    )
                    score += threat_score

            # 3. Check for suspicious processes
            _, processes_msg = await SecurityService.get_top_processes()

            # Legitimate processes that may run from temp dirs (whitelist)
            legit_temp_procs = [
                "systemd",
                "systemd-",
                "python",
                "perl",
                "ruby",
                "java",
                "node",
                "apt",
                "dpkg",
                "snap",
                "unzip",
                "tar",
                "wget",
                "curl",
            ]

            try:
                if shutil.which("ps"):
                    # Use ps directly without bash piping when possible
                    cmd = ["bash", "-c", "ps aux --sort=-%cpu | head -50"]
                    success, output = await CommandExecutor.execute(cmd)

                    if success and output:
                        for line in output.split("\n"):
                            for susp_dir in ["/tmp/", "/dev/shm/", "/var/tmp/"]:
                                if susp_dir in line:
                                    # Parse ps aux line safely
                                    # ps aux format: USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND
                                    try:
                                        parts = line.split(
                                            None, 10
                                        )  # Split into max 11 parts
                                        if len(parts) < 11:
                                            logger.warning(
                                                f"Unexpected ps format: {line}"
                                            )
                                            continue

                                        proc_name = parts[
                                            10
                                        ]  # Last part is always the command

                                        # Check if process is in whitelist
                                        is_legitimate = any(
                                            legit in proc_name.lower()
                                            for legit in legit_temp_procs
                                        )

                                        if not is_legitimate:
                                            threats.append(
                                                {
                                                    "title": f"❗ Proceso sospechoso ejecutándose desde {susp_dir.rstrip('/')}",
                                                    "level": "ALTO",
                                                    "score": 3,
                                                    "details": f"Proceso: {proc_name}",
                                                }
                                            )
                                            score += 3
                                            break
                                    except (IndexError, ValueError) as e:
                                        logger.warning(
                                            f"Failed to parse process line: {line}: {e}"
                                        )
                                        continue
            except Exception as e:
                logger.warning(f"Error checking suspicious processes: {e}")

            # 4. Check cron jobs for suspicious patterns
            _, cron_msg = await SecurityService.get_cron_jobs()

            # Suspicious cron patterns with regex to avoid false positives
            # Format: (pattern_regex, description)
            suspicious_cron_patterns = [
                (r"curl\s+.*\|\s*bash", "curl pipe bash"),
                (r"wget\s+.*\|\s*bash", "wget pipe bash"),
                (r"\bnetcat\b", "netcat"),
                (r"bash\s+-i\s", "interactive bash shell"),
                (r"/tmp/.*\.(sh|exe|bin)", "executable in /tmp"),
                (r"/dev/shm/.*\.(sh|exe|bin)", "executable in /dev/shm"),
                (r">\s*/dev/(tcp|udp)", "shell redirect to /dev/tcp or /dev/udp"),
            ]

            if cron_msg and "crontab" in cron_msg.lower():
                for pattern_regex, description in suspicious_cron_patterns:
                    if re.search(pattern_regex, cron_msg, re.IGNORECASE):
                        threats.append(
                            {
                                "title": f"🔄 Patrón sospechoso detectado en cron: {description}",
                                "level": "ALTO",
                                "score": 3,
                                "details": f"Se encontró '{description}' en tareas programadas",
                            }
                        )
                        score += 3
                        break

            # 5. Check for unusual SUID files
            # Note: suid_msg not used, checking directly from find command
            known_suid = [
                "/usr/bin/passwd",
                "/usr/bin/sudo",
                "/usr/bin/ping",
                "/usr/bin/su",
                "/usr/bin/chsh",
                "/usr/bin/chfn",
                "/usr/bin/newgrp",
                "/bin/mount",
                "/bin/umount",
                "/usr/bin/at",
            ]

            if suid_msg and "SUID" in suid_msg:
                try:
                    if shutil.which("find"):
                        cmd = ["find", "/", "-perm", "-4000", "-type", "f"]
                        success, output = await CommandExecutor.execute(cmd)

                        if success and output:
                            for line in output.split("\n"):
                                if line.strip() and line.strip() not in known_suid:
                                    threats.append(
                                        {
                                            "title": "⚠️ Archivo SUID inusual detectado",
                                            "level": "ALTO",
                                            "score": 3,
                                            "details": f"Archivo: {line.strip()}",
                                        }
                                    )
                                    score += 3
                                    break
                except Exception as e:
                    logger.warning(f"Error checking SUID files: {e}")

            # 6. Check for suspicious services
            _, services_msg = await SecurityService.check_services()

            # Suspicious service patterns - use word boundaries to avoid false positives
            # Format: (pattern, full_name) - pattern uses word boundaries for exact matching
            suspicious_services = [
                (r"\bnetcat\.service\b", "netcat"),
                (r"\bsocat\.service\b", "socat"),
                (r"\bcryptominer\.service\b", "cryptominer"),
                (r"\bxmrig\.service\b", "xmrig"),
                (r"\bncat\.service\b", "ncat"),
            ]

            for pattern, service_name in suspicious_services:
                if re.search(pattern, services_msg, re.IGNORECASE):
                    threats.append(
                        {
                            "title": f"🛑 Servicio sospechoso detectado: {service_name}",
                            "level": "ALTO",
                            "score": 3,
                            "details": f"Se encontró servicio potencialmente malicioso: {service_name}",
                        }
                    )
                    score += 3
                    break

            # Generate report
            if score == 0:
                status = "✅ SISTEMA SEGURO"
                emoji = "✅"
            elif score <= 2:
                status = "ℹ️ ACTIVIDAD NORMAL"
                emoji = "ℹ️"
            elif score <= 5:
                status = "⚠️ ACTIVIDAD SOSPECHOSA"
                emoji = "⚠️"
            else:
                status = "🚨 POSIBLE COMPROMISO"
                emoji = "🚨"

            message = f"{emoji} ANÁLISIS DE AMENAZAS\n"
            message += "=" * 50 + "\n\n"
            message += f"Estado general: {status}\n\n"

            if threats:
                message += "Hallazgos detectados:\n"
                message += "-" * 50 + "\n\n"
                for threat in threats:
                    message += f"{threat['title']}\n"
                    message += f"Riesgo: {threat['level']}\n"
                    message += f"Detalles: {threat['details']}\n\n"
            else:
                message += "No se detectaron amenazas significativas.\n\n"

            message += f"Score total: {score}\n"
            message += "-" * 50 + "\n\n"

            if score > 5:
                message += "🔔 RECOMENDACIONES:\n"
                message += "• Revisar procesos activos inmediatamente\n"
                message += "• Analizar conexiones de red sospechosas\n"
                message += "• Verificar archivos modificados recientemente\n"
                message += "• Considerar ejecutar análisis antimalware\n"
            elif score > 2:
                message += "🔔 RECOMENDACIONES:\n"
                message += "• Revisar procesos y conexiones activas\n"
                message += "• Verificar integridad de archivos críticos\n"
                message += "• Auditar intentos de acceso recientes\n"

            return True, message

        except Exception as e:
            logger.error(f"Error analyzing threats: {str(e)}")
            return False, f"❌ Error en análisis de amenazas: {str(e)}"
