#!/usr/bin/env python3
"""
Simple HTTP server to serve the frontend
"""
import http.server
import socketserver
import os
import sys
import webbrowser
from pathlib import Path

PORT = 8004
FRONTEND_DIR = Path(__file__).parent / 'frontend'

# Check if frontend directory exists
if not FRONTEND_DIR.exists():
    print("=" * 60)
    print("ERROR: Frontend directory not found!")
    print("=" * 60)
    print(f"Looking for: {FRONTEND_DIR}")
    print(f"Current directory: {Path(__file__).parent}")
    print("\nPlease make sure you're running this script from the project root.")
    sys.exit(1)

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Python 3.7+ supports directory parameter
        try:
            super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)
        except TypeError:
            # Fallback for older Python versions
            super().__init__(*args, **kwargs)
    
    def translate_path(self, path):
        # Translate path to frontend directory for older Python versions
        path = super().translate_path(path)
        # Get relative path from current directory
        relpath = os.path.relpath(path, os.getcwd())
        # Return full path to frontend file
        return str(FRONTEND_DIR / relpath.lstrip('/'))
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Custom log format
        print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    print("=" * 60)
    print("Frontend Server")
    print("=" * 60)
    print(f"Frontend directory: {FRONTEND_DIR}")
    print(f"Serving at: http://localhost:{PORT}")
    print("=" * 60)
    
    # Change to frontend directory for serving files
    original_dir = os.getcwd()
    
    try:
        # Change to frontend directory
        os.chdir(FRONTEND_DIR)
        
        # Create server
        httpd = socketserver.TCPServer(("", PORT), MyHTTPRequestHandler)
        
        print("\n✓ Server started successfully!")
        print(f"✓ Open your browser at: http://localhost:{PORT}")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 60)
        print()
        
        # Open browser automatically
        try:
            import time
            time.sleep(1)  # Wait a bit for server to start
            webbrowser.open(f'http://localhost:{PORT}')
            print("✓ Browser opened automatically")
        except Exception as e:
            print(f"⚠ Could not open browser automatically: {e}")
            print(f"   Please open manually: http://localhost:{PORT}")
        
        print()
        
        # Serve forever
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("Stopping server...")
            print("=" * 60)
            httpd.shutdown()
            httpd.server_close()
            print("✓ Server stopped")
    except OSError as e:
        if "Address already in use" in str(e) or "Only one usage" in str(e):
            print(f"\n✗ ERROR: Port {PORT} is already in use!")
            print("\nSolutions:")
            print(f"1. Close the application using port {PORT}")
            print(f"2. Or change PORT in serve_frontend.py to another port (e.g., 8001)")
            print("\nTo find what's using the port:")
            print("  Windows: netstat -ano | findstr :8000")
            print("  Linux/Mac: lsof -i :8000")
        else:
            print(f"\n✗ ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Restore original directory
        os.chdir(original_dir)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        sys.exit(0)
