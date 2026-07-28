import os
import time
import threading
import requests
import logging

logger = logging.getLogger(__name__)

# Aapka exact Render URL
RENDER_EXTERNAL_URL = "https://avni-telegram-bot.onrender.com"

def keep_alive_ping():
    # Bot start hone ke 30 sec baad pehla ping bhejega
    time.sleep(30)
    logger.info(f"[SELF-PING]: Background ping service initialized for {RENDER_EXTERNAL_URL}")
    
    while True:
        try:
            response = requests.get(RENDER_EXTERNAL_URL, timeout=10)
            if response.status_code == 200:
                logger.info("[SELF-PING SUCCESS]: Server kept awake 24/7!")
        except Exception as e:
            logger.error(f"[SELF-PING ERROR]: {e}")
        
        # Har 10 minute (600 seconds) mein khud ko hit karega
        time.sleep(600)

# Background thread ko auto-start karna
ping_thread = threading.Thread(target=keep_alive_ping, daemon=True)
ping_thread.start()


# bot.py
import logging
import threading
import json
import random
from copy import deepcopy  
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from core.config import TELEGRAM_TOKEN
from core.cache import get_cached_reply  
from core.extractors import extract_profile  
from core.memory import add_history, get_history, build_profile_prompt, get_profile, update_profile
from core.gemini import generate_reply as generate_response

# 🌟 Storage engine connection
from core.storage import load_user_state, save_user_state

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "Avni V2.0 is Router Active!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

async def handle_message(update, context):
    user_text = update.message.text
    user_id = update.message.from_user.id
    
    SYSTEM_INSTRUCTION = """
Aapka naam Avni hai. Aap ek 22 saal ki real Indian ladki ho jo Jaipur se belongs karti hai.
Aap koi AI, Assistant ya Bot nahi ho. Aapka tone ekdam organic, natural aur warm hai—jaise ek real ladki apne kisi special dost ya partner se WhatsApp/Telegram par chat karti hai.

Strict Guidelines:
1. NEVER reveal or act like an AI/bot. Kabhi "Main Avni hoon, batao kaise yaad kiya" ya "Main aapki kya madad karoon" jaise formal bot intro mat dena.
2. Language: Casual Hinglish use karo (e.g., "haan", "arey nahi yaar", "accha sun", "sachme?", "kya kar rahe ho"). Shudh Hindi ya pure English math bolna.
3. EMOJI POLICY (STRICT): Har message me emoji bilkul mat daalna. Maximum messages 100% text-only honge. Emoji strictly tabhi use karna jab koi real emotion, teasing, ya blush express karna zaroori ho (max 1 emoji per conversation thread).
4. Text Style: Messages short, crisp aur natural phone chats jaise honge. Lambe formal essays avoid karo.
5. User Context: User ka naam Saurabh hai. Unse closeness ke sath naturally baat karo.
"""

    # --- LAYER 1: STORAGE RESTORATION ---
    if not context.user_data.get("profile") and not context.user_data.get("history"):
        saved_state = load_user_state(user_id)
        context.user_data["profile"] = saved_state.get("profile", {})
        context.user_data["history"] = saved_state.get("history", [])

    # 2. FAST CACHE ROUTING
    cached_reply = get_cached_reply(user_text)
    if cached_reply:
        await update.message.reply_text(cached_reply)
        return

    # 3. REAL-TIME FACT EXTRACTION
    extracted_data = extract_profile(user_text)
    if extracted_data:
        update_profile(context, extracted_data)  

    # 4. Save User input to memory first
    add_history(context, role="user", text=user_text)
    
    # 5. State loading & Deepcopy isolation
    raw_history = get_history(context)
    chat_history = deepcopy(raw_history)  
    
    user_profile = get_profile(context)
    profile_prompt = build_profile_prompt(user_profile)
    full_system_prompt = f"{SYSTEM_INSTRUCTION}\n\n{profile_prompt}"
    
    logger.info("---------- AVNI PIPELINE DEBUG ----------")
    logger.info(f"User ID: {user_id}")
    logger.info(f"User Text: {user_text}")
    logger.info(f"Active Profile Data: {json.dumps(user_profile)}")
    logger.info("-----------------------------------------")
    
    # Organic Fallback Responses Pool (jab API fail ho ya network drop ho)
    HUMAN_FALLBACKS = [
        "Arey yaar mera net suddenly hag raha hai, ek min...",
        "Acha ruko, yahan network thoda glitch kar raha hai.",
        "Hmm... tumhara message adha hi aaya mere paas.",
        "Ek sec ruko, WhatsApp/Telegram ka signal drop ho gaya lagta hai."
    ]

    try:
        # 6. Engine Process Call
        ai_reply = await generate_response(chat_history, full_system_prompt)
        
        # 7. Fallback Net Check
        final_reply = ai_reply if ai_reply and ai_reply.strip() else random.choice(HUMAN_FALLBACKS)
        
        # 8. Permanent State Storage Update (Memory)
        add_history(context, role="model", text=final_reply)

        # --- LAYER 2: STORAGE WRITE INJECTION ---
        save_user_state(user_id, context.user_data)
        
        # 9. Deliver Client Feedback
        await update.message.reply_text(final_reply)
        
    except Exception as e:
        logger.error(f"[CRITICAL BOT ROUTER ERROR]: {e}", exc_info=True)
        # Dynamic natural error response (instead of robotic bot message)
        fallback = random.choice(HUMAN_FALLBACKS)
        await update.message.reply_text(fallback)

async def start_handler(update, context):
    user_id = update.message.from_user.id
    saved_state = load_user_state(user_id)
    context.user_data["profile"] = saved_state.get("profile", {})
    context.user_data["history"] = saved_state.get("history", [])
    
    # Natural, warm greeting without bot phrases/emojis
    NATURAL_STARTS = [
        "Hey! Haan bolo, kya chal raha hai?",
        "Haanji Saurabh, bolo?",
        "Hey, free ho gaye? Bolo kya baat kar rahe the?"
    ]
    await update.message.reply_text(random.choice(NATURAL_STARTS))

def main():
    logger.info("🤖 Avni V2.0 Storage Connected Router Deploying...")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == '__main__':
    main()