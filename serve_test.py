#!/usr/bin/env python3
"""
Simple HTTP server to serve the test HTML file
This avoids CORS issues when testing the frontend
"""
import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 3000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    # Change to the directory containing the HTML file
    os.chdir(Path(__file__).parent)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🚀 Test server running at http://localhost:{PORT}")
        print(f"📄 Open: http://localhost:{PORT}/test_frontend.html")
        print("🛑 Press Ctrl+C to stop")
        
        # Try to open the browser automatically
        try:
            webbrowser.open(f'http://localhost:{PORT}/test_frontend.html')
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")

if __name__ == "__main__":
    main()

