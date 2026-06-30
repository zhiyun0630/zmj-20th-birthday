"""Local preview: build site and serve on a free local port."""

import http.server
import os
import socket
import socketserver
import webbrowser
from pathlib import Path

from build import build

PORT = 8080
DIST = Path(__file__).resolve().parent / "dist"
MAX_PORT_TRIES = 10


def find_free_port(start_port: int) -> int:
    for port in range(start_port, start_port + MAX_PORT_TRIES):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise OSError(f"No free port found in range {start_port}-{start_port + MAX_PORT_TRIES - 1}")


def main():
    build()
    os.chdir(DIST)
    handler = http.server.SimpleHTTPRequestHandler
    port = find_free_port(PORT)
    with socketserver.TCPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}"
        print(f"Serving at {url}")
        print("Press Ctrl+C to stop")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
