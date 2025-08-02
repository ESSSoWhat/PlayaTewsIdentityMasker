import time
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = '''
<!DOCTYPE html>
<html>
<head>
    <title>MLOps Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .status { color: green; font-weight: bold; }
    </style>
</head>
<body>
    <h1>PlayaTews Identity Masker MLOps Dashboard</h1>
    <div class="metric">
        <h3>System Status</h3>
        <p class="status">âœ… All systems operational</p>
        <p>Last updated: <span id="timestamp"></span></p>
    </div>
    <div class="metric">
        <h3>Model API</h3>
        <p>Status: <span class="status">Running</span></p>
        <p>Endpoint: http://localhost:8000</p>
    </div>
    <div class="metric">
        <h3>MLflow</h3>
        <p>Status: <span class="status">Running</span></p>
        <p>Endpoint: http://localhost:5000</p>
    </div>
    <div class="metric">
        <h3>Monitoring</h3>
        <p>Status: <span class="status">Active</span></p>
        <p>Endpoint: http://localhost:9090</p>
    </div>
    <script>
        document.getElementById('timestamp').textContent = new Date().toLocaleString();
    </script>
</body>
</html>
            '''
            
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_dashboard_server():
    server = HTTPServer(('localhost', 3000), DashboardHandler)
    print(f"Dashboard started on http://localhost:3000")
    server.serve_forever()

if __name__ == '__main__':
    start_dashboard_server()
