#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 5173
os.chdir(os.path.dirname(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Frontend server running at http://localhost:{PORT}")
    httpd.serve_forever()
