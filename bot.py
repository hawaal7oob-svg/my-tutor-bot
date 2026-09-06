import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)
import google.generativeai as genai

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = (
    "أنت معلم ورائد ذكاء اصطناعي تفاعلي ومحفز. "
    "واجبك هو تقديم الشرح والتوضيح بأسلوب سليم، متدرج، ومبسط للمستخدم."
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "أهلاً بك! أنا معلمك الذكي 🎓\n"
        "كيف يمكنني مساعدتك في دراستك أو أسئلتك اليوم؟"
    )
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    chat_id = update.effective_chat.id
    
    await context.bot.send_chat_action(
        chat_id=chat_id, 
        action="typing"
    )

    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text(
            "حدث خطأ أثناء معالجة الطلب، يرجى المحاولة لاحقاً."
        )

def main():
    if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
        raise ValueError(
            "يرجى التأكد من إضافة المفاتيح في Environment Variables!"
        )

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    )

    logging.info("البوت يعمل الآن بنجاح...")
    app.run_polling()

if __name__ == '__main__':
    main()
