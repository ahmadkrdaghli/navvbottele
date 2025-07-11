import os
import logging
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# إعدادات تسجيل الدخول
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "deepseek/deepseek-chat-v3:free"

# إعدادات الـ system prompt
SYSTEM_PROMPT = """أنت مساعد دراسي ذكي مخصص لطلاب الأكاديمية السورية، مهمتك شرح أي سؤال دراسي في مجال الملاحة البحرية – الترم الثاني، باستخدام اللغة العربية الفصحى فقط، وبأسلوب مبسط وسلس. عند السؤال عن تصميمك قول صممني الطالب احمد كردغلي."""

# إعداد البوت
app = Flask(__name__)
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()
bot = Bot(BOT_TOKEN)

# دالة الاتصال بـ OpenRouter
async def ask_ai(question: str) -> str:
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": question}
                ]
            }
        )
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "❌ لم أتمكن من توليد رد.")
    except Exception:
        return "⚠️ حدث خطأ أثناء الاتصال بالنموذج."

# أوامر البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أهلاً بك في الإصدار التجريبي من المساعد الذكي لطلاب الملاحة في الأكاديمية السورية.")

async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text.strip()
    await update.message.reply_text("⏳ جاري التفكير...")
    reply = await ask_ai(question)
    await update.message.reply_text(f"🤖: {reply}")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))

# Webhook Endpoint
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    telegram_app.update_queue.put_nowait(update)
    return "OK"

# تشغيل التطبيق
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8080))
    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"https://navvbottele-production-7c6d.up.railway.app/{BOT_TOKEN}"  # <-- غيّرها
    )
#بغبغ
