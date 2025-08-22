#!/usr/bin/env python3

import http.server
import socketserver
import threading
import time

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html_content = f'''
            <html>
                <head><title>Basic HTTP Server Test</title></head>
                <body>
                    <h1>HTTP Server is Working!</h1>
                    <p>If you can see this, basic HTTP serving works.</p>
                    <p>Server time: {time.ctime()}</p>
                </body>
            </html>
            '''
            self.wfile.write(html_content.encode())
        elif self.path == '/test':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "message": "Basic server working"}')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')

if __name__ == "__main__":
    PORT = 8005
    print(f"🚀 Starting basic HTTP server on port {PORT}")
    print(f"📱 Access at: http://127.0.0.1:{PORT}")
    print(f"📱 Or try: http://localhost:{PORT}")
    
    try:
        with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
            print(f"✅ Server started successfully on port {PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Server failed to start: {e}")