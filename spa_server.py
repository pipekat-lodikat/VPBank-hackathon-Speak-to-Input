#!/usr/bin/env python3
"""
Simple HTTP Server with SPA (Single Page Application) routing
Serves index.html for all non-file routes
"""

import http.server
import socketserver
import os
from pathlib import Path

class SPAHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that serves index.html for SPA routes"""

    def do_GET(self):
        """Handle GET requests with SPA routing"""

        # Get the file path
        path = self.translate_path(self.path)

        # If path is a directory, try index.html
        if os.path.isdir(path):
            index_path = os.path.join(path, 'index.html')
            if os.path.exists(index_path):
                path = index_path

        # If file doesn't exist and is not a static asset, serve index.html (SPA routing)
        if not os.path.exists(path):
            # Check if it's requesting a static asset (has extension)
            if '.' not in os.path.basename(self.path):
                # It's a route, serve index.html
                self.path = '/index.html'

        # Serve the file
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def end_headers(self):
        """Add CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        http.server.SimpleHTTPRequestHandler.end_headers(self)

if __name__ == '__main__':
    PORT = 9999

    with socketserver.TCPServer(("", PORT), SPAHTTPRequestHandler) as httpd:
        print(f"🌐 SPA Server running at http://0.0.0.0:{PORT}")
        print(f"📂 Serving directory: {os.getcwd()}")
        print(f"✅ SPA routing enabled (all routes → index.html)")
        httpd.serve_forever()
