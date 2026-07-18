import logging
import threading
import json
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from core.config import TELEGRAM_TOKEN
from core.memory import add_history, get_history, build_profile_prompt, get_profile
from core.gemini import generate_reply as generate_response
from core.prompt import SYSTEM_INSTRUCTION

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Render Dummy Port Server ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Avni V2.0 is Router Active!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)
# --------------------------------

async def handle_message(update, context):
    user_text = update.message.text
    
    # 1. Message save karo
    add_history(context, role="user", text=user_text)
    
    # 2. State loading
    chat_history = get_history(context)
    user_profile = get_profile(context)
    
    # 3. Context & Prompt combination
    profile_prompt = build_profile_prompt(user_profile)
    full_system_prompt = f"{SYSTEM_INSTRUCTION}\n\n{profile_prompt}"
    
    # --- 🔍 DEBUG PIPELINE LOGS ---
    logger.info("---------- AVNI PIPELINE DEBUG ----------")
    logger.info(f"User Text: {user_text}")
    logger.info(f"Full System Prompt Length: {len(full_system_prompt)} chars")
    logger.info(f"Chat History Payload: {json.dumps(chat_history, indent=2)}")
    logger.info("-----------------------------------------")
    
    try:
        # 4. API Hit
        bot_response = await generate_response(chat_history, full_system_prompt)
        
        # 5. History update
        add_history(context, role="model", text=bot_response)
        
        # 6. Final UI update
        await update.message.reply_text(bot_response)
        
    except Exception as e:
        # Pura traceback report trace karega
        logger.error(f"[CRITICAL BOT ROUTER ERROR]: {e}", exc_info=True)
        await update.message.reply_text("Oops! Mera system thoda freeze ho gaya. Ek baar fir se try karna? 🥺")

def main():
    logger.info("========================================")
    logger.info("🤖 Avni V2.0 Pure Router Deploying...")
    logger.info("========================================")

    # Threading setup for Render port scanning
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Handlers (Natural human behavior integration)
    application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Heyy! Main Avni. ✨ Batao kaise yaad kiya aaj?")))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Application successfully running in routing mode.")
    application.run_polling()

if __name__ == '__main__':
    main()
