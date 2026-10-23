# Local preview that behaves like GitHub Pages: /servicos -> servicos.html, /en/ -> en/index.html, 404.html for misses, gzip for text.
# python3 tools/serve.py [port]
import http.server, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def log_message(self, *a): pass
    def send_head(self):
        path = self.translate_path(self.path)
        if not os.path.exists(path) and os.path.exists(path + '.html'):
            self.path = self.path.split('?')[0].split('#')[0] + '.html'
        elif not os.path.exists(path) or (os.path.isdir(path) and not os.path.exists(os.path.join(path, 'index.html'))):
            body = open(os.path.join(ROOT, '404.html'), 'rb').read()
            self.send_response(404); self.send_header('Content-Type', 'text/html; charset=utf-8'); self.send_header('Content-Length', str(len(body))); self.end_headers()
            from io import BytesIO; return BytesIO(body)
        p2 = self.translate_path(self.path)
        if os.path.isdir(p2): p2 = os.path.join(p2, 'index.html')
        if 'gzip' in self.headers.get('Accept-Encoding', '') and p2.endswith(('.html', '.css', '.js', '.svg', '.json')) and os.path.isfile(p2):
            # GitHub Pages compresses text; do the same so local Lighthouse numbers are comparable
            import gzip
            from io import BytesIO
            body = gzip.compress(open(p2, 'rb').read(), 6)
            self.send_response(200); self.send_header('Content-Type', self.guess_type(p2)); self.send_header('Content-Encoding', 'gzip')
            self.send_header('Content-Length', str(len(body))); self.send_header('Cache-Control', 'max-age=600'); self.end_headers()
            return BytesIO(body)
        return super().send_head()
http.server.ThreadingHTTPServer(('127.0.0.1', int(sys.argv[1]) if len(sys.argv) > 1 else 4747), H).serve_forever()
