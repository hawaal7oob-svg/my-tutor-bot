import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ------------------- الإعدادات العامة -------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
PORT = int(os.environ.get("PORT", 10000))  # Render يمرر المنفذ تلقائيًا

# ------------------- خادم بسيط لتلبية Health Check -------------------
class HealthCheckHandler(BaseHTTPRequestHandler):
    def _respond(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def do_GET(self):
        self._respond()

    def do_HEAD(self):
        self._respond()

    # لتفادي طباعة كل طلب في الـ logs
    def log_message(self, format, *args):
        return


def run_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthCheckHandler)
    logger.info(f"Health check server running on port {PORT}")
    server.serve_forever()


# ------------------- أوامر البوت -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً! البوت يعمل بنجاح ✅")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)


def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("لم يتم ضبط متغير البيئة TELEGRAM_TOKEN")

    # 1) تشغيل خادم الـ Health Check في Thread منفصل (daemon)
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    # 2) بناء تطبيق البوت
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # 3) تشغيل الـ Polling في الـ Main Thread (هذا ما يُبقي العملية حية)
    logger.info("Starting bot polling...")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
