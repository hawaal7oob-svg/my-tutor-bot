import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# سيرفر وهمي يدعم طلبات GET و HEAD ليتوافق مع Render تماماً
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"OK")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# تشغيل السيرفر في الخلفية
Thread(target=run_health_check_server, daemon=True).start()

# ==========================================
# ضع كود البوت الخاص بك هنا
# ==========================================
