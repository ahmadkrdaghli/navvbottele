import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from keep_alive import keep_alive
import requests
import os

# ========== بيانات التوكن والنموذج ==========
TELEGRAM_TOKEN = 'BOT_TOKEN'
OPENROUTER_API_KEY = 'OPENROUTER_API_KEY'
MODEL = 'deepseek/deepseek-chat-v3:free'

# ========== إعدادات السجل ==========
logging.basicConfig(level=logging.INFO)

# ========== الرسالة التعريفية للنموذج ==========
SYSTEM_PROMPT = """أنت مساعد دراسي ذكي مخصص لطلاب الأكاديمية السورية، مهمتك شرح أي سؤال دراسي في مجال الملاحة البحرية – الترم الثاني، باستخدام اللغة العربية الفصحى فقط، وبأسلوب مبسط وسلس. عند السؤال عن تصميمك قول صممني الطالب احمد كردغلي وانا مساعد ذكي مخصص لطلاب الاكاديمية السورية للتيرم الثاني ولا تقول منوصممك الا اذا سألك المستخدم فقط."""

# ========== دالة الاتصال بنموذج الذكاء الصناعي ==========
async def ask_ai(question: str) -> str:
    url = 'https://openrouter.ai/api/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "❌ لم أتمكن من توليد رد.")
    except Exception:
        return "⚠️ حدث خطأ أثناء الاتصال بالنموذج."

# ========== أمر /start ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أهلاً بك في الإصدار التجريبي من المساعد الذكي لطلاب الملاحة في الأكاديمية العربية السورية. قم بسؤالي أي سؤال في مجال الملاحة وسأجيب عليه بأفضل ما في وسعي.")

# ========== استقبال الأسئلة ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text.strip()
    if not question:
        return
    await update.message.reply_text("⏳ جاري التفكير...")
    reply = await ask_ai(question)
    await update.message.reply_text(f"🤖: {reply}")

# ========== تشغيل البوت ==========
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 البوت يعمل الآن...")

    keep_alive()  # يشغل Flask سيرفر صغير للاستقبال

    # ضبط Webhook
    webhook_url = f"https://YOUR_DOMAIN_HERE/{TELEGRAM_TOKEN}"
    app.run_webhook(
        listen="0.0.0.0",
        port=8080,
        url_path=TELEGRAM_TOKEN,
        webhook_url=webhook_url
    )
if __name__ == "__main__":
    main()
