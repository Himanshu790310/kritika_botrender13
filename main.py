import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize bot
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SECRET_TOKEN = "yrytdrxdDYsrRfYDDEYFEDCTtddtyedfdssDTSXddyYTFyfedtyd5ft"  # Your secret token

# Initialize application
application = Application.builder().token(TOKEN).build()

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bot is working! Send me a message.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🔁 You said: {update.message.text}")

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@app.route("/webhook", methods=["POST"])
async def webhook():
    # Verify secret token
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != SECRET_TOKEN:
        logger.warning("⚠️ Invalid secret token")
        return "Unauthorized", 401

    try:
        update = Update.de_json(request.get_json(), application.bot)
        await application.process_update(update)
        return "OK", 200
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return "Error", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
