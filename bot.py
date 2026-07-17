import logging
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from core.config import TELEGRAM_TOKEN
from core.memory import handle_message

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Render Ke Liye Dummy Web Server ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Avni V2.0 is Alive and Running!"

def run_flask():
    # Render default port 10000 use karta hai
    app.run(host='0.0.0.0', port=10000)
# -------------------------------------

def main():
    logger.info("========================================")
    logger.info("🤖 Avni V2.0 Modular System Booting...")
    logger.info("========================================")

    # 1. Flask server ko alag thread me start karo taaki Render ko open port mile
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # 2. Telegram Application Build karo
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Handlers attach karo
    application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("👋 Hello! Main Avni Bot hoon. Kaise madad karu aapki?")))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Bot ko polling mode me start karo
    logger.info("Application started")
    application.run_polling()

if __name__ == '__main__':
    main()