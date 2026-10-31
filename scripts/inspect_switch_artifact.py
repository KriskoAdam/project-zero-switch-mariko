#!/usr/bin/env python3
"""Read-only structural inspection for Switch NSO/NRO/KIP/NPDM and ELF inputs.

This intentionally validates a documented subset. It never executes or extracts files.
Compressed Switch segments are identified but not decompressed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path


class FormatError(ValueError):
    pass


def u32(b: bytes, off: int) -> int:
    if off < 0 or off + 4 > len(b):
        raise FormatError(f"truncated u32 at 0x{off:x}")
    return struct.unpack_from("<I", b, off)[0]


def check_range(start: int, size: int, limit: int, label: str) -> None:
    if start < 0 or size < 0 or start > limit or size > limit - start:
        raise FormatError(f"{label} range [0x{start:x}, +0x{size:x}) exceeds 0x{limit:x}")


def no_overlap(ranges: list[tuple[int, int, str]]) -> None:
    ordered = sorted((a, a + n, name) for a, n, name in ranges if n)
    for left, right in zip(ordered, ordered[1:]):
        if right[0] < left[1]:
            raise FormatError(f"overlapping ranges: {left[2]} and {right[2]}")


def inspect_nso(b: bytes) -> dict:
    if len(b) < 0x100 or b[:4] != b"NSO0":
        raise FormatError("NSO requires NSO0 and complete 0x100-byte header")
    flags = u32(b, 0x0c)
    if flags & ~0xff:
        raise FormatError("NSO contains unknown flag bits")
    segs, file_ranges, memory_ranges = [], [], []
    for idx, name in enumerate(("text", "rodata", "data")):
        p = 0x10 + idx * 0x10
        off, addr, mem_size = struct.unpack_from("<III", b, p)
        file_size = u32(b, 0x60 + idx * 4)
        compressed = bool(flags & (1 << idx)) or bool(flags & (1 << 7))
        if not file_size and mem_size:
            raise FormatError(f"NSO {name} has memory data but zero stored size")
        check_range(off, file_size, len(b), f"NSO {name} file")
        if mem_size and addr > 0xffffffff - mem_size:
            raise FormatError(f"NSO {name} memory range overflows 32-bit address space")
        file_ranges.append((off, file_size, name))
        memory_ranges.append((addr, mem_size, name))
        segs.append({"name": name, "file_offset": off, "file_size": file_size,
                     "memory_offset": addr, "memory_size": mem_size,
                     "compression": "unsupported (LZ4/Zbic)" if compressed else "none",
                     "executable": name == "text" and not compressed,
                     "mapping_status": "verified header fields; payload not decompressed" if compressed else "header-mapped"})
    no_overlap(file_ranges)
    no_overlap(memory_ranges)
    return {"format": "NSO", "validation": "valid-subset", "version": u32(b, 4),
            "flags": flags, "build_id_hex": b[0x40:0x60].hex(),
            "bss_size": u32(b, 0x3c), "segments": segs,
            "unsupported": ["LZ4/Zbic decompression", "full loader semantics", "hash verification"]}


def inspect_nro(b: bytes) -> dict:
    if len(b) < 0x80 or b[0x10:0x14] != b"NRO0":
        raise FormatError("NRO requires NRO0 at 0x10 and complete 0x80-byte header")
    version, declared_size, flags = struct.unpack_from("<III", b, 0x14)
    if declared_size < 0x80 or declared_size > len(b):
        raise FormatError("NRO declared image size is outside file bounds")
    if flags & ~3:
        raise FormatError("NRO contains unknown flag bits")
    if flags & 2:
        raise FormatError("compressed NRO segment layout is not supported")
    segs, ranges = [], []
    for name, aoff in (("text", 0x20), ("rodata", 0x28), ("data", 0x30)):
        mem_off, size = struct.unpack_from("<II", b, aoff)
        # NRO load-image segment file offsets follow their memory offsets in the flat image.
        check_range(mem_off, size, declared_size, f"NRO {name}")
        ranges.append((mem_off, size, name))
        segs.append({"name": name, "file_offset": mem_off, "file_size": size,
                     "memory_offset": mem_off, "memory_size": size,
                     "executable": name == "text", "mapping_status": "NRO flat-image mapping"})
    no_overlap(ranges)
    return {"format": "NRO", "validation": "valid-subset", "version": version,
            "declared_image_size": declared_size, "flags": flags,
            "build_id_hex": b[0x40:0x60].hex(), "bss_size": u32(b, 0x38),
            "segments": segs, "additional_header_offset": u32(b, 0x3c),
            "unsupported": ["compressed NRO", "ASET asset parsing", "full loader semantics"]}


def inspect_kip(b: bytes) -> dict:
    if len(b) < 0x100 or b[:4] != b"KIP1":
        raise FormatError("KIP requires KIP1 and complete 0x100-byte header")
    flags = b[0x1f]
    if flags & ~0x7f:
        raise FormatError("KIP contains unknown flag bits")
    segs, ranges = [], []
    for idx, name in enumerate(("text", "rodata", "data", "bss")):
        p = 0x20 + idx * 0x10
        off, mem_size, stored_size = struct.unpack_from("<III", b, p)
        compressed = idx < 3 and bool(flags & (1 << idx))
        # A zero stored size is explicitly allowed for BSS; other nonzero data is bounded.
        check_range(off, stored_size, len(b), f"KIP {name} payload")
        if idx < 3 and not compressed and stored_size > mem_size:
            raise FormatError(f"KIP {name} stored size exceeds memory size")
        ranges.append((off, stored_size, name))
        segs.append({"name": name, "file_offset": off, "file_size": stored_size,
                     "memory_size": mem_size, "compression": "unsupported BLZ" if compressed else "none",
                     "executable": idx == 0 and not compressed,
                     "mapping_status": "header-mapped" if not compressed else "payload not decoded"})
    no_overlap(ranges)
    return {"format": "KIP", "validation": "valid-subset", "name": b[4:0x10].split(b"\0", 1)[0].decode("ascii", "replace"),
            "program_id": f"0x{struct.unpack_from('<Q', b, 0x10)[0]:016x}", "version": u32(b, 0x18),
            "flags": flags, "segments": segs,
            "unsupported": ["BLZ decompression", "kernel capability decoding"]}


def inspect_npdm(b: bytes) -> dict:
    if len(b) < 0x80 or b[:4] != b"META":
        raise FormatError("NPDM requires META and complete 0x80-byte header")
    aci_off, aci_size, acid_off, acid_size = struct.unpack_from("<IIII", b, 0x70)
    sections = []
    for name, off, size in (("ACI", aci_off, aci_size), ("ACID", acid_off, acid_size)):
        if size:
            check_range(off, size, len(b), f"NPDM {name}")
            sections.append((off, size, name))
            expected = b"ACI0" if name == "ACI" else b"\0\0\0\0"  # ACID begins with signature.
            if name == "ACI" and b[off:off+4] != expected:
                raise FormatError("NPDM ACI section lacks ACI0 magic")
            if name == "ACID":
                if size < 0x208 or b[off+0x100:off+0x104] != b"ACID":
                    raise FormatError("NPDM ACID section lacks supported signature/header prefix")
                acid_size_field = u32(b, off + 0x104)
                if acid_size_field < 0x38 or acid_size_field > size - 0x100:
                    raise FormatError("NPDM ACID declared body size is invalid")
    no_overlap(sections)
    name = b[0x20:0x30].split(b"\0", 1)[0].decode("ascii", "replace")
    return {"format": "NPDM", "validation": "valid-subset", "name": name,
            "flags0": b[0x0c], "flags1": b[0x0d], "version": u32(b, 0x18),
            "stack_size": u32(b, 0x1c), "aci": {"offset": aci_off, "size": aci_size},
            "acid": {"offset": acid_off, "size": acid_size, "signature_verified": False},
            "executable_regions": [],
            "unsupported": ["RSA signature verification", "FAC/SAC/KC decoding", "loader policy semantics"]}


def inspect_elf(b: bytes) -> dict:
    try:
        from elftools.elf.elffile import ELFFile
        import io
        elf = ELFFile(io.BytesIO(b))
        segs = []
        for seg in elf.iter_segments():
            if seg.header.p_type == "PT_LOAD":
                executable = bool(seg.header.p_flags & 1)
                segs.append({"name": "PT_LOAD", "file_offset": int(seg.header.p_offset),
                             "file_size": int(seg.header.p_filesz), "memory_offset": int(seg.header.p_vaddr),
                             "memory_size": int(seg.header.p_memsz), "executable": executable,
                             "mapping_status": "ELF program header"})
        return {"format": "ELF", "validation": "pyelftools-parsed", "architecture": elf.get_machine_arch(),
                "class_bits": 64 if elf.elfclass == 64 else 32, "endianness": "little" if elf.little_endian else "big",
                "segments": segs, "unsupported": []}
    except ImportError:
        raise FormatError("ELF inspection requires pyelftools")
    except Exception as e:
        raise FormatError(f"ELF parse failed: {e}") from e


def inspect_bytes(b: bytes) -> dict:
    if b.startswith(b"NSO0"):
        return inspect_nso(b)
    if len(b) >= 0x14 and b[0x10:0x14] == b"NRO0":
        return inspect_nro(b)
    if b.startswith(b"KIP1"):
        return inspect_kip(b)
    if b.startswith(b"META"):
        return inspect_npdm(b)
    if b.startswith(b"\x7fELF"):
        return inspect_elf(b)
    raise FormatError("unrecognized supported format")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("--disassemble", action="store_true", help="disassemble mapped AArch64 executable regions when supported")
    ap.add_argument("--synthetic", action="store_true", help="label input as a synthetic fixture")
    args = ap.parse_args()
    try:
        raw = args.input.read_bytes()
        result = {"input": str(args.input), "size": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                  "evidence_class": "synthetic fixture" if args.synthetic else "input file; provenance not established"}
        result.update(inspect_bytes(raw))
        result["verified_fields"] = ["file size", "SHA-256", "fields covered by this parser subset"]
        result["heuristic_results"] = []
        if args.disassemble:
            result["disassembly"] = {"status": "not attempted", "note": "only supported by the separate ELF symbol-aware tool; Switch segment mapping is metadata-only"}
            if result["format"] == "ELF" and result.get("architecture") == "AArch64":
                from inspect_arm64_binary import analyze
                result["disassembly"] = analyze(args.input, max_instructions=400, max_bytes=0x4000)
        payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(payload, encoding="utf-8")
        else:
            sys.stdout.write(payload)
        return 0
    except (OSError, FormatError) as e:
        payload = json.dumps({"input": str(args.input), "validation": "rejected", "error": str(e)}, indent=2) + "\n"
        if args.output:
            args.output.write_text(payload, encoding="utf-8")
        else:
            sys.stdout.write(payload)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
