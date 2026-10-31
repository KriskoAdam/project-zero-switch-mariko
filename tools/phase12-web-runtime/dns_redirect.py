#!/usr/bin/env python3
"""Temporary, narrow DNS forwarder for the Phase 12 captive-portal test.

It binds only to a private IPv4 address on the Mac, redirects the two publicly
documented Switch connection-test names to that Mac, and forwards other DNS
queries to the first resolver listed in /etc/resolv.conf. It writes no query
log. Binding UDP/53 normally requires administrator privileges on macOS.
"""
from __future__ import annotations

import argparse
import ipaddress
import os
import re
import socket
import struct
import subprocess
from pathlib import Path

TARGETS = {"conntest.nintendowifi.net", "ctest.cdn.nintendo.net"}
MAX_DNS_PACKET = 4096


def interface_ipv4(interface: str) -> str:
    output = subprocess.check_output(["/sbin/ifconfig", interface], text=True)
    match = re.search(r"\binet (\d+\.\d+\.\d+\.\d+)\b", output)
    if not match:
        raise RuntimeError(f"No IPv4 address on {interface}")
    ip = match.group(1)
    if not ipaddress.IPv4Address(ip).is_private:
        raise RuntimeError(f"Refusing non-private bind address: {ip}")
    return ip


def configured_upstream() -> str:
    for line in Path("/etc/resolv.conf").read_text(encoding="utf-8").splitlines():
        match = re.match(r"\s*nameserver\s+(\d+\.\d+\.\d+\.\d+)\s*$", line)
        if match and ipaddress.IPv4Address(match.group(1)).is_private:
            return match.group(1)
    raise RuntimeError("No private IPv4 DNS forwarder found in /etc/resolv.conf; refusing to guess an upstream.")


def question(packet: bytes) -> tuple[str, int, int, int] | None:
    if len(packet) < 17:
        return None
    qdcount = struct.unpack_from(">H", packet, 4)[0]
    if qdcount != 1:
        return None
    labels: list[str] = []
    pos = 12
    while pos < len(packet):
        size = packet[pos]
        pos += 1
        if size == 0:
            break
        if size & 0xC0 or size > 63 or pos + size > len(packet):
            return None
        try:
            labels.append(packet[pos:pos + size].decode("ascii"))
        except UnicodeDecodeError:
            return None
        pos += size
    else:
        return None
    if pos + 4 > len(packet):
        return None
    qtype, qclass = struct.unpack_from(">HH", packet, pos)
    qend = pos + 4
    return ".".join(labels).lower(), qtype, qclass, qend


def local_answer(packet: bytes, qend: int, ip: str, include_a: bool) -> bytes:
    request_flags = struct.unpack_from(">H", packet, 2)[0]
    response_flags = 0x8000 | 0x0400 | 0x0080 | (request_flags & 0x0100)  # QR, AA, RA, preserve RD
    answer_count = 1 if include_a else 0
    header = packet[:2] + struct.pack(">HHHHH", response_flags, 1, answer_count, 0, 0)
    question_bytes = packet[12:qend]
    if not include_a:
        return header + question_bytes
    answer = b"\xc0\x0c" + struct.pack(">HHIH", 1, 1, 0, 4) + socket.inet_aton(ip)
    return header + question_bytes + answer


def drop_sudo_privileges() -> None:
    if os.geteuid() != 0:
        return
    uid = os.environ.get("SUDO_UID")
    gid = os.environ.get("SUDO_GID")
    if uid is None or gid is None:
        raise RuntimeError("Refusing to keep root privileges; start this through sudo from the user account.")
    os.setgroups([int(gid)])
    os.setgid(int(gid))
    os.setuid(int(uid))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interface", default="en0")
    parser.add_argument("--bind-ip", help="Private Mac IPv4; normally discovered from --interface")
    parser.add_argument("--upstream", help="Private upstream DNS IP; defaults to /etc/resolv.conf")
    args = parser.parse_args()
    bind_ip = args.bind_ip or interface_ipv4(args.interface)
    if not ipaddress.IPv4Address(bind_ip).is_private:
        raise SystemExit("Refusing a non-private bind address")
    upstream = args.upstream or configured_upstream()
    if not ipaddress.IPv4Address(upstream).is_private:
        raise SystemExit("Refusing a non-private upstream resolver")
    if os.geteuid() != 0:
        raise SystemExit("UDP port 53 requires administrator privileges on this Mac; no service was started.")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((bind_ip, 53))
    drop_sudo_privileges()
    print(f"DNS test listener: {bind_ip}:53; forwarding to private resolver {upstream}", flush=True)
    print("Redirecting only: " + ", ".join(sorted(TARGETS)), flush=True)
    print("Ctrl-C stops this temporary process. No DNS settings are changed by this script.", flush=True)
    try:
        while True:
            packet, client = sock.recvfrom(MAX_DNS_PACKET)
            parsed = question(packet)
            if parsed and parsed[0] in TARGETS and parsed[2] == 1 and parsed[1] in (1, 28):
                name, qtype, _qclass, qend = parsed
                print(f"local test lookup: {name} from {client[0]}", flush=True)
                response = local_answer(packet, qend, bind_ip, qtype == 1)
                sock.sendto(response, client)
                continue
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as forwarder:
                    forwarder.settimeout(3)
                    forwarder.sendto(packet, (upstream, 53))
                    response, _ = forwarder.recvfrom(MAX_DNS_PACKET)
                sock.sendto(response, client)
            except (OSError, TimeoutError):
                # Forwarding failed. Drop the query instead of fabricating a reply.
                continue
    except KeyboardInterrupt:
        print("Stopping temporary DNS listener.", flush=True)
    finally:
        sock.close()


if __name__ == "__main__":
    main()
