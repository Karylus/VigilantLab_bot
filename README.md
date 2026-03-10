# VigilantLab Bot (WATCHMAN)

VigilantLab Bot (repository: WATCHMAN) is a small Telegram bot to help you remotely manage and monitor a home lab. It exposes a set of restricted commands for a single allowed Telegram user to perform common maintenance tasks like checking status, scheduling a reboot, updating packages, reading CPU temperature, and remounting disks.

This README explains how to configure, run and extend the bot, and includes tips for logging and deployment.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the bot](#running-the-bot)
- [Available commands](#available-commands)
- [Logging and filtering noisy messages](#logging-and-filtering-noisy-messages)
- [Deployment suggestions](#deployment-suggestions)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- Restricted access — only a single Telegram user (configured by ID) can use the bot.
- Commands implemented:
  - `/start` — welcome/help message
  - `/reboot` — schedule a reboot
  - `/status` — run a quick connectivity check (ping)
  - `/update` — run `apt update` and `apt upgrade -y`
  - `/temp` — read CPU temperature from `/sys/class/thermal/thermal_zone0/temp`
  - `/remount` — run `mount -a`
- Uses `python-telegram-bot` for Telegram integration.
- Minimal external dependencies; configuration via `.env`.

---

## Prerequisites

- Python 3.8+ (code uses modern typing and asyncio)
- A machine capable of running the commands used by the bot (some actions require `sudo` privileges)
- Telegram bot token (from BotFather)
- Telegram numeric user ID for the person allowed to use the bot
- Recommended: run inside a virtual environment

---

## Installation

1. Clone the repository:

   git clone https://github.com/<your-username>/WATCHMAN.git
   cd WATCHMAN

2. Create and activate a virtual environment:

   python -m venv venv
   # On Unix/macOS
   source venv/bin/activate
   # On Windows (PowerShell)
   .\venv\Scripts\Activate.ps1

3. Install dependencies:

   pip install -r requirements.txt

If `requirements.txt` is not present in the repo, install the likely dependencies manually:

   pip install python-telegram-bot python-dotenv

---

## Configuration

Create a `.env` file in the project root with the following variables:

- `BOT_TOKEN` — the token from BotFather (string)
- `TG_USERNAME` — the numeric Telegram user ID allowed to use the bot (integer)

Example `.env`:

BOT_TOKEN=123456789:ABCDEF...your_token_here...
TG_USERNAME=123456789

Important: In the code `TG_USER_ID = int(os.getenv("TG_USERNAME"))` — the environment variable must contain a numeric ID, not a username handle.

Security note: Keep the `.env` file out of version control. Add it to `.gitignore`.

---

## Running the bot

Start the bot from the project directory:

   python main.py

The bot uses `application.run_polling()` and will poll Telegram for updates. For a production deployment, prefer running it under a process manager or systemd service (see [Deployment suggestions](#deployment-suggestions)).

---

## Available commands

All commands are filtered so only the configured `TG_USERNAME` (ID) can run them.

- `/start` — Shows a welcome message and lists available commands.
- `/reboot` — Schedules a reboot after a short delay (the implementation uses a background shell sleep + `sudo reboot`). Use with caution.
- `/status` — Performs a quick local `ping` to determine reachability.
- `/update` — Runs `sudo apt update` and then `sudo apt upgrade -y`. May require `sudo` without password or appropriate permissions.
- `/temp` — Reads CPU temperature from the standard Linux sysfs thermal interface and reports degrees Celsius.
- `/remount` — Runs `sudo mount -a` to remount filesystems.

Note: Many commands call `sudo`. For a headless remote bot, you may need to configure `sudoers` to allow the bot's runtime user to run specific commands without a password. Be careful and follow least-privilege principles.

---

## Logging and filtering noisy messages

The bot configures Python logging with a basic format. In some environments or library versions, the Telegram library can emit noisy messages such as `getUpdates` logs. You can reduce noise by:

1. Setting the `telegram` library logger to a higher level (e.g., `WARNING`), while keeping your application logger at `INFO`:

   logging.basicConfig(
       format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
       level=logging.INFO,
   )
   # Reduce noise from python-telegram-bot:
   logging.getLogger("telegram").setLevel(logging.WARNING)

2. Alternatively, add a custom logging filter that excludes messages containing a specific substring (for example `getUpdates`):

   ```python
   import logging

   class ExcludeMessageFilter(logging.Filter):
       def __init__(self, pattern: str, case_insensitive: bool = True):
           super().__init__()
           self.pattern = pattern
           self.case_insensitive = case_insensitive

       def filter(self, record: logging.LogRecord) -> bool:
           try:
               msg = record.getMessage() or ""
               if self.case_insensitive:
                   return self.pattern.lower() not in msg.lower()
               else:
                   return self.pattern not in msg
           except Exception:
               # On error, allow the record
               return True

   # Create and register the filter
   exclude_filter = ExcludeMessageFilter("getUpdates", case_insensitive=True)
   logging.getLogger("telegram").addFilter(exclude_filter)
   # Or to affect all logs:
   # logging.getLogger().addFilter(exclude_filter)
   ```

3. If you want persistent logs, combine the above with a `RotatingFileHandler` to prevent unbounded log growth.

---

## Deployment suggestions

- Use a system service (systemd) or a process manager (supervisord, pm2 for Python wrappers, or Docker) to keep the bot running and automatically restart it on failure.
- Run the bot under a dedicated system user with minimal privileges.
- If the bot must execute `sudo` commands, restrict allowed commands in `/etc/sudoers` (use `visudo`) to avoid granting a wide scope of permissions.
- For remote deployment, secure the machine (firewall, SSH keys) and ensure backups or monitoring are in place.

Example systemd service template:

   [Unit]
   Description=VigilantLab Bot
   After=network.target

   [Service]
   Type=simple
   User=watchman
   WorkingDirectory=/path/to/WATCHMAN
   EnvironmentFile=/path/to/WATCHMAN/.env
   ExecStart=/path/to/venv/bin/python main.py
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target

Adjust paths, user, and environment as required.

---

## Troubleshooting

- Bot does not respond:
  - Verify the bot token in `.env`.
  - Confirm `TG_USERNAME` is the numeric ID of your Telegram user and matches the one sending commands.
  - Check logs for exceptions.
- Permission errors when running commands:
  - Many commands use `sudo`. Make sure the runtime user can execute required commands or run the process as a user with the correct privileges.
- Temperature reading returns invalid values:
  - The bot reads `/sys/class/thermal/thermal_zone0/temp`. Hardware or OS differences may use a different path; adjust the code if necessary.
- Too many log messages from Telegram library:
  - Use the logging recommendations above to filter or raise the `telegram` logger level.

---

## Contributing

Contributions are welcome. Suggested workflow:

1. Open an issue to discuss larger changes.
2. Fork the repository and create a feature branch.
3. Submit a pull request with clear description and tests (if applicable).

Coding style:
- Keep code readable and documented.
- Guard dangerous operations (reboot, mount, apt operations) behind restrictions and clear logging.
- Prefer small, focused commits.

---

## Security & Safety Notes

- Rebooting, updating and remounting filesystems remotely are sensitive actions. Ensure you understand the implications and restrict usage to trusted users.
- Do not store secrets (like bot tokens) in public repositories. Use environment variables and secret managers for CI/CD.
- When granting `sudo` permissions, always limit them to the specific commands the bot needs, not to full `NOPASSWD: ALL`.

---

## License

This project is licensed under the Apache License 2.0. See the `LICENSE` file in the repository root for the full license text.