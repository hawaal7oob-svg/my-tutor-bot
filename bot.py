import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from google import genai

# إعداد التسجيل لرصد أي أخطاء
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# جلب المفاتيح من بيئة العمل (Environment Variables)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# تهيئة عميل جوجل جيمني
client = genai.Client(api_key=GEMINI_API_KEY)

# التعليمات البرمجية لتوجيه أسلوب البوت (System Instruction)
SYSTEM_INSTRUCTION = (
    "أنت معلم ورائد ذكاء اصطناعي تفاعلي ومحفز. "
    "واجبك هو تقديم الشرح والتوضيح بأسلوب سليم، متدرج، ومبسط للمستخدم."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الرد عند تشغيل البوت لأول مرة"""
    welcome_text = "أهلاً بك! أنا معلمك الذكي 🎓\nكيف يمكنني مساعدتك في دراستك أو أسئلتك اليوم؟"
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة كافة الرسائل النصية وإرسالها إلى Gemini API"""
    user_text = update.message.text

    # إظهار حالة (جاري الكتابة...) للمستخدم
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # إرسال الطلب إلى موديل gemini-1.5-flash المستقر
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=user_text,
            config={
                "system_instruction": SYSTEM_INSTRUCTION
            }
        )
        
        # إرسال الإجابة للمستخدم
        await update.message.reply_text(response.text)

    except Exception as e:
        logging.error(f"Error while calling Gemini API: {e}")
        await update.message.reply_text("حدث خطأ أثناء معالجة الطلب، يرجى المحاولة لاحقاً.")

def main():
    """تشغيل البوت"""
    if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
        raise ValueError("يرجى التأكد من إضافة TELEGRAM_BOT_TOKEN و GEMINI_API_KEY في Environment Variables!")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # إضافة المعالجات (Handlers)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # بدء الاستماع للرسائل
    logging.info("البوت يعمل الآن بنجاح...")
    app.run_polling()

if __name__ == '__main__':
    main()
