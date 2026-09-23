import os
import uuid
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋\n"
        "فایلت رو بفرست تا لینک دانلودش رو برات بسازم."
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
    file_path = DOWNLOAD_DIR / f"{file_id}_{safe_name}"

    await telegram_file.download_to_drive(str(file_path))

    await message.reply_text(
        f"✅ فایل دریافت شد.\n\n"
        f"🔗 لینک فایل:\n"
        f"فعلاً مرحله ساخت لینک وب باقی مانده."
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.Document.ALL | filters.VIDEO | filters.AUDIO,
            handle_file,
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()
