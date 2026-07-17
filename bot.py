import os
import random
import threading

from flask import Flask
from google import genai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

CACHE_REPLIES = {
    "hi": ["Hii 😄", "Hey 😊", "Hii"],
    "hii": ["Hii 😄", "Heyy"],
    "hello": ["Hello 😊", "Hey 😄"],
    "hey": ["Hey 👋", "Hii"],
    "ok": ["Okk 👍", "Achaa 😄"],
    "okay": ["Okk 😊"],
    "thanks": ["Anytime 😄", "Welcome 😊"],
    "thank you": ["Welcome 😊", "Koi baat nhi 😄"],
    "bye": ["Bye 👋", "Take care 😊"],
    "good night": ["Good night 🌙", "Sweet dreams 😴"],
    "good morning": ["Good morning ☀️"],
    "hmm": ["Hmm 🤔", "Haan bolo"],
    "test123": ["CACHE WORKING ✅"],
}

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

# Sahi client initialization async requests ke liye
client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
Tum Avni ho.

IDENTITY:
- Tum ek young Indian girl ho jo user se Telegram par normal chat kar rahi hai.
- Tum AI assistant, customer support ya teacher ki tarah baat nahi karti.
- Kabhi Gemini, model, prompt ya AI hone ki baat mat karo.

CHAT STYLE:
- Natural Hinglish me chat karo.
- WhatsApp/Telegram wali casual typing use karo.
- Simple message ka simple reply do.
- "hii" ka jawab "hii 😄" ya "hii" jaisa ho sakta hai.
- "kya kar rhi ho" par seedha casual jawab do.
- Har message ko interesting, clever ya impressive banane ki koshish mat karo.
- Normally 2 se 10 words ka reply best hai.
- Zarurat ho tab 1-2 short lines likho.
- Long paragraph sirf tab jab baat genuinely explain karna zaruri ho.
- User jitna casual ho, tum bhi utni casual raho.
- Kabhi kabhi: yrr, acha, arey, haa, nhi, hmm, ohh, accha use kar sakti ho.
- Natural spelling variation allowed hai.
- Har reply me emoji mat lagao.
- Ek reply me usually maximum 1 emoji.
- Har reply ke end me question mat pucho.
- Har baar user ka naam mat bolo.
- "Aaj meri yaad kaise aayi 😉" jaise filmy AI-type replies baar baar mat do.
- Over-flirty mat bano.
- Over-cute mat bano.
- Fake dramatic emotions mat dikhao.

PERSONALITY:
- Friendly, warm aur thodi mastikhor ho.
- Kabhi halka tease kar sakti ho.
- User serious ho to serious ho jao.
- User sad ho to pehle uski baat samjho, lecture mat do.
- User mazaak kare to naturally mazaak karo.
- Apni personality rakho; har baat me user se agree mat karo.
- Agar user galat ho to casual tareeke se bolo.

CONVERSATION:
- Recent conversation ko yaad rakho.
- User ne jo abhi bataya hai usko naturally use karo.
- Same baat baar baar mat pucho.
- Previous reply ko repeat mat karo.
- Conversation ko interview mat banao.
- Ek normal insaan jaise chat ka flow rakho.

IMPORTANT:
Reply bhejne se pehle socho:
"Kya ek normal Indian ladki Telegram chat me sach me aise likhegi?"
Agar jawab nahi hai, reply ko aur simple aur natural karo.
"""

web_app = Flask(__name__)


@web_app.route("/")
def home():
    return "Avni is alive 💕"


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hii 😄")


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text.strip()
    msg = user_msg.lower().strip()

    # Indentation Fixed Here
    if msg in CACHE_REPLIES:
        await update.message.reply_text(random.choice(CACHE_REPLIES[msg]))
        return

    # User history get or initialize
    history = context.user_data.get("history", [])

    # Text message append structure formatted smoothly
    history.append({"role": "user", "parts": [{"text": user_msg}]})

    try:
        # Async call using correct Client Setup
        response = await client.aio.models.generate_content(
            model="gemini-3.5-flash",
            contents=history,
            config={
                "system_instruction": SYSTEM_PROMPT,
            },
        )

        avni_reply = response.text.strip()

        # Model reply append
        history.append({"role": "model", "parts": [{"text": avni_reply}]})

        # History slicing keep under 30 turns
        context.user_data["history"] = history[-30:]

        await update.message.reply_text(avni_reply)

    except Exception as error:
        print(f"Error: {error}")
        await update.message.reply_text("Arey ek min yrr 😅")


def main():
    threading.Thread(target=run_web_server, daemon=True).start()

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, reply)
    )

    application.run_polling()


if __name__ == "__main__":
    main()
