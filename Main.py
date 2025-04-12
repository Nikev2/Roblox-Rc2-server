from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import threading
import time
import urllib.request

def get_local_ip():
    # Use a dummy connection to an external IP
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            # Doesn't actually connect to Google, just used to get your local IP
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
    return ip

HOST = get_local_ip()  # Accessible from LAN
PORT = 8765            # Use any open port
original_result = "false"
result = original_result  # This will be updated via POST

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global result
        global original_result
        print(f"🔗 GET from {self.client_address}")
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(result.encode())
        result = original_result # Revert to original after GET

    def do_POST(self):
        global result
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode()
        result = post_data  # Update the result
        print(f"📨 POST from {self.client_address} set result to: {result}")

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Result updated")

def keep_alive():
    def ping():
        while True:
            try:
                print("🔁 Sending keep-alive ping...")
                urllib.request.urlopen(f"http://{HOST}:{PORT}", timeout=10)
            except Exception as e:
                print(f"⚠️ Keep-alive ping failed: {e}")
            time.sleep(300)  # Ping every 5 minutes
    thread = threading.Thread(target=ping, daemon=True)
    thread.start()

def run():
    keep_alive()
    server = HTTPServer((HOST, PORT), SimpleHandler)
    print(f"🚀 HTTP server running on http://{HOST}:{PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run()
