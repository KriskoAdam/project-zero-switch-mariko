#!/usr/bin/env python3
"""Small, local-only web-runtime test server for PROJECT ZERO Phase 12.

Uses only Python's standard library. It serves the adjacent web/ directory,
records bounded test JSON to results/phase12_web_results.jsonl, and provides
same-origin HTTP/XHR/fetch and a minimal WebSocket echo endpoint.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import socket
import struct
import subprocess
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"
LOG_PATH = ROOT / "results" / "phase12_web_results.jsonl"
MAX_BODY = 16_384


def private_interface_ip(interface: str) -> str:
    try:
        ip = subprocess.check_output(["/usr/sbin/ipconfig", "getifaddr", interface], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        details = subprocess.check_output(["/sbin/ifconfig", interface], text=True)
        match = re.search(r"\binet (\d+\.\d+\.\d+\.\d+)\b", details)
        ip = match.group(1) if match else ""
    parts = ip.split(".")
    if len(parts) != 4 or not parts[0].isdigit() or not parts[1].isdigit():
        raise RuntimeError(f"{interface} has no IPv4 address")
    first, second = int(parts[0]), int(parts[1])
    if not (first == 10 or (first == 172 and 16 <= second <= 31) or (first == 192 and second == 168)):
        raise RuntimeError(f"{interface} address is not a private IPv4 address: {ip}")
    return ip


def drop_sudo_privileges() -> None:
    """If started via sudo for a low port, return to the invoking user."""
    if os.geteuid() != 0:
        return
    uid = os.environ.get("SUDO_UID")
    gid = os.environ.get("SUDO_GID")
    if uid is None or gid is None:
        raise RuntimeError("Refusing to keep root privileges; start this through sudo from the user account.")
    os.setgroups([int(gid)])
    os.setgid(int(gid))
    os.setuid(int(uid))


class Handler(BaseHTTPRequestHandler):
    server_version = "ProjectZeroPhase12/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: object) -> None:
        # Keep a small access log alongside experiment results.
        line = "%s [%s] %s\n" % (self.client_address[0], time.strftime("%Y-%m-%dT%H:%M:%S%z"), fmt % args)
        with (ROOT / "results" / "phase12_access.log").open("a", encoding="utf-8") as f:
            f.write(line)

    def _send(self, status: int, body: bytes, content_type: str = "text/plain; charset=utf-8", *, head_only: bool = False) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self' ws://" + self.headers.get("Host", "invalid"))
        self.send_header("Connection", "close")
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/ws" and self.headers.get("Upgrade", "").lower() == "websocket":
            self._websocket_echo()
            return
        if path == "/api/ping":
            self._send(200, b'{"ok":true,"source":"phase12-local-server"}', "application/json; charset=utf-8")
            return
        relative = "index.html" if path in ("/", "") else path.lstrip("/")
        candidate = (WEB_ROOT / relative).resolve()
        if WEB_ROOT.resolve() not in candidate.parents or not candidate.is_file():
            self._send(404, b"Not found")
            return
        content_type = "text/html; charset=utf-8" if candidate.suffix == ".html" else "application/octet-stream"
        self._send(200, candidate.read_bytes(), content_type)

    def do_HEAD(self) -> None:
        """Return GET-equivalent headers without a response body."""
        path = urlparse(self.path).path
        if path == "/api/ping":
            self._send(200, b'{"ok":true,"source":"phase12-local-server"}', "application/json; charset=utf-8", head_only=True)
            return
        relative = "index.html" if path in ("/", "") else path.lstrip("/")
        candidate = (WEB_ROOT / relative).resolve()
        if WEB_ROOT.resolve() not in candidate.parents or not candidate.is_file():
            self._send(404, b"Not found", head_only=True)
            return
        content_type = "text/html; charset=utf-8" if candidate.suffix == ".html" else "application/octet-stream"
        self._send(200, candidate.read_bytes(), content_type, head_only=True)

    def do_POST(self) -> None:
        if urlparse(self.path).path not in ("/api/fetch", "/api/xhr", "/api/results"):
            self._send(404, b"Not found")
            return
        raw_length = self.headers.get("Content-Length", "0")
        try:
            length = int(raw_length)
        except ValueError:
            self._send(400, b"Bad Content-Length")
            return
        if length < 0 or length > MAX_BODY:
            self._send(413, b"Request too large")
            return
        raw = self.rfile.read(length)
        if self.path.startswith("/api/results"):
            try:
                record = json.loads(raw.decode("utf-8"))
                if not isinstance(record, dict):
                    raise ValueError("expected JSON object")
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
                self._send(400, b"Invalid JSON")
                return
            record = {"received_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "client_ip": self.client_address[0], "result": record}
            with LOG_PATH.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
            self._send(200, b'{"saved":true}', "application/json; charset=utf-8")
        else:
            # Echo only a fixed acknowledgement; never reflect arbitrary input.
            self._send(200, b'{"ok":true,"bytes_received":' + str(len(raw)).encode("ascii") + b'}', "application/json; charset=utf-8")

    def _websocket_echo(self) -> None:
        origin = self.headers.get("Origin", "")
        host = self.headers.get("Host", "")
        if origin != "http://" + host or self.headers.get("Sec-WebSocket-Version") != "13":
            self._send(403, b"Origin/version rejected")
            return
        key = self.headers.get("Sec-WebSocket-Key", "")
        if not key:
            self._send(400, b"Missing key")
            return
        accept = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")).digest()).decode("ascii")
        self.send_response(101, "Switching Protocols")
        self.send_header("Upgrade", "websocket")
        self.send_header("Connection", "Upgrade")
        self.send_header("Sec-WebSocket-Accept", accept)
        self.end_headers()
        self.connection.settimeout(5)
        try:
            head = self.rfile.read(2)
            if len(head) != 2:
                return
            opcode, length_byte = head[0] & 0x0F, head[1]
            length = length_byte & 0x7F
            if length == 126:
                ext = self.rfile.read(2)
                if len(ext) != 2: return
                length = struct.unpack(">H", ext)[0]
            elif length == 127:
                return
            masked = bool(length_byte & 0x80)
            if opcode != 1 or not masked or length > 1024:
                return
            mask = self.rfile.read(4)
            payload = self.rfile.read(length)
            if len(mask) != 4 or len(payload) != length:
                return
            decoded = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            if decoded != b"phase12-safe-echo":
                return
            self.connection.sendall(bytes([0x81, len(decoded)]) + decoded)
        except (OSError, socket.timeout):
            return


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interface", default="en0", help="macOS interface whose private IPv4 address will be used (default: en0)")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    host = private_interface_ip(args.interface)
    (ROOT / "results").mkdir(exist_ok=True)
    server = ThreadingHTTPServer((host, args.port), Handler)
    drop_sudo_privileges()
    shown_url = f"http://{host}/" if args.port == 80 else f"http://{host}:{args.port}/"
    print(f"Serving {shown_url} (Ctrl-C to stop)", flush=True)
    print(f"Result log: {LOG_PATH}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
