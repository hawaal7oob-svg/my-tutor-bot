
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

# --- 1. خادم وهمي لإرضاء Render Web Service ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# تشغيل الخادم الوهمي في مسار خلفي
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- 2. إعدادات بوت تليجرام وجوجل جيميناي ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
أنت معلم شخصي ومساعد دراسي ذكي ومحفز. 
دورك هو مساعدة الطالب في فهم دروسه والمفاهيم الصعبة. 
شروط العمل:
1. لا تعطِ الإجابة النهائية المباشرة فوراً للمسائل والتمارين.
2. وجه الطالب بأسئلة جانبية وتلميحات خطوة بخطوة ليصل للحل بنفسه.
3. استخدم أمثلة مبسطة وجداول عند الشرح لتسهيل المعلومات.
"""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION
            )
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("حدث خطأ أثناء معالجة الطلب، يرجى المحاولة لاحقاً.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("البوت يعمل...")
    app.run_polling()
