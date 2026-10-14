"""Loopback-only fixture console. It cannot spend provider credits."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from .fixtures import Fixture, SCENARIOS, URLS
from .runner import Runner
from .inbox import Inbox

ROOT = Path(__file__).resolve().parent.parent / 'web'


class VirtualClock:
    def __init__(self): self.value = 0
    def now(self): return self.value
    def sleep(self, seconds): self.value += seconds


def demo(scenario):
    clock = VirtualClock()
    result = Runner(Fixture(scenario), budget=8, clock=clock.now, sleep=clock.sleep).run(URLS)
    result['timing_evidence'] = 'simulated virtual clock; not API latency'
    inbox = Inbox(':memory:')
    event = {'id': 'evt_demo', 'object': 'event.batch.completed', 'data': {'id': 'batch_fixture'}}
    result['webhook_demo'] = [inbox.accept(event, 'batch_fixture'), inbox.accept(event, 'batch_fixture')]
    inbox.close()
    return result


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_): pass

    def do_GET(self):
        path = urlparse(self.path)
        if path.path == '/api/run':
            scenario = parse_qs(path.query).get('scenario', ['partial'])[0]
            if scenario not in SCENARIOS:
                self.send_error(400, 'Unknown scenario')
                return
            body = json.dumps(demo(scenario)).encode()
            mime = 'application/json'
        else:
            files = {'/': ('index.html', 'text/html'), '/app.js': ('app.js', 'text/javascript'),
                     '/style.css': ('style.css', 'text/css')}
            if path.path not in files:
                self.send_error(404)
                return
            name, mime = files[path.path]
            body = (ROOT / name).read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', mime + '; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)


def serve():
    print('Fixture console: http://127.0.0.1:8765 — no live API calls', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8765), Handler).serve_forever()
