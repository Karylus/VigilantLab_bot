# WATCHMAN - Home Lab Security Monitor Bot

WATCHMAN es un bot de Telegram avanzado diseñado para monitorizar y auditar remotamente tu Home Lab. Proporciona acceso seguro (restringido a un único usuario autorizado) a un conjunto completo de herramientas de análisis de seguridad, estado del sistema y mantenimiento.

**✨ Características principales:**
- 🔒 **Acceso restringido** — Solo un usuario de Telegram autorizado puede usar el bot
- 🎮 **Sistema de menús interactivos** — Navegación intuitiva sin necesidad de recordar comandos
- 🔐 **15+ comandos de seguridad** — Análisis exhaustivo de amenazas, conexiones, puertos, servicios y más
- ⚡ **Verificación SSL/TLS nativa** — Sin dependencias de openssl externo
- 🚨 **Detección de amenazas** — Análisis heurístico de indicadores de compromiso (IoC)
- 📊 **Salidas formateadas** — Mensajes legibles y bien estructurados en Telegram
- 🏗️ **Arquitectura modular** — Fácil de extender y mantener

---

## Tabla de Contenidos

- [Características](#características)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecutar el Bot](#ejecutar-el-bot)
- [Comandos Disponibles](#comandos-disponibles)
  - [Comandos de Sistema](#comandos-de-sistema)
  - [Comandos de Seguridad](#comandos-de-seguridad)
  - [Comandos de Mantenimiento](#comandos-de-mantenimiento)
- [Sistema de Menús Interactivos](#sistema-de-menús-interactivos)
- [Arquitectura](#arquitectura)
- [Logging](#logging)
- [Sugerencias de Despliegue](#sugerencias-de-despliegue)
- [Solución de Problemas](#solución-de-problemas)
- [Licencia](#licencia)

---

## Características

### 🖥️ Monitoreo de Sistema
- Estado general del sistema
- Temperatura de CPU
- Reinicio programado
- Actualización de paquetes
- Remontaje de sistemas de archivos

### 🔐 Auditoría de Seguridad (15 comandos)
- **Análisis de Red:**
  - Conexiones TCP activas
  - Puertos abiertos y servicios escuchando
  - Procesos con conexiones de red
  - Diagnóstico de red

- **Firewall & Acceso:**
  - Estado del firewall
  - Reglas activas del firewall
  - Intentos fallidos de login
  - Sesiones activas de usuarios

- **Autenticación & Credenciales:**
  - Auditoría de claves SSH
  - Configuración de sudoers
  - Política de contraseñas

- **Análisis de Procesos & Servicios:**
  - Procesos con mayor consumo de recursos
  - Servicios activos del sistema
  - Archivos SUID (posible escalada de privilegios)
  - Tareas cron programadas

- **Criptografía:**
  - Verificación de certificados SSL/TLS (con validación nativa)

- **Detección de Amenazas:**
  - 🚨 **Análisis de Amenazas** — Detección heurística de IoCs y comportamientos sospechosos
  - Evaluación de riesgo por puntuación
  - Recomendaciones contextualizadas

### 🔧 Mantenimiento
- Actualización del sistema
- Reinicio programado
- Remontaje de filesystems

---

## Requisitos Previos

- **Python 3.11+** (se recomienda 3.11 o 3.12)
- **Sistema operativo:** Linux (Debian/Ubuntu recomendado)
- **Token del bot de Telegram** (obtener de BotFather)
- **ID numérico de usuario de Telegram** autorizado
- **Entorno virtual** de Python (recomendado)
- **Herramientas de sistema:** 
  - `ss` o `netstat` — análisis de conexiones
  - `systemctl` o `service` — gestión de servicios
  - `sudo` — acceso a comandos administrativos
  - Opcional: `ufw`, `firewalld` para análisis de firewall

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/<your-username>/WATCHMAN.git
cd WATCHMAN
```

### 2. Crear y activar entorno virtual

```bash
# En Unix/macOS/Linux
python3 -m venv venv
source venv/bin/activate

# En Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

O instalar manualmente:

```bash
pip install python-telegram-bot>=22.5 python-dotenv>=1.0.0
```

---

## Configuración

### Crear archivo `.env`

En la raíz del proyecto, crea un archivo `.env` con las siguientes variables:

```
BOT_TOKEN=123456789:ABCDEF1234567890abcdef1234567890abc
TG_USER_ID=987654321
```

**Variables requeridas:**
- `BOT_TOKEN` — Token del bot (obtenido de BotFather)
- `TG_USER_ID` — ID numérico de tu usuario de Telegram (no el nombre de usuario)

**Obtener tu ID de Telegram:**
1. Escribe `@userinfobot` en Telegram
2. El bot te devolverá tu ID numérico

**Seguridad:**
- Nunca compartir el `BOT_TOKEN` públicamente
- Mantener `.env` fuera del control de versiones (añadir a `.gitignore`)
- Usar un usuario de Telegram de confianza como `TG_USER_ID`

---

## Ejecutar el Bot

Desde el directorio raíz del proyecto:

```bash
python src/main.py
```

El bot se conectará a Telegram y comenzará a escuchar comandos del usuario autorizado.

Para detener el bot: `Ctrl+C`

---

## Comandos Disponibles

### Comandos de Sistema

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/start` | Muestra el menú principal interactivo | `/start` |
| `/status` | Estado general del sistema | `/status` |
| `/temp` | Temperatura actual del CPU | `/temp` |
| `/reboot` | Programa reinicio del sistema | `/reboot` |
| `/update` | Actualiza paquetes del sistema | `/update` |
| `/remount` | Remonta sistemas de archivos | `/remount` |

### Comandos de Seguridad

#### Análisis de Red
| Comando | Descripción |
|---------|-------------|
| `/connections` | 🌐 Lista conexiones TCP activas |
| `/openports` | 🔓 Muestra puertos abiertos y servicios |
| `/networkproc` | 🔗 Procesos con conexiones de red |

#### Firewall & Acceso
| Comando | Descripción |
|---------|-------------|
| `/firewall` | 🔥 Estado del firewall |
| `/fwrules` | 📋 Reglas activas del firewall |
| `/failedlogins` | 🔐 Intentos recientes de login fallidos |
| `/sessions` | 👥 Usuarios actualmente conectados |

#### Autenticación
| Comando | Descripción |
|---------|-------------|
| `/sshkeys` | 🔑 Audita claves SSH autorizadas |
| `/sudoers` | 👤 Lista usuarios con privilegios sudo |

#### Procesos & Servicios
| Comando | Descripción |
|---------|-------------|
| `/topproc` | ⚙️ Procesos con mayor consumo de recursos |
| `/services` | 🚀 Servicios activos del sistema |
| `/suidfiles` | ⚠️ Archivos SUID (escalada potencial) |
| `/cronjobs` | ⏰ Tareas cron programadas |

#### Criptografía & Auditoría
| Comando | Descripción |
|---------|-------------|
| `/sslcheck <dominio>` | 🔐 Verifica certificados SSL/TLS |
| `/audit` | 🔒 Auditoría completa de seguridad |
| `/threats` | 🚨 Análisis de amenazas y IoC |

### Comandos de Mantenimiento

| Comando | Descripción |
|---------|-------------|
| `/update` | ⬆️ Actualiza el sistema |
| `/reboot` | 🔄 Reinicia el sistema |
| `/remount` | 💾 Remonta filesystems |

---

## Sistema de Menús Interactivos

WATCHMAN incluye un sistema completo de menús interactivos accesibles a través de botones inline en Telegram.

### Estructura de Menús

```
🤖 WATCHMAN v1.0
├── 📊 SISTEMA
│   ├── 📈 Estado
│   ├── 🌡️ Temperatura
│   ├── ⬆️ Actualizar
│   ├── 🔄 Reiniciar
│   └── 💾 Remontar
├── 🔒 SEGURIDAD
│   ├── 🌐 Conexiones
│   ├── 🔓 Puertos
│   ├── 🔗 Procesos Red
│   ├── 🔥 Firewall
│   ├── 📋 Reglas FW
│   ├── ❌ Login Fallido
│   ├── 👥 Sesiones
│   ├── 🔑 SSH Keys
│   ├── 👤 Sudoers
│   ├── ⚙️ Top Proc
│   ├── 🚀 Servicios
│   ├── 🔐 SSL Check
│   ├── ⚠️ SUID
│   ├── ⏰ Cron
│   ├── 📊 Auditoria
│   └── 🚨 Amenazas
├── 🔧 MANTENIMIENTO
│   ├── ⬆️ Actualizar
│   ├── 🔄 Reiniciar
│   └── 💾 Remontar FS
└── ℹ️ AYUDA
```

**Uso:**
1. Ejecuta `/start` para ver el menú principal
2. Presiona los botones para navegar
3. Selecciona un comando para ejecutarlo
4. Los resultados se muestran en mensajes formateados
5. Presiona "Atrás" para volver al menú anterior

---

## Arquitectura

### Estructura del Proyecto

```
WATCHMAN/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada
│   ├── config.py               # Configuración y variables globales
│   ├── handler.py              # Manejo de comandos
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── base.py             # Clase base para comandos
│   │   ├── handler.py          # Gestor de comandos
│   │   ├── security.py         # Comandos de seguridad
│   │   ├── system.py           # Comandos de sistema
│   │   └── maintenance.py      # Comandos de mantenimiento
│   ├── services/
│   │   ├── __init__.py
│   │   ├── command_executor.py # Ejecutor de comandos del sistema
│   │   └── security_functions.py # Lógica de auditoría de seguridad
│   └── utils/
│       ├── __init__.py
│       ├── formatters.py       # Formateo de salidas para Telegram
│       └── menus.py            # Sistema de menús interactivos
├── .env.example                # Ejemplo de configuración
├── .gitignore
├── .python-version             # Versión de Python recomendada
├── README.md                   # Este archivo
├── LICENSE                     # Apache 2.0
└── pyproject.toml              # Configuración del proyecto
```

### Patrones de Diseño

- **Command Pattern:** Cada comando hereda de `BaseCommand`
- **Service Layer:** Lógica de negocio separada en `SecurityService` y `CommandExecutor`
- **Factory Pattern:** Menus construidos dinámicamente
- **Async/Await:** Operaciones no bloqueantes con asyncio

---

## Logging

El bot incluye logging automático en la consola. Para ajustar el nivel de detalle:

### Reducir ruido de la librería Telegram

En `src/main.py`:

```python
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Reduce verbose logs from python-telegram-bot
logging.getLogger("telegram").setLevel(logging.WARNING)
```

### Habilitar logging a archivo

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'watchman.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)
```

---

## Sugerencias de Despliegue

### Ejecución Manual (Desarrollo)

```bash
python src/main.py
```

### Servicio Systemd (Producción)

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
ExecStart=/opt/watchman/venv/bin/python src/main.py
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

Para que el bot ejecute comandos con privilegios, configurar sudoers (usar `visudo`):

```
# Permitir al usuario 'watchman' ejecutar comandos específicos sin contraseña
watchman ALL=(ALL) NOPASSWD: /usr/bin/reboot, /usr/bin/apt, /usr/bin/mount, /bin/mount, /usr/sbin/ufw, /usr/sbin/firewall-cmd, /usr/bin/lastb
```

### Docker (Opcional)

Crear `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY .env .

CMD ["python", "src/main.py"]
```

Ejecutar:

```bash
docker build -t watchman .
docker run --name watchman-bot \
  -e BOT_TOKEN=<your_token> \
  -e TG_USER_ID=<your_id> \
  -d watchman
```

---

## Solución de Problemas

### El bot no responde

**Checklist:**
1. ¿Es correcto el `BOT_TOKEN` en `.env`?
2. ¿Es correcto el `TG_USER_ID`? (debe ser tu ID de Telegram, no tu nombre)
3. ¿El bot está en ejecución? (`python src/main.py`)
4. ¿Hay errores en los logs?

```bash
# Ejecutar con logging verbose
python -u src/main.py
```

### Errores de permisos en comandos

Muchos comandos requieren `sudo`. Asegúrate de:

1. Añadir el usuario a sudoers (ver sección Despliegue)
2. O ejecutar el bot como root (no recomendado)

```bash
# Ver permisos actuales
sudo -l -U watchman
```

### Comando `/sslcheck` no funciona

Asegúrate de que el dominio es válido:

```
❌ /sslcheck invalid@domain  (incorrecto)
✅ /sslcheck example.com      (correcto)
```

### Temperatura devuelve valores inválidos

El bot lee `/sys/class/thermal/thermal_zone0/temp`. En algunos sistemas está en otra ruta:

```bash
# Encontrar la ruta correcta
find /sys -name "thermal_zone*"
```

Luego editar `src/services/command_executor.py` si es necesario.

### Demasiados logs de "getUpdates"

Ver sección de [Logging](#logging) para filtrar mensajes de Telegram.

---

## Desarrollo

### Ejecutar con entorno virtual

```bash
source venv/bin/activate  # En Linux/macOS
python src/main.py
```

### Añadir un nuevo comando

1. Crear clase en `src/commands/security.py` (o el archivo apropiado):

```python
from src.commands.base import BaseCommand

class MiComandoCommand(BaseCommand):
    name = "micomando"
    description = "🎯 Descripción del comando"
    
    async def execute(self, update, context):
        # Lógica aquí
        await self.send_message(update, context, "Resultado")
```

2. Registrar en `src/commands/handler.py`:

```python
from src.commands.security import MiComandoCommand

self.commands = {
    # ... otros comandos
    "micomando": MiComandoCommand(),
}
```

3. Añadir al menú en `src/utils/menus.py`

### Ejecutar tests

```bash
pytest tests/
```

---

## Seguridad & Notas Importantes

⚠️ **Riesgos Operacionales:**
- Reboots y updates remotos pueden interrumpir servicios
- Cambios en firewall pueden bloquear acceso
- Asegúrate de entender completamente qué haces

🔐 **Mejores Prácticas:**
- **Nunca** compartir el `BOT_TOKEN` públicamente
- Limitar permisos de sudo al mínimo necesario
- Usar solo en redes de confianza
- Mantener el sistema actualizado
- Revisar logs regularmente
- Usar VPN si accedes desde Internet

🛡️ **Restricciones de Seguridad:**
- Solo el `TG_USER_ID` configurado puede usar el bot
- Los comandos se ejecutan con los permisos del usuario que corre el bot
- No hay auditoría de comandos ejecutados a través del bot (considera añadirla)

---

## Contribuciones

Las contribuciones son bienvenidas. Flujo sugerido:

1. Abre un issue para discutir cambios importantes
2. Fork del repositorio y crea una rama de feature
3. Envía un pull request con descripción clara
4. Asegúrate de que pase los tests

---

## Licencia

Este proyecto está bajo licencia **Apache License 2.0**. Ver archivo `LICENSE` para más detalles.

---

## Cambios Recientes (v1.0.0)

✅ **15 comandos de seguridad completamente implementados**
✅ **Sistema de menús interactivos mejorado**
✅ **Detección de amenazas (análisis de IoC)**
✅ **Verificación SSL/TLS nativa (sin openssl externo)**
✅ **Formateo mejorado de salidas**
✅ **socket.getservbyport() para resolución dinámica de servicios**
✅ **Arquitectura modular y escalable**

---

**¿Preguntas o problemas?** Abre un issue en el repositorio.

**Hecho con ❤️ para tu Home Lab.**