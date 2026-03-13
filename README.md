# WATCHMAN - Home Lab Security Monitor Bot

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Telegram Bot](https://img.shields.io/badge/telegram-bot-blue.svg)](https://core.telegram.org/bots)

Bot de Telegram avanzado para monitorizar y auditar remotamente tu Home Lab. Acceso restringido a un único usuario autorizado con 20+ comandos de seguridad, análisis de sistema y mantenimiento.

**✨ Características:**
- 🔒 Acceso restringido a usuario autorizado
- 🔐 20+ comandos de seguridad y auditoría
- ⏱️ Rate limiting y protección contra abuso
- 📝 Logging centralizado con rotación de archivos

---

## Instalación Rápida

### Requisitos Previos
- Python 3.11+
- Git
- Token de bot de Telegram (@BotFather)
- Tu ID de usuario de Telegram (@userinfobot)

### Con `uv` (Recomendado)

```bash
# Instalar uv (si no lo tienes)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clonar e instalar
git clone https://github.com/yourusername/WATCHMAN.git
cd WATCHMAN
uv sync

# Configurar
cp .env.example .env
# Editar .env con BOT_TOKEN y TG_USER_ID

# Ejecutar
source .venv/bin/activate
python src/main.py
```

### Con `pip`

```bash
# Clonar e instalar
git clone https://github.com/yourusername/WATCHMAN.git
cd WATCHMAN
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar
cp .env.example .env
# Editar .env con BOT_TOKEN y TG_USER_ID

# Ejecutar
python src/main.py
```

### Con Docker

```bash
# Configurar
cp .env.example .env
# Editar .env con tus credenciales

# Construir y ejecutar
docker build -t watchman .
docker run --name watchman-bot -d --restart unless-stopped --env-file .env watchman
```

---

## Configuración

### Variables de Entorno (`.env`)

```
BOT_TOKEN=123456789:ABCDEF1234567890abcdef1234567890abc
TG_USER_ID=987654321

# Opcional
LOG_FILE=watchman.log
LOG_LEVEL=INFO
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
RATE_LIMIT_CALLS=10
RATE_LIMIT_WINDOW=60
TEMP_CRITICAL_THRESHOLD=110.0
REBOOT_DELAY=10
```

**Obtener credenciales:**
1. Busca `@BotFather` en Telegram → `/newbot` → obtén BOT_TOKEN
2. Busca `@userinfobot` en Telegram → obtén TG_USER_ID

---

## Comandos Disponibles

### Sistema
| Comando | Descripción |
|---------|-------------|
| `/status` | Estado general del sistema |
| `/temp` | Temperatura de la CPU |
| `/reboot` | Programar el reinicio |
| `/update` | Actualizar los paquetes |
| `/remount` | Remontar los filesystems |

### Seguridad
| Comando | Descripción |
|---------|-------------|
| `/connections` | Conexiones TCP activas |
| `/openports` | Puertos abiertos |
| `/firewall` | Estado del firewall |
| `/failedlogins` | Intentos fallidos de login |
| `/sessions` | Usuarios conectados |
| `/sshkeys` | Auditar claves SSH |
| `/sudoers` | Usuarios con privilegios sudo |
| `/services` | Servicios activos |
| `/suidfiles` | Archivos SUID |
| `/cronjobs` | Tareas cron |
| `/sslcheck <dominio>` | Verificar certificados SSL |
| `/audit` | Auditoría completa |
| `/threats` | Análisis de amenazas |

**Usar desde menú:**
- Envía `/start` para ver menú interactivo
- Navega con botones
- Presiona "Atrás" para volver

---

## Estructura del Proyecto

```
WATCHMAN/
├── src/
│   ├── main.py                 # Punto de entrada
│   ├── config/
│   │   └── settings.py         # Configuración
│   ├── commands/
│   │   ├── base.py             # Clase base de comandos
│   │   ├── handler.py          # Gestor de comandos
│   │   ├── security.py         # Comandos de seguridad
│   │   ├── system.py           # Comandos de sistema
│   │   └── maintenance.py      # Comandos de mantenimiento
│   ├── handlers/
│   │   └── telegram_handler.py # Manejador de Telegram
│   ├── services/
│   │   ├── command_executor.py # Ejecutor de comandos
│   │   ├── security_functions.py # Lógica de seguridad
│   │   └── system_service.py   # Servicios del sistema
│   └── utils/
│       ├── formatters.py       # Formateo de salidas
│       ├── logger.py           # Logging
│       ├── menus.py            # Menús interactivos
│       └── rate_limiter.py     # Rate limiting
├── tests/                      # Tests
├── .env.example                # Variables de ejemplo
├── .python-version             # Versión Python (3.11)
├── pyproject.toml              # Configuración del proyecto
├── requirements.txt            # Dependencias
├── requirements-dev.txt        # Dependencias de desarrollo
├── setup.py                    # Setup para instalación
├── Makefile                    # Tareas de desarrollo
├── .editorconfig               # Configuración de editor
├── .pre-commit-config.yaml     # Pre-commit hooks
├── pytest.ini                  # Configuración de pytest
├── MANIFEST.in                 # Archivos para empaquetado
├── LICENSE                     # Apache 2.0
├── README.md                   # Este archivo
├── INSTALL.md                  # Guía detallada de instalación
└── CONTRIBUTING.md             # Guía de contribución
```

---

## Despliegue en Producción

### Con Systemd (Linux)

Crear `/etc/systemd/system/watchman.service`:

```ini
[Unit]
Description=WATCHMAN Home Lab Security Monitor
After=network.target

[Service]
Type=simple
User=watchman
WorkingDirectory=/opt/watchman
EnvironmentFile=/opt/watchman/.env
ExecStart=/opt/watchman/.venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Luego:

```bash
sudo systemctl daemon-reload
sudo systemctl enable watchman
sudo systemctl start watchman
sudo systemctl status watchman
```

### Permisos de Sudo

Editar con `sudo visudo`:

```
watchman ALL=(ALL) NOPASSWD: /usr/bin/reboot, /usr/bin/apt, /usr/bin/mount, /bin/mount, /usr/sbin/ufw, /usr/sbin/firewall-cmd, /usr/bin/lastb
```

### Con Docker Compose

Crear `docker-compose.yml`:

```yaml
version: '3.8'

services:
  watchman:
    build: .
    container_name: watchman-bot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
```

Luego:

```bash
docker-compose up -d
docker-compose logs -f
```

---

## Solución de Problemas

### El bot no responde

**Checklist:**
1. ¿BOT_TOKEN es correcto en `.env`?
2. ¿TG_USER_ID es tu ID (número), no tu nombre de usuario?
3. ¿El bot está corriendo? (`ps aux | grep python`)
4. ¿Hay errores? Ejecuta: `LOG_LEVEL=DEBUG python src/main.py`

### Errores de permisos

```bash
# Ver permisos actuales
sudo -l -U watchman

# Los comandos necesitan sudo, configura visudo
sudo visudo
```

### `/sslcheck` no funciona

Asegúrate de usar dominio válido: `/sslcheck example.com` ✅ vs `/sslcheck invalid@domain` ❌

### Temperatura inválida

```bash
# Encontrar la ruta correcta
find /sys -name "thermal_zone*"

# Editar .env si es necesario
TEMP_THERMAL_ZONE=/path/to/thermal/zone
```

---

## Logging

Los logs se guardan en la ruta especificada en `LOG_FILE` (por defecto: ninguno, solo consola).

**Configuración:**
- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR (default: INFO)
- `LOG_MAX_BYTES`: Tamaño máximo por archivo (default: 10MB)
- `LOG_BACKUP_COUNT`: Archivos de respaldo (default: 5)

Los archivos rotan automáticamente:
```
watchman.log       (actual)
watchman.log.1     (backup)
watchman.log.2     (backup)
...
watchman.log.5     (backup)
```

---

## Desarrollo

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.

---

## Seguridad

⚠️ **Importante:**
- Nunca compartir `BOT_TOKEN` públicamente
- Usar solo en redes de confianza
- Mantener `.env` fuera de control de versiones
- Revisar logs regularmente
- Mantener el sistema actualizado
- Usar usuario no-root para ejecutar el bot

---

## Licencia

Apache License 2.0 - Ver [LICENSE](LICENSE)

---

## Más Información

- 📖 [Guía Completa de Instalación](INSTALL.md)
- 🤝 [Cómo Contribuir](CONTRIBUTING.md)
- 🐛 [Reportar Issues](https://github.com/yourusername/WATCHMAN/issues)
