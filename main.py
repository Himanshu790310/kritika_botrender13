import os
import asyncio
import logging
import sys
import re

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    TypeHandler
)

# --- Logger Setup ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("TelegramBot")

# --- Environment Validation ---
def get_env_var(name):
    value = os.environ.get(name)
    if not value:
        logger.error(f"Missing required environment variable: {name}")
        return None
    return value

TELEGRAM_BOT_TOKEN = get_env_var('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = get_env_var('WEBHOOK_URL')
WEBHOOK_SECRET_TOKEN = get_env_var('WEBHOOK_SECRET_TOKEN')

if not all([TELEGRAM_BOT_TOKEN, WEBHOOK_URL, WEBHOOK_SECRET_TOKEN]):
    logger.error("Shutting down due to missing environment variables")
    sys.exit(1)

PORT = int(os.environ.get('PORT', 10000))

# --- Bot Handlers ---
application = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your bot.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You said: {update.message.text}")

async def set_webhook():
    try:
        webhook_url = f"{WEBHOOK_URL}/webhook"
        logger.info(f"Setting webhook to: {webhook_url}")
        
        await application.bot.set_webhook(
            url=webhook_url,
            secret_token=WEBHOOK_SECRET_TOKEN,
            drop_pending_updates=True,
            max_connections=10,
            allowed_updates=Update.ALL_TYPES,
            certificate=None  # Disable certificate verification
        )
        
        logger.info("Webhook set successfully")
    except Exception as e:
        logger.error(f"Webhook setup failed: {str(e)}")
        sys.exit(1)

def main():
    global application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    if WEBHOOK_URL:
        logger.info("Starting in webhook mode")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(set_webhook())
        
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=f"{WEBHOOK_URL}/webhook",
            secret_token=WEBHOOK_SECRET_TOKEN,
            cert=None,
            key=None,
        )
    else:
        logger.info("Starting in polling mode")
        application.run_polling()

if __name__ == "__main__":
    main()
