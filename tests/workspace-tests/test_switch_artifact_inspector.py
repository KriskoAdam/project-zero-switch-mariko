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
    b[0x80:0x100] = b"\xff" * 0x80
    return bytes(b)


def npdm():
    b = bytearray(0x80)
    b[:4] = b"META"
    b[0x20:0x24] = b"test"
    return bytes(b)


def npdm_with_sac_and_caps():
    aci = bytearray(0x6c)
    aci[:4] = b"ACI0"
    struct.pack_into("<Q", aci, 0x10, 0x010000000000100A)
    struct.pack_into("<II", aci, 0x20, 0x40, 0x20)  # minimal documented FAC header area
    struct.pack_into("<II", aci, 0x28, 0x60, 4)
    struct.pack_into("<II", aci, 0x30, 0x64, 8)
    struct.pack_into("<I", aci, 0x40, 1)  # FAC format version
    aci[0x60:0x64] = bytes((0x82,)) + b"svc"
    # ThreadInfo descriptor (type 3): priorities 2..40, cores 0..3.
    thread_field = 2 | (40 << 6) | (0 << 12) | (3 << 18)
    struct.pack_into("<II", aci, 0x64, (thread_field << 4) | 0x7, 0xffffffff)
    out = bytearray(0x80 + len(aci))
    out[:0x80] = npdm()
    struct.pack_into("<II", out, 0x70, 0x80, len(aci))
    out[0x80:] = aci
    return bytes(out)


def npdm_with_acid_sac_and_caps():
    acid = bytearray(0x26c)
    acid[0x200:0x204] = b"ACID"
    struct.pack_into("<I", acid, 0x204, len(acid) - 0x100)
    struct.pack_into("<I", acid, 0x20c, 1)
    struct.pack_into("<QQ", acid, 0x210, 0x0100000000001000, 0x0100000000001fff)
    struct.pack_into("<II", acid, 0x220, 0x240, 0x20)
    struct.pack_into("<II", acid, 0x228, 0x260, 4)
    struct.pack_into("<II", acid, 0x230, 0x264, 8)
    struct.pack_into("<I", acid, 0x240, 1)
    acid[0x260:0x264] = bytes((0x02,)) + b"svc"
    thread_field = 1 | (20 << 6) | (0 << 12) | (2 << 18)
    struct.pack_into("<II", acid, 0x264, (thread_field << 4) | 0x7, 0xffffffff)
    out = bytearray(0x80 + len(acid))
    out[:0x80] = npdm()
    struct.pack_into("<II", out, 0x78, 0x80, len(acid))
    out[0x80:] = acid
    return bytes(out)


