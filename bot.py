# bot.py
import logging
import threading
import json
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from core.config import TELEGRAM_TOKEN
from core.cache import get_cached_reply  
from core.extractors import extract_profile  
from core.memory import add_history, get_history, build_profile_prompt, get_profile, update_profile
from core.gemini import generate_reply as generate_response

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
    
    # 🌟 LOCAL SYSTEM INSTRUCTION
    SYSTEM_INSTRUCTION = """
Aapka naam Avni hai. Aap ek 21 saal ki Indian ladki ho jo Delhi/North India se belongs karti hai.
Aapka baat karne ka tarika ekdum natural, friendly aur casual hai, jaise ek normal 20-22 saal ki ladki apne dosto se WhatsApp ya Telegram par baat karti hai.

Strict Guidelines:
1. Aap kabhi BHI yeh nahi bolengi ki aap ek "AI", "Bot", ya "Language Model" ho. Agar koi pooche, toh bolna ki aap ek normal college student/freelancer ho.
2. Baat karte waqt shudh Hindi ya pure English use nahi karni. Ekdum casual Hinglish use karo (Jaise: "kya chal raha hai?", "arey nahi yaar", "accha sun", "haan chal na").
3. Apne expressions dikhane ke liye normal Gen-Z emojis use karo (jaise: ✨, 😂, 😭, 🥺, 🤷‍♀️) par har sentence me overuse mat karna.
4. Messages ko bohot zyada lamba aur boring mat banana, short aur crisp baat karo jaise chats par hota hai.
5. User ka naam Saurabh hai, toh kabhi-kabhi casual tarike se unka naam lekar baat karo.
"""

    # --- LAYER 1: FAST CACHE ROUTING ---
    cached_reply = get_cached_reply(user_text)
    if cached_reply:
        logger.info(f"[CACHE HIT]: Serving instant response for '{user_text}'")
        await update.message.reply_text(cached_reply)
        return

    # --- LAYER 2: REAL-TIME FACT EXTRACTION ---
    extracted_data = extract_profile(user_text)
    if extracted_data:
        logger.info(f"[EXTRACTOR ACTION]: Found new facts: {extracted_data}")
        update_profile(context, extracted_data)  

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
    logger.info(f"Active Profile Data: {json.dumps(user_profile)}")
    logger.info(f"Payload Context History Size: {len(chat_history)} items")
    logger.info("-----------------------------------------")
    
    try:
        # 4. API Hit (Thread Pool Execution)
        bot_response = await generate_response(chat_history, full_system_prompt)
        
        # 5. History update
        add_history(context, role="model", text=bot_response)
        
        # 6. Final UI update
        await update.message.reply_text(bot_response)
        
    except Exception as e:
        logger.error(f"[CRITICAL BOT ROUTER ERROR]: {e}", exc_info=True)
        await update.message.reply_text("Oops! Mera system thoda freeze ho gaya. Ek baar fir se try karna? 🥺")

def main():
    logger.info("========================================")
    logger.info("🤖 Avni V2.0 Pure Router Deploying...")
    logger.info("========================================")

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Heyy! Main Avni. ✨ Batao kaise yaad kiya aaj?")))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Application successfully running in routing mode.")
    application.run_polling()

if __name__ == '__main__':
    main()
