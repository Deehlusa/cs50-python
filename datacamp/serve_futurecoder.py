# -*- coding: utf-8 -*-
"""
Servidor local do futurecoder (fork PT-BR, self-host).

O futurecoder roda Python no navegador via Pyodide, que usa SharedArrayBuffer —
isso exige os headers COOP/COEP. Este servidor entrega o build em PT-BR
(.futurecoder-src/frontend/course) com esses headers.

Rodar:  python3 serve_futurecoder.py
Depois abra http://localhost:8001  (redireciona pra /course/).

Conteúdo: futurecoder (github.com/alexmojaki/futurecoder), licença MIT.
Build em português gerado com FUTURECODER_LANGUAGE=br.
"""

import http.server
import socketserver
from pathlib import Path

ROOT = Path(__file__).parent / ".futurecoder-src" / "frontend"
PORT = 8002  # origem limpa (o SW de precache ficou cravado em :8001)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def end_headers(self):
        # Necessário para SharedArrayBuffer (Pyodide: input(), Ctrl+C).
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Cross-Origin-Resource-Policy", "cross-origin")
        super().end_headers()

    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.send_response(302)
            self.send_header("Location", "/course/")
            self.end_headers()
            return
        # Neutraliza o service worker (precache) que servia build antigo no dev:
        # entrega um SW que se desregistra e limpa os caches.
        if self.path.split("?")[0].endswith("service-worker.js"):
            stub = (
                b"self.addEventListener('install',e=>self.skipWaiting());\n"
                b"self.addEventListener('activate',async e=>{\n"
                b"  const ks=await caches.keys(); await Promise.all(ks.map(k=>caches.delete(k)));\n"
                b"  await self.registration.unregister();\n"
                b"  const cs=await self.clients.matchAll(); cs.forEach(c=>c.navigate(c.url));\n"
                b"});\n"
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript")
            self.send_header("Content-Length", str(len(stub)))
            self.end_headers()
            self.wfile.write(stub)
            return
        super().do_GET()

    def log_message(self, *a):
        pass


def main():
    if not (ROOT / "course" / "index.html").exists():
        print("Build não encontrado. Rode o build do futurecoder primeiro.")
        print(f"Esperado: {ROOT / 'course' / 'index.html'}")
        return
    print(f"futurecoder (PT-BR) -> http://localhost:{PORT}")
    print("Ctrl+C para parar.")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nAté mais!")


if __name__ == "__main__":
    main()