def nro_with_assets():
    base = bytearray(nro())
    aset = bytearray(0x403c)
    aset[:4] = b"ASET"
    struct.pack_into("<I", aset, 4, 0)
    struct.pack_into("<QQ", aset, 8, 0x38, 4)
    struct.pack_into("<QQ", aset, 0x18, 0x3c, 0x4000)
    aset[0x38:0x40] = b"ICNC"
    aset[0x3c:0x403c] = b"\0" * 0x4000
    base.extend(aset)
    return bytes(base)


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
        zbic_mode = inspector.inspect_nso(nso(flags=0x80))
        self.assertEqual([x["compression"] for x in zbic_mode["segments"]], ["none", "none", "none"])
        zbic_text = inspector.inspect_nso(nso(flags=0x81))
        self.assertIn("ZBIC", zbic_text["segments"][0]["compression"])

    def test_nso_rejects_truncation_bad_offset_and_overlap(self):
        for data in (b"NSO0", nso(bad_offset=True), nso(overlap=True)):
            with self.assertRaises(inspector.FormatError):
                inspector.inspect_nso(data)

    def test_fixed_headers_cannot_be_segment_payloads(self):
        b = bytearray(nso())
        struct.pack_into("<I", b, 0x10, 0x80)
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_nso(bytes(b))
        b = bytearray(kip())
        struct.pack_into("<I", b, 0x20, 0xf0)
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_kip(bytes(b))
        b = bytearray(nro())
        struct.pack_into("<I", b, 0x3c, 0x40)
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_nro(bytes(b))

    def test_nso_rejects_invalid_compression_metadata_and_unknown_flags(self):
        b = bytearray(nso())
        struct.pack_into("<I", b, 0x60, 0)
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_nso(bytes(b))
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_nso(nso(flags=0x100))

    def test_nso_module_name_rodata_metadata_and_hash_flags(self):
        b = bytearray(nso(flags=(1 << 3) | (1 << 6)))
        b.extend(b"\0" * 4)
        struct.pack_into("<II", b, 0x88, 0, 4)
        struct.pack_into("<II", b, 0x90, 1, 3)
        struct.pack_into("<II", b, 0x98, 0, 0)
        struct.pack_into("<I", b, 0x1c, 0x110)
        struct.pack_into("<I", b, 0x2c, 4)
        b[0x110:0x114] = b"name"
        result = inspector.inspect_nso(bytes(b))
        self.assertTrue(result["execute_only_memory"])
        self.assertTrue(result["segment_hashes"]["text"]["enabled"])
        self.assertEqual(result["module_name"]["file_offset"], 0x110)
        self.assertEqual(result["rodata_metadata"]["embedded"]["size"], 4)
        struct.pack_into("<II", b, 0x88, 0xfffffff0, 0x40)
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_nso(bytes(b))

    def test_nro_header_and_range_checks(self):
        self.assertEqual(len(inspector.inspect_nro(nro())["segments"]), 3)
        for data in (nro()[:0x20], nro(bad_size=True)):
            with self.assertRaises(inspector.FormatError):
                inspector.inspect_nro(data)
        compressed = inspector.inspect_nro(nro(flags=2))
        self.assertIn("compressed", compressed["segments"][0]["compression"])
        self.assertFalse(compressed["segments"][0]["executable"])

    def test_nro_rejects_overlapping_regions(self):
        b = bytearray(nro())
        struct.pack_into("<II", b, 0x28, 0x88, 0x10)
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_nro(bytes(b))

    def test_nro_assets_ranges_and_additional_header(self):
        result = inspector.inspect_nro(nro_with_assets())
        self.assertEqual(result["assets"]["sections"]["icon"]["size"], 4)
        self.assertEqual(result["assets"]["sections"]["nacp"]["size"], 0x4000)
        b = bytearray(nro_with_assets())
        struct.pack_into("<Q", b, len(nro()) + 8, 0xfffffff0)
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_nro(bytes(b))
        b = bytearray(nro_with_assets())
        struct.pack_into("<Q", b, len(nro()) + 0x20, 4)
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_nro(bytes(b))
        b = bytearray(nro())
        struct.pack_into("<I", b, 0x3c, len(nro()))
        b.extend(b"NRA0" + b"\0" * 0x7c)
        result = inspector.inspect_nro(bytes(b))
        self.assertEqual(result["additional_header"]["magic"], "NRA0")

    def test_kip_valid_and_compressed(self):
        self.assertEqual(inspector.inspect_kip(kip())["format"], "KIP")
        compressed = bytearray(kip(flags=1))
        self.assertEqual(inspector.inspect_kip(bytes(compressed))["segments"][0]["compression"], "unsupported BLZ")

    def test_kip_kernel_capability_descriptors(self):
        b = bytearray(kip())
        thread_field = 5 | (32 << 6) | (1 << 12) | (4 << 18)
        struct.pack_into("<I", b, 0x80, (thread_field << 4) | 7)
        caps = inspector.inspect_kip(bytes(b))["kernel_capabilities"]
        self.assertEqual(caps[0]["type"], "thread_info")
        self.assertEqual(caps[0]["thread_info"]["lowest_priority"], 5)
        self.assertEqual(caps[0]["thread_info"]["max_core"], 4)

    def test_kernel_capability_descriptor_families(self):
        kinds = {3: "thread_info", 4: "enable_system_calls", 6: "memory_map", 7: "io_memory_map",
                 10: "memory_region_map", 11: "enable_interrupts", 13: "misc_params",
                 14: "kernel_version", 15: "handle_table_size", 16: "misc_flags"}
        words = []
        for type_id in kinds:
            field = 1
            raw = (field << (type_id + 1)) | ((1 << type_id) - 1)
            words.append(raw)
        parsed = inspector._inspect_kernel_capabilities(struct.pack("<" + "I" * len(words), *words), "test")
        self.assertEqual([item["type"] for item in parsed], list(kinds.values()))
        with self.assertRaises(inspector.FormatError):
            inspector._inspect_kernel_capabilities(b"\0\0\0\0", "test")
        with self.assertRaises(inspector.FormatError):
            inspector._inspect_kernel_capabilities(b"\0", "test")

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
        b = bytearray(npdm() + b"ACI0" + b"\0" * 0x34)
        struct.pack_into("<II", b, 0x70, 0x80, 0x38)
        self.assertEqual(inspector.inspect_npdm(bytes(b))["aci"]["size"], 0x38)
        struct.pack_into("<II", b, 0x70, 0xfffffff0, 0x100)
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_npdm(bytes(b))
        struct.pack_into("<II", b, 0x70, 0x80, 0x38)
        b[0x80:0x84] = b"BAD!"
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_npdm(bytes(b))

    def test_npdm_service_access_control_and_kernel_capabilities(self):
        result = inspector.inspect_npdm(npdm_with_sac_and_caps())
        self.assertEqual(result["aci_details"]["program_id"], "0x010000000000100a")
        sac = result["aci_details"]["sections"]["sac"]["services"]
        self.assertEqual(sac, [{"name": "svc", "is_server": True, "raw_descriptor": 0x82}])
        cap = result["aci_details"]["sections"]["kernel_capabilities"]["entries"][0]
        self.assertEqual(cap["type"], "thread_info")
        self.assertEqual(cap["thread_info"]["highest_priority"], 40)

    def test_npdm_acid_uses_full_rsa2048_prefix_and_parses_access_lists(self):
        result = inspector.inspect_npdm(npdm_with_acid_sac_and_caps())
        acid = result["acid"]["details"]
        self.assertEqual(acid["program_id_min"], "0x0100000000001000")
        self.assertEqual(acid["sac"]["services"][0]["name"], "svc")
        self.assertFalse(result["acid"]["signature_verified"])
        b = bytearray(npdm_with_acid_sac_and_caps())
        b[0x80 + 0x100:0x80 + 0x104] = b"ACID"
        b[0x80 + 0x200:0x80 + 0x204] = b"BAD!"
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_npdm(bytes(b))
        b = bytearray(npdm_with_acid_sac_and_caps())
        struct.pack_into("<I", b, 0x80 + 0x204, 0x20)
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_npdm(bytes(b))

    def test_npdm_rejects_bad_sac_and_nested_overlap(self):
        b = bytearray(npdm_with_sac_and_caps())
        b[0x80 + 0x60] = 0x87
        with self.assertRaises(inspector.FormatError):
            inspector.inspect_npdm(bytes(b))
        b = bytearray(npdm_with_sac_and_caps())
        struct.pack_into("<II", b, 0x80 + 0x30, 0x60, 4)
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
