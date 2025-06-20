import os
import asyncio
import logging
import sys

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

# --- Environment Configuration ---
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

PORT = int(os.environ.get('PORT', 10000))  # Render uses 10000 by default

# Global application instance
application = None

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    logger.info(f"Received /start command from {user.id} (chat_id={chat_id})")
    
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! I'm your Telegram bot. How can I help you today?"
    )
    logger.info(f"Sent /start reply to {user.id}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all text messages that are not commands."""
    chat_id = update.effective_chat.id
    user_message = update.message.text
    
    logger.info(f"Received message from {chat_id}: '{user_message}'")
    
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Received your message: '{user_message}'. This is a test response.",
        )
        logger.info(f"Reply sent to {chat_id}")
    except Exception as e:
        logger.error(f"Failed to send message to {chat_id}: {e}")

async def webhook_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming webhook updates."""
    logger.info("Received update via webhook")
    await application.process_update(update)

async def set_webhook() -> None:
    """Configure the webhook for production environment."""
    webhook_url = f"{WEBHOOK_URL}/webhook"
    logger.info(f"Setting webhook to: {webhook_url}")
    
    try:
        await application.bot.set_webhook(
            url=webhook_url,
            secret_token=WEBHOOK_SECRET_TOKEN,
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
            max_connections=40
        )
        logger.info("Webhook configured successfully")
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        raise

def main() -> None:
    """Start the bot."""
    global application
    
    # Log environment variable status
    logger.info(f"TELEGRAM_BOT_TOKEN: {'set' if TELEGRAM_BOT_TOKEN else 'missing'}")
    logger.info(f"WEBHOOK_URL: {'set' if WEBHOOK_URL else 'missing'}")
    logger.info(f"WEBHOOK_SECRET_TOKEN: {'set' if WEBHOOK_SECRET_TOKEN else 'missing'}")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(TypeHandler(Update, webhook_handler))

    # Start the Bot
    if WEBHOOK_URL:
        logger.info("Starting in production mode with webhook")
        
        # Set up webhook
        loop = asyncio.get_event_loop()
        loop.run_until_complete(set_webhook())
        
        # Run webhook server
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=f"{WEBHOOK_URL}/webhook",
            secret_token=WEBHOOK_SECRET_TOKEN,
        )
    else:
        logger.info("Starting in development mode with polling")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
