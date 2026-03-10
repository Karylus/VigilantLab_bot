import logging
import re
import os
import subprocess
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters

load_dotenv(override=True)
TOKEN = os.getenv("BOT_TOKEN")
TG_USER_ID = int(os.getenv("TG_USERNAME"))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.WARNING
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Bienvenido! Con este bot podrás comunicarte con tu Home Lab. \nLos comandos disponibles son:"
        "\n/reboot - Reinicia el home lab."
        "\n/status - Muestra si el home lab está encendido."
        "\n/update - Actualiza los paquetes del sistema"
        "\n/temp - Muestra la temperatura de la CPU.",
    )


async def reboot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Solicitando reinicio del home lab..."
    )

    def schedule_reboot(delay_seconds: int = 10) -> tuple[bool, str]:
        try:
            cmd = ["bash", "-lc", f"(sleep {delay_seconds} && sudo reboot) &"]
            res = subprocess.run(cmd, capture_output=True, text=True)
            output = (res.stdout or "") + (res.stderr or "")
            return res.returncode == 0, output.strip()
        except Exception as e:
            return False, str(e)

    ok, out = schedule_reboot(delay_seconds=10)

    if ok:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Reinicio programado en 10 segundos. El sistema se reiniciará pronto.",
        )
    else:
        msg = "No se pudo programar el reinicio."
        if out:
            msg += f" Detalles: {out}"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg,
        )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    def get_status() -> tuple[bool, str]:
        try:
            terminal = ["ping", "127.0.0.1", "-c", "3"]
            res = subprocess.run(terminal, capture_output=True, text=True)
            output = (res.stdout or "") + (res.stderr or "")
            return res.returncode == 0, output.strip()
        except Exception as e:
            return f"Error: {str(e)}", ""

    ok, out = get_status()

    if ok:
        status_msg = "El home lab está funcionando correctamente."
    else:
        status_msg = "El home lab no está funcionando."
        if out:
            status_msg += f"\nDetalles: {out}"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=status_msg,
    )


async def update_packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Se van a actualizar los paquetes del sistema.",
    )

    def update_packages() -> tuple[bool, str]:
        try:
            terminal = ["sudo", "apt", "update"]
            res = subprocess.run(terminal, capture_output=True, text=True)
            output = (res.stdout or "") + (res.stderr or "")
            return res.returncode == 0, output.strip()
        except Exception as e:
            return f"Error: {str(e)}", ""

    def upgrade_packages() -> tuple[bool, str]:
        try:
            terminal = ["sudo", "apt", "upgrade", "-y"]
            res = subprocess.run(terminal, capture_output=True, text=True)
            output = (res.stdout or "") + (res.stderr or "")
            return res.returncode == 0, output.strip()
        except Exception as e:
            return f"Error: {str(e)}", ""

    ok_update, out_update = update_packages()

    if ok_update:
        ok_upgrade, out_upgrade = upgrade_packages()
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Error al actualizar paquetes.",
        )

    if ok_upgrade:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Actualización de paquetes completada.",
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Error al actualizar paquetes.",
        )


async def temp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        terminal = ["cat", "/sys/class/thermal/thermal_zone0/temp"]
        res = subprocess.run(terminal, capture_output=True, text=True)
        output = (res.stdout or "") + (res.stderr or "")
        value_str = output.strip()

        if not value_str:
            raise ValueError("Salida vacía al leer la temperatura")

        try:
            temp_milli = int(value_str)
        except ValueError:
            m = re.search(r"-?\d+", value_str)
            if m:
                temp_milli = int(m.group())
            else:
                raise ValueError(f"Valor de temperatura no válido: {value_str}")

        temp_c = temp_milli / 1000.0
        critical_threshold_milli = 110000
        is_critical = temp_milli > critical_threshold_milli

        critical_msg = " CRÍTICA: la temperatura supera 110°C." if is_critical else ""

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Temperatura actual: {temp_c:.1f} °C. {critical_msg}",
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Error al obtener la temperatura: {str(e)}",
        )


async def remount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    def remount_disks() -> tuple[bool, str]:
        try:
            terminal = ["sudo", "mount", "-a"]
            res = subprocess.run(terminal, capture_output=True, text=True)
            output = (res.stdout or "") + (res.stderr or "")
            return res.returncode == 0, output.strip()
        except Exception as e:
            return f"Error: {str(e)}", ""

    ok, out = remount_disks()

    if ok:
        status_msg = "Se ha montado el disco correctamente."
    else:
        status_msg = "No se ha podido montar el disco."
        if out:
            status_msg += f"\nDetalles: {out}"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=status_msg,
    )


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler("start", start, filters=filters.User(TG_USER_ID))
    application.add_handler(start_handler)

    reboot_handler = CommandHandler("reboot", reboot, filters=filters.User(TG_USER_ID))
    application.add_handler(reboot_handler)

    status_handler = CommandHandler("status", status, filters=filters.User(TG_USER_ID))
    application.add_handler(status_handler)

    update_handler = CommandHandler(
        "update", update_packages, filters=filters.User(TG_USER_ID)
    )
    application.add_handler(update_handler)

    temp_handler = CommandHandler("temp", temp, filters=filters.User(TG_USER_ID))
    application.add_handler(temp_handler)

    remount_handler = CommandHandler(
        "remount", remount, filters=filters.User(TG_USER_ID)
    )
    application.add_handler(remount_handler)

    application.run_polling()
