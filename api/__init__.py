"""
api — USM HTTP introspection API (stdlib only, zero deps).
Runs on port 8766.

GET /info
GET /namespaces
GET /namespaces/<ns>/state
GET /namespaces/<ns>/history?n=50
GET /namespaces/<ns>/replay?since=<unix_ts>
GET /stats
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dataclasses import asdict

def _json(data) -> bytes:
    return json.dumps(data, default=str).encode()

class USMAPIHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass   # silence stdlib access log; USMLogger handles it

    def send_json(self, data, status=200):
        body = _json(data)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        from registry.namespaces import namespaces
        from registry.publishers import publishers
        from registry.viewers    import viewers
        from storage.memory      import mem
        from storage.replay      import replay

        parsed = urlparse(self.path)
        path   = parsed.path.rstrip('/')
        qs     = parse_qs(parsed.query)

        # GET /info
        if path == '/info':
            return self.send_json({
                "server":   "Universal State Mirror",
                "version":  1,
                "ts":       time.time(),
                "ws_port":  8765,
                "api_port": 8766,
            })

        # GET /namespaces
        if path == '/namespaces':
            return self.send_json({"namespaces": namespaces.all()})

        # GET /stats
        if path == '/stats':
            return self.send_json({
                "namespaces": namespaces.stats(),
                "publishers": len(publishers.all()),
                "viewers":    len(viewers.all()),
            })

        # GET /namespaces/<ns>/state|history|replay
        if path.startswith('/namespaces/'):
            rest = path[len('/namespaces/'):]
            for suffix in ('/state', '/history', '/replay'):
                if rest.endswith(suffix):
                    ns = rest[:-len(suffix)]
                    if suffix == '/state':
                        frame = mem.read(ns)
                        if not frame:
                            return self.send_json({"error": f"No live state for '{ns}'"}, 404)
                        return self.send_json(asdict(frame))
                    elif suffix == '/history':
                        n = int(qs.get('n', ['50'])[0])
                        frames = replay.last_n(ns, n)
                        return self.send_json({
                            "namespace": ns, "count": len(frames),
                            "frames": [asdict(f) for f in frames]
                        })
                    elif suffix == '/replay':
                        since = float(qs.get('since', [str(time.time() - 60)])[0])
                        frames = replay.since(ns, since)
                        return self.send_json({
                            "namespace": ns, "since": since,
                            "count": len(frames),
                            "frames": [asdict(f) for f in frames]
                        })

        self.send_json({"error": "not found"}, 404)

def run_api(host: str = "0.0.0.0", port: int = 8766):
    server = HTTPServer((host, port), USMAPIHandler)
    server.serve_forever()
