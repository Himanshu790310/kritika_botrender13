import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
SECRET_TOKEN = os.getenv('WEBHOOK_SECRET_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Start command from {update.effective_user.id}")
    await update.message.reply_text('Bot is alive!')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Message from {update.effective_user.id}: {update.message.text}")
    await update.message.reply_text(f'You said: {update.message.text}')

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    if WEBHOOK_URL:
        logger.info("Starting in webhook mode")
        app.run_webhook(
            listen="0.0.0.0",
            port=10000,
            webhook_url=f"{WEBHOOK_URL}/webhook",
            secret_token=SECRET_TOKEN,
        )
    else:
        logger.info("Starting in polling mode")
        app.run_polling()

if __name__ == "__main__":
    main()
