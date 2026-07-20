# check_models.py
import os
from google import genai
from dotenv import load_dotenv

# .env se key load karega, koi secret expose nahi hoga
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

try:
    client = genai.Client(api_key=api_key)
    print("Checking available models for your API Key...")
    for model in client.models.list():
        print(f"-> {model.name}")
except Exception as e:
    print(f"⚠️ Error occurred: {e}")