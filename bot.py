import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import google.generativeai as genai

# إعداد التسجيل لرصد أي أخطاء
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# جلب المفاتيح من بيئة العمل
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# إعداد مفتاح Gemini
genai.configure(api_key=GEMINI_API_KEY)

# التعليمات البرمجية لتوجيه أسلوب البوت
SYSTEM_INSTRUCTION = (
    "أنت معلم ورائد ذكاء اصطناعي تفاعلي ومحفز. "
    "واجبك هو تقديم الشرح والتوضيح بأسلوب سليم، متدرج، ومبسط للمستخدم."
)

# إنشاء الموديل
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "أهلاً بك! أنا معلمك الذكي 🎓\nكيف يمكنني مساعدتك في دراستك أو أسئلتك اليوم؟"
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Error while calling Gemini API: {e}")
        await update.message.reply_text("حدث خطأ أثناء معالجة الطلب، يرجى المحاولة لاحقاً.")

def main():
    if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
        raise ValueError("يرجى التأكد من إضافة TELEGRAM_BOT_TOKEN و GEMINI_API_KEY!")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    logging.info("البوت يعمل الآن بنجاح...")
    app.run_polling()

if __name__ == '__main__':
    main()
