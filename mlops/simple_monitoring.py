import time
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class MonitoringHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': (datetime.now() - self.server.start_time).total_seconds(),
                'requests_total': getattr(self.server, 'request_count', 0),
                'memory_usage_mb': 128.5,
                'cpu_usage_percent': 15.2
            }
            
            self.server.request_count = getattr(self.server, 'request_count', 0) + 1
            self.wfile.write(json.dumps(metrics).encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_monitoring_server():
    server = HTTPServer(('localhost', 9090), MonitoringHandler)
    server.start_time = datetime.now()
    server.request_count = 0
    print(f"Monitoring server started on http://localhost:9090")
    server.serve_forever()

if __name__ == '__main__':
    start_monitoring_server()
