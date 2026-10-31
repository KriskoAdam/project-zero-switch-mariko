import importlib.util
import hashlib
import json
import subprocess
import struct
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "inspect_switch_artifact.py"
spec = importlib.util.spec_from_file_location("switch_artifact_inspector", SCRIPT)
inspector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspector)


def nso(flags=0, bad_offset=False, overlap=False, compressed_bad=False):
    b = bytearray(0x110)
    b[:4] = b"NSO0"
    struct.pack_into("<I", b, 0x0c, flags)
    desc = [(0x100, 0, 0x10), (0x108 if overlap else 0x108, 0x1000, 0x08), (0x108, 0x2000, 0x08)]
    # Use distinct valid payload locations unless the overlap case is requested.
    if not overlap:
        desc = [(0x100, 0, 8), (0x108, 0x1000, 4), (0x10c, 0x2000, 4)]
    for i, (off, addr, size) in enumerate(desc):
        struct.pack_into("<III", b, 0x10 + i * 0x10, off, addr, size)
        stored = 0x20 if compressed_bad and i == 0 else size
        struct.pack_into("<I", b, 0x60 + i * 4, stored)
    if bad_offset:
        struct.pack_into("<I", b, 0x10, 0xfffffff0)
    return bytes(b)


def nro(flags=0, bad_size=False, overlap=False):
    b = bytearray(0x120)
    b[0x10:0x14] = b"NRO0"
    struct.pack_into("<III", b, 0x14, 0, 0x80 if bad_size else len(b), flags)
    vals = [(0x80, 0x10), (0x90 if overlap else 0x90, 0x10), (0xa0, 0x10)]
    if not overlap:
        vals = [(0x80, 0x10), (0x90, 0x10), (0xa0, 0x10)]
    for i, pair in enumerate(vals):
        struct.pack_into("<II", b, 0x20 + i * 8, *pair)
    return bytes(b)


def kip(flags=0, bad_range=False, overlap=False):
    b = bytearray(0x110)
    b[:4] = b"KIP1"
    b[4:8] = b"test"
    b[0x1f] = flags
    vals = [(0x100, 8, 8), (0x104 if overlap else 0x108, 4, 4), (0x10c, 4, 4), (0x110, 0, 0)]
    if bad_range:
        vals[0] = (0x10f, 8, 8)
    for i, item in enumerate(vals):
        struct.pack_into("<III", b, 0x20 + i * 0x10, *item)
    return bytes(b)


def npdm():
    b = bytearray(0x80)
    b[:4] = b"META"
    b[0x20:0x24] = b"test"
    return bytes(b)


class SwitchArtifactTests(unittest.TestCase):
    def test_valid_minimal_formats(self):
        for data, expected in ((nso(), "NSO"), (nro(), "NRO"), (kip(), "KIP"), (npdm(), "NPDM")):
            with self.subTest(expected=expected):
                self.assertEqual(inspector.inspect_bytes(data)["format"], expected)

    def test_nso_valid_regions_and_compression_marked(self):
        r = inspector.inspect_nso(nso())
        self.assertEqual(r["segments"][0]["file_offset"], 0x100)
        self.assertTrue(r["segments"][0]["executable"])
        r = inspector.inspect_nso(nso(flags=1))
        self.assertFalse(r["segments"][0]["executable"])
        self.assertIn("unsupported", r["segments"][0]["compression"])

    def test_nso_rejects_truncation_bad_offset_and_overlap(self):
        for data in (b"NSO0", nso(bad_offset=True), nso(overlap=True)):
            with self.assertRaises(inspector.FormatError):
                inspector.inspect_nso(data)

    def test_nso_rejects_invalid_compression_metadata_and_unknown_flags(self):
        b = bytearray(nso())
        struct.pack_into("<I", b, 0x60, 0)
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_nso(bytes(b))
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_nso(nso(flags=0x100))

    def test_nro_header_and_range_checks(self):
        self.assertEqual(len(inspector.inspect_nro(nro())["segments"]), 3)
        for data in (nro()[:0x20], nro(bad_size=True), nro(flags=2)):
            with self.assertRaises(inspector.FormatError):
                inspector.inspect_nro(data)

    def test_nro_rejects_overlapping_regions(self):
        b = bytearray(nro())
        struct.pack_into("<II", b, 0x28, 0x88, 0x10)
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_nro(bytes(b))

    def test_kip_valid_and_compressed(self):
        self.assertEqual(inspector.inspect_kip(kip())["format"], "KIP")
        compressed = bytearray(kip(flags=1))
        self.assertEqual(inspector.inspect_kip(bytes(compressed))["segments"][0]["compression"], "unsupported BLZ")

    def test_kip_rejects_truncated_bad_range_and_overlap(self):
        for data in (b"KIP1", kip(bad_range=True)):
            with self.assertRaises(inspector.FormatError):
                inspector.inspect_kip(data)
        b = bytearray(kip())
        struct.pack_into("<I", b, 0x30, 0x104)
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_kip(bytes(b))

    def test_npdm_minimal_and_bad_inputs(self):
        self.assertEqual(inspector.inspect_npdm(npdm())["format"], "NPDM")
        for data in (b"META", b"NOPE" + b"\0" * 0x80):
            with self.assertRaises(inspector.FormatError):
                inspector.inspect_npdm(data)

    def test_npdm_section_bounds_overlap_and_magic(self):
        b = bytearray(npdm() + b"ACI0" + b"\0" * 12)
        struct.pack_into("<II", b, 0x70, 0x80, 0x10)
        self.assertEqual(inspector.inspect_npdm(bytes(b))["aci"]["size"], 0x10)
        struct.pack_into("<II", b, 0x70, 0xfffffff0, 0x100)
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_npdm(bytes(b))
        struct.pack_into("<II", b, 0x70, 0x80, 0x10)
        b[0x80:0x84] = b"BAD!"
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_npdm(bytes(b))

    def test_unrecognized_format_is_rejected(self):
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_bytes(b"not firmware")

    def test_cli_json_hash_and_synthetic_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.nso"
            path.write_bytes(nso())
            p = subprocess.run([sys.executable, str(SCRIPT), str(path), "--synthetic"],
                               text=True, capture_output=True, check=False)
            self.assertEqual(p.returncode, 0, p.stderr)
            result = json.loads(p.stdout)
            self.assertEqual(result["sha256"], hashlib.sha256(nso()).hexdigest())
            self.assertEqual(result["evidence_class"], "synthetic fixture")
            bad = subprocess.run([sys.executable, str(SCRIPT), str(path.with_name("missing"))],
                                 text=True, capture_output=True, check=False)
            self.assertEqual(bad.returncode, 2)


if __name__ == "__main__":
    unittest.main()
