# avni-bot/bot.py
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from core.config import TELEGRAM_TOKEN
from core.gemini import generate_reply
from core.cache import get_cached_reply
from core.prompt import SYSTEM_PROMPT
from core.extractors import extract_profile
from core.memory import (
    get_profile,
    update_profile,
    get_history,
    add_history,
    build_profile_prompt,
)

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("Avni")

# Initializing Telegram Engine
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

async def send_message(update: Update, text: str):
    if update.message:
        await update.message.reply_text(text)

def clean_message(text: str) -> str:
    return text.strip() if text else ""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(update, "Hii 😄")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling update:", exc_info=context.error)

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_message = clean_message(update.message.text)
    if not user_message:
        return

    # 1. Quick Cache Filter
    cached_reply = get_cached_reply(user_message)
    if cached_reply:
        await send_message(update, cached_reply)
        return

    # 2. Dynamic Memory Extraction
    profile_data = extract_profile(user_message)
    if profile_data:
        update_profile(context, profile_data)

    profile = get_profile(context)
    profile_prompt = build_profile_prompt(profile)

    # Injecting instructions separately into System Scope to prevent hallucination
    DYNAMIC_SYSTEM_PROMPT = f"{SYSTEM_PROMPT}\n{profile_prompt}".strip()

    # Load recent state
    history = get_history(context)

    # 3. Create temporary deep list to request generation safely
    from copy import deepcopy
    api_payload = deepcopy(history)
    api_payload.append({
        "role": "user",
        "parts": [{"text": user_message}]
    })

    # 4. Engine Process Call
    ai_reply = await generate_reply(api_payload, DYNAMIC_SYSTEM_PROMPT)
    
    # Fallback to prevent Telegram API crash if string is empty/None
    final_reply = ai_reply or "Hmm..."

    # 5. Permanent State Storage Update
    add_history(context, "user", user_message)
    add_history(context, "model", final_reply)

    # 6. Deliver Client Feedback
    await send_message(update, final_reply)
# Register Core Signal Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
app.add_error_handler(error_handler)

def main():
    logger.info("========================================")
    logger.info("🤖 Avni V2.0 Modular System Booting...")
    logger.info("========================================")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()