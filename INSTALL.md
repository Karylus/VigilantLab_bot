# Guía de Instalación - WATCHMAN

## Requisitos Previos

- **Python 3.11+**
- **Git**
- **Token de bot de Telegram** (@BotFather)
- **Tu ID de usuario de Telegram** (@userinfobot)

Verifica tus requisitos:
```bash
python3 --version
git --version
```

## Instalación Rápida

### Con `uv` (Recomendado)

```bash
# Instalar uv si no lo tienes
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
git clone https://github.com/yourusername/WATCHMAN.git
cd WATCHMAN

# Configurar
cp .env.example .env
# Editar .env con tus credenciales

# Construir y ejecutar
docker build -t watchman .
docker run --name watchman-bot -d --restart unless-stopped --env-file .env watchman

# Ver logs
docker logs -f watchman-bot
```

## Configuración

### Obtener Credenciales

**BOT_TOKEN:**
1. Busca `@BotFather` en Telegram
2. Envía `/newbot`
3. Sigue las instrucciones
4. Copia el token recibido

**TG_USER_ID:**
1. Busca `@userinfobot` en Telegram
2. Envía cualquier mensaje
3. Copia tu ID numérico

### Crear `.env`

```bash
cp .env.example .env
# Editar con tu editor favorito
nano .env
```

Contenido mínimo necesario:
```
BOT_TOKEN=123456789:ABCDEF1234567890abcdef1234567890abc
TG_USER_ID=987654321
```

Configuración opcional:
```
LOG_FILE=watchman.log
LOG_LEVEL=INFO
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
RATE_LIMIT_CALLS=10
RATE_LIMIT_WINDOW=60
TEMP_CRITICAL_THRESHOLD=110.0
REBOOT_DELAY=10
```

## Verificación

```bash
# Activar entorno
source .venv/bin/activate  # o .\.venv\Scripts\Activate.ps1 en Windows

# Listar paquetes
pip list

# Verificar compilación
python -m py_compile src/main.py

# Ejecutar bot
python src/main.py
```

Deberías ver:
```
Bot is now polling for updates... (Press Ctrl+C to stop)
```

## Prueba del Bot

1. Abre Telegram
2. Busca tu bot por nombre
3. Envía `/start`
4. Deberías ver el menú principal
5. Prueba algunos comandos

## Troubleshooting

### "ModuleNotFoundError: No module named 'telegram'"

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### "BOT_TOKEN not set in environment variables"

1. Verifica que `.env` existe en la raíz del proyecto
2. Asegúrate de que contiene: `BOT_TOKEN=tu_token_aqui`
3. Reinicia el bot

```bash
cat .env
```

### "TG_USER_ID not set or invalid"

1. Obtén tu ID correcto de `@userinfobot`
2. Debe ser un número, no un nombre de usuario
3. Verifica en `.env`: `TG_USER_ID=tu_id_aqui`

### El bot no responde en Telegram

**Checklist:**
1. ¿El bot está corriendo? `ps aux | grep python`
2. ¿BOT_TOKEN es correcto?
3. ¿TG_USER_ID es tu ID (número)?
4. ¿Hay errores? `LOG_LEVEL=DEBUG python src/main.py`

### "uv: command not found"

```bash
# Reiniciar terminal o shell
exec $SHELL

# O instalar manualmente
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Python 3.11+ no disponible

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv
```

**Fedora:**
```bash
sudo dnf install python3.11
```

**macOS:**
```bash
brew install python@3.11
```

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

## Próximos Pasos

1. Lee el [README.md](README.md) para conocer los comandos
2. Consulta [CONTRIBUTING.md](CONTRIBUTING.md) si deseas contribuir
3. Revisa logs regularmente: `tail -f watchman.log`

## Seguridad

⚠️ **Importante:**
- Nunca compartir `BOT_TOKEN` públicamente
- Mantener `.env` fuera de control de versiones
- Usar usuario no-root para ejecutar el bot
- Mantener el sistema actualizado
- Revisar logs regularmente