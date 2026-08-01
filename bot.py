import logging
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from core.config import TELEGRAM_TOKEN
from core.gemini_service import generate_reply_with_context
from core.humanizer import humanize_response
from memory.ranking import extract_ranked_facts
from memory.context_builder import build_full_prompt_context
from storage.db import save_fact, save_message, ensure_user

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

web_app = Flask(__name__)

@web_app.route("/")
def health_check():
    return "Avni Bot Engine is Running Healthy!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user:
        ensure_user(user.id, first_name=user.first_name or "")
        await update.message.reply_text(f"Hii {user.first_name or 'Saurabh'}! Avni yahan hai ✨ Batao aaj kya chal raha hai?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user = update.effective_user
    user_id = user.id
    first_name = user.first_name or ""
    user_text = update.message.text.strip()

    logger.info("---------- AVNI PIPELINE DEBUG ----------")
    logger.info("User ID: %s | Name: %s", user_id, first_name)
    logger.info("User Text: %s", user_text)

    ensure_user(user_id, first_name=first_name)

    # 1. Fact Extraction
    detected_facts = extract_ranked_facts(user_text)
    for key, val, f_type, score in detected_facts:
        save_fact(user_id, key, val, fact_type=f_type, importance=score, first_name=first_name)

    # 2. Build Context Directive
    contents, dynamic_system_prompt, active_mood = build_full_prompt_context(user_id, user_text)

    # 3. Save User Message
    save_message(user_id, "user", user_text, first_name=first_name)

    # 4. Generate Gemini Completion
    raw_response = await generate_reply_with_context(contents, dynamic_system_prompt)
    
    # 5. Post-Process via Humanizer Engine
    final_response = humanize_response(raw_response or "Hmm... lagta hai net slow hai.", mood=active_mood)

    # 6. Save Model Message & Reply
    save_message(user_id, "model", final_response, first_name=first_name)
    await update.message.reply_text(final_response)

def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN is missing! Exiting...")
        return

    threading.Thread(target=run_flask, daemon=True).start()

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Avni Bot Enterprise Humanizer Pipeline Engine READY...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()