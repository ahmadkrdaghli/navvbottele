import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# ========== بيانات التوكن والنموذج ==========
TELEGRAM_TOKEN = '7956062539:AAEOGife_prAUmXZ_DvWkRULl4c3ARz32h4'
OPENROUTER_API_KEY = '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'
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
    app.run_polling()

if __name__ == "__main__":
    main()
