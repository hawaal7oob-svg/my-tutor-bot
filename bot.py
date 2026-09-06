import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# 1. كود السيرفر الوهمي (لجعل Render يرى أن البوت يستجيب كـ Web Service مجانية)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# تشغيل السيرفر الوهمي في الخلفية
Thread(target=run_health_check_server, daemon=True).start()


# ==========================================
# 2. هنا يبدأ كود بوت تيليجرام الخاص بك كاملاً
# ==========================================
import logging
from telegram import Update
# بقية استيراداتك وكود البوت الخاص بك هنا...
