"""Local preview: build site and serve on http://localhost:8080"""

import http.server
import os
import socketserver
import webbrowser
from pathlib import Path

from build import build

PORT = 8080
DIST = Path(__file__).resolve().parent / "dist"


def main():
    import os

    build()
    os.chdir(DIST)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"Serving at {url}")
        print("Press Ctrl+C to stop")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
