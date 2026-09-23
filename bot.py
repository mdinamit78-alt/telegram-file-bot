import os
import uuid
from pathlib import Path

from flask import Flask, send_from_directory
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
BASE_URL = os.environ["RENDER_EXTERNAL_URL"]

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

app_web = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()


@app_web.route("/")
def home():
    return "Telegram File Bot is running!"


@app_web.route("/files/<filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋\n"
        "فایل رو بفرست تا لینک دانلودش رو برات بسازم."
    )


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if message.document:
        telegram_file = await message.document.get_file()
        original_name = message.document.file_name or "file"
    elif message.video:
        telegram_file = await message.video.get_file()
        original_name = "video.mp4"
    elif message.audio:
        telegram_file = await message.audio.get_file()
        original_name = "audio.mp3"
    else:
        return

    file_id = uuid.uuid4().hex
    safe_name = Path(original_name).name
    stored_name = f"{file_id}_{safe_name}"
    file_path = DOWNLOAD_DIR / stored_name

    await telegram_file.download_to_drive(str(file_path))

    link = f"{BASE_URL}/files/{stored_name}"

    await message.reply_text(
        f"✅ فایل آماده شد!\n\n"
        f"🔗 لینک دانلود:\n{link}"
    )


telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(
    MessageHandler(
        filters.Document.ALL | filters.VIDEO | filters.AUDIO,
        handle_file,
    )
)


@app_web.post("/telegram")
async def telegram_webhook():
    data = await app_web.request.get_json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK"


if __name__ == "__main__":
    import asyncio
    from threading import Thread

    async def initialize():
        await telegram_app.initialize()
        await telegram_app.bot.set_webhook(
            url=f"{BASE_URL}/telegram"
        )

    asyncio.run(initialize())

    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)
