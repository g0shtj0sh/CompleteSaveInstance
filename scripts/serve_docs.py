"""Preview the built documentation using its production GitHub Pages base path."""

from __future__ import annotations

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "/CompleteSaveInstance/"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, directory=str(ROOT / "build"), **kwargs)

    def send_header(self, keyword: str, value: str) -> None:
        if keyword.lower() == "location" and value.startswith("/") and not value.startswith(BASE):
            value = BASE + value.lstrip("/")
        super().send_header(keyword, value)

    def do_GET(self) -> None:
        if self.path == "/":
            self.send_response(302)
            self.send_header("Location", BASE)
            self.end_headers()
            return
        if not self.path.startswith(BASE):
            self.send_error(404)
            return
        self.path = "/" + self.path[len(BASE):]
        super().do_GET()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=4173)
    args = parser.parse_args()
    if not (ROOT / "build/index.html").is_file():
        raise SystemExit("Run npm run docs:build first.")
    print(f"Documentation preview: http://127.0.0.1:{args.port}{BASE}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
