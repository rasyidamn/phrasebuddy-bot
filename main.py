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
MODEL = "gemini-3.5-flash-lite"  # cek nama model terbaru di AI Studio

SYSTEM = """You help an Indonesian learner say things in everyday American English.
The user may write in Indonesian or English.

Reply with exactly ONE short sentence. Output only that sentence.

Rules:
- Default to plain, common words. If a simple word works, use it ("tired" is fine).
- Casual idioms or slang are OK only if almost every English learner would
  understand them (e.g. "I'm wiped out", "I'm starving", "gonna").
- Avoid rare, regional, or trendy slang (e.g. "beat", "running on empty",
  "whip up", "bright and early").
- Stay close to the original meaning. Don't add or change details.
- Contractions are fine.
- If the user wrote English, rewrite it to sound more natural and everyday.
- No explanations, no translation, no extra chat.

Examples:
Aku besok pagi harus bangun gasik -> I have to get up really early tomorrow.
Aku habis ini mau masak mie -> I'm gonna make some noodles after this.
Aku capek banget hari ini -> I'm so tired today.
Aku lapar banget -> I'm starving.
Aku capek banget, pengen langsung tidur -> I'm wiped out, I just wanna go to bed.
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
                max_output_tokens=150,
                thinking_config=types.ThinkingConfig(
                    thinking_level=types.ThinkingLevel.MINIMAL
                ),
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
