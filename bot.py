import logging
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from core.config import TELEGRAM_TOKEN
from core.memory import add_history, get_history, build_profile_prompt, get_profile
from core.gemini import generate_reply as generate_response

# --- Avni Ka Realistic Ladki Wala Persona ---
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
    app.run(host='0.0.0.0', port=10000)
# -------------------------------------

async def handle_message(update, context):
    user_text = update.message.text
    
    # 1. User ka message history me add karo
    add_history(context, role="user", text=user_text)
    
    # 2. History aur Profile fetch karo
    chat_history = get_history(context)
    user_profile = get_profile(context)
    
    # 3. System prompt ke sath profile prompt taiyar karo
    profile_prompt = build_profile_prompt(user_profile)
    full_system_prompt = f"{SYSTEM_INSTRUCTION}\n\n{profile_prompt}"
    
    try:
        # 4. Gemini se response le kar aao
        bot_response = await generate_response(chat_history, full_system_prompt)
        
        # 5. Bot ka response history me add karo
        add_history(context, role="model", text=bot_response)
        
        # 6. User ko reply bhejo
        await update.message.reply_text(bot_response)
        
    except Exception as e:
        logger.error(f"Error in generating response: {e}")
        await update.message.reply_text("API abhi response nahi de rahi hai, kripya thoda rukiye. 😅")

def main():
    logger.info("========================================")
    logger.info("🤖 Avni V2.0 Modular System Booting...")
    logger.info("========================================")

    # 1. Flask server start karo
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # 2. Telegram Application Build karo
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Handlers attach karo - Ekdam natural welcome message
    application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("Heyy! Main Avni. ✨ Batao kaise yaad kiya aaj?")))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Bot ko polling mode me start karo
    logger.info("Application started")
    application.run_polling()

if __name__ == '__main__':
    main()
