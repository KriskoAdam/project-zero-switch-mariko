#!/usr/bin/env python3
"""Passive macOS USB identity/interface snapshot; writes no device data."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import subprocess

SERIAL = re.compile(r"Switch V2\d+")


def run_ioreg(args: list[str]) -> str:
    p = subprocess.run(["/usr/sbin/ioreg", *args], capture_output=True, text=True, check=True)
    return p.stdout


def prop_int(text: str, name: str) -> int | None:
    m = re.search(rf'"{re.escape(name)}"\s*=\s*(\d+)', text)
    return int(m.group(1)) if m else None


def node_block(text: str, heading: str) -> str | None:
    start = text.find(heading)
    if start < 0:
        return None
    end = text.find("\n+-o ", start + len(heading))
    return text[start:] if end < 0 else text[start:end]


def capture(label: str, outdir: Path) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    dev = run_ioreg(["-r", "-c", "IOUSBHostDevice", "-l", "-w0"])
    iface = run_ioreg(["-r", "-c", "IOUSBHostInterface", "-l", "-w0"])
    dev = SERIAL.sub("[REDACTED_SERIAL]", dev)
    iface = SERIAL.sub("[REDACTED_SERIAL]", iface)
    (outdir / f"{label}_usb_devices.txt").write_text(dev)
    (outdir / f"{label}_usb_interfaces.txt").write_text(iface)

    target = node_block(dev, "Nintendo Switch@")
    interface = node_block(iface, "MTP@")
    if interface is None:
        interface = node_block(iface, "IOUSBHostInterface@0")
    obj = {
        "captured_at": datetime.now().astimezone().isoformat(timespec="milliseconds"),
        "label": label,
        "commands": [
            "/usr/sbin/ioreg -r -c IOUSBHostDevice -l -w0",
            "/usr/sbin/ioreg -r -c IOUSBHostInterface -l -w0",
        ],
        "device_found": target is not None,
        "device": None,
        "interface": None,
        "raw_files": [f"{label}_usb_devices.txt", f"{label}_usb_interfaces.txt"],
    }
    if target:
        obj["device"] = {
            "vid": f"0x{(prop_int(target, 'idVendor') or 0):04x}",
            "pid": f"0x{(prop_int(target, 'idProduct') or 0):04x}",
            "manufacturer": "Nintendo" if "USB Vendor Name\" = \"Nintendo" in target else None,
            "product": "Nintendo Switch" if "USB Product Name\" = \"Nintendo Switch" in target else None,
        }
    if interface:
        obj["interface"] = {
            "name": "MTP" if "MTP@" in interface else "IOUSBHostInterface",
            "class": prop_int(interface, "bInterfaceClass"),
            "subclass": prop_int(interface, "bInterfaceSubClass"),
            "protocol": prop_int(interface, "bInterfaceProtocol"),
            "interface_number": prop_int(interface, "bInterfaceNumber"),
            "endpoint_count": prop_int(interface, "bNumEndpoints"),
        }
    return obj


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("label")
    ap.add_argument("outdir", type=Path)
    ap.add_argument("--json", type=Path, required=True)
    args = ap.parse_args()
    result = capture(args.label, args.outdir)
    args.json.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
