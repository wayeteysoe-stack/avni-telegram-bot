import asyncio
import logging
import os
import random
import threading
import time
import urllib.request
from flask import Flask
from telegram import Update
from telegram.constants import ChatAction
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
@web_app.route("/health")
def health_check():
    return "Avni Bot Engine Active", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port, use_reloader=False)

def keep_alive_ping():
    """Background Anti-Sleep Pinger: Pings its own Render URL every 5 mins to prevent sleep."""
    # Render automatically sets RENDER_EXTERNAL_URL in environment
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    target_url = f"{render_url}/health" if render_url else "http://127.0.0.1:10000/health"
    
    while True:
        try:
            time.sleep(300) # Wait 5 minutes
            urllib.request.urlopen(target_url)
            logger.info(f"[KEEP-ALIVE] Successfully pinged {target_url} to block Render sleep.")
        except Exception as e:
            logger.warning(f"[KEEP-ALIVE] Ping failed: {e}")

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

    # 1. Fact Extractor
    detected_facts = extract_ranked_facts(user_text)
    for key, val, f_type, score in detected_facts:
        save_fact(user_id, key, val, fact_type=f_type, importance=score, first_name=first_name)

    # 2. Behavior & Context Builder
    contents, dynamic_system_prompt, active_mood = build_full_prompt_context(user_id, user_text)

    # 3. Save User Message
    save_message(user_id, "user", user_text, first_name=first_name)

    # 4. Typing Action Simulation
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    except Exception:
        pass

    # 5. Gemini Reply Generation
    raw_response = await generate_reply_with_context(contents, dynamic_system_prompt)
    
    # 6. Minimal Humanizer Post-Processing
    final_response = humanize_response(raw_response or "Hmm... thoda net issue lag raha hai.", mood=active_mood)

    # 7. Typing Delay (1.0s - 2.0s)
    await asyncio.sleep(random.uniform(1.0, 2.0))

    # 8. Save & Send Response
    save_message(user_id, "model", final_response, first_name=first_name)
    await update.message.reply_text(final_response)

def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN is missing! Exiting...")
        return

    # 1. Start Flask Web Engine in Background Thread
    threading.Thread(target=run_flask, daemon=True).start()

    # 2. Start Anti-Sleep Pinger Thread
    threading.Thread(target=keep_alive_ping, daemon=True).start()

    # Build Continuous Polling Telegram Application
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Avni Bot Persistent Polling Engine READY...")
    
    # Run Polling (stop_signals=() completely ignores Render's sleep signals)
    app.run_polling(
        drop_pending_updates=True,
        stop_signals=()
    )

if __name__ == "__main__":
    main()