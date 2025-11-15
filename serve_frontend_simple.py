#!/usr/bin/env python3
"""
Simple alternative frontend server (Python 3 built-in)
"""
import os
import sys
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8000
FRONTEND_DIR = Path(__file__).parent / 'frontend'

class FrontendHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def main():
    if not FRONTEND_DIR.exists():
        print(f"ERROR: Frontend directory not found: {FRONTEND_DIR}")
        sys.exit(1)
    
    os.chdir(FRONTEND_DIR)
    
    server = HTTPServer(("", PORT), FrontendHandler)
    
    print("=" * 60)
    print("Frontend Server (Simple)")
    print("=" * 60)
    print(f"Serving at: http://localhost:{PORT}")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        webbrowser.open(f'http://localhost:{PORT}')
    except:
        pass
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped")
        server.shutdown()

if __name__ == '__main__':
    main()

