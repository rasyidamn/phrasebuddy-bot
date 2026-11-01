import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters,
)
import time

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-2.5-flash-lite"  # cek nama model terbaru di AI Studio

SYSTEM = """You help an Indonesian learner say things in everyday American English.
The user may write in Indonesian or English.
Reply with 1 to 3 short, natural sentences that a native US speaker would
really say in daily life.
Rules:
- Use simple, common words. No heavy vocabulary, no formal or textbook style.
- Keep grammar simple and natural (contractions like "I'm", "don't" are fine).
- If the user wrote English, give a more natural everyday version.
- Output only the sentences. No explanations, no translation, no extra chat.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Kirim kalimat Indonesia atau Inggris, nanti aku buatkan kalimat Inggris sehari-hari."
    )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        t = time.perf_counter()
        resp = await client.aio.models.generate_content(
            model=MODEL,
            contents=update.message.text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM,
                temperature=0.3,
                max_output_tokens=150,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
        print(f"gemini: {time.perf_counter() - t:.1f}s")
        await update.message.reply_text(resp.text or "Coba kirim ulang ya.")
    except Exception as e:
        print("error:", e)
        await update.message.reply_text("Lagi error, coba lagi sebentar.")

def main():
    app = ApplicationBuilder().token(os.environ["TELEGRAM_TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()

if __name__ == "__main__":
    main()