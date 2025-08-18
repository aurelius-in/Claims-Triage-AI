#!/usr/bin/env python3
"""
Simple HTTP server to serve the Claims Triage AI demo
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8080

class DemoHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/simple-demo.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

def main():
    print("🚀 Starting Claims Triage AI Demo Server...")
    print(f"📁 Serving from: {os.getcwd()}")
    print(f"🌐 Demo URL: http://localhost:{PORT}")
    print("=" * 50)
    
    # Change to the directory containing the demo files
    os.chdir(Path(__file__).parent)
    
    with socketserver.TCPServer(("", PORT), DemoHandler) as httpd:
        print(f"✅ Server started on port {PORT}")
        print("🔗 Opening demo in browser...")
        
        # Open the demo in the default browser
        webbrowser.open(f'http://localhost:{PORT}')
        
        print("🛑 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Demo server stopped")

if __name__ == "__main__":
    main()
