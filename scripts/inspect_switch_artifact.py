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
    module_name_offset, module_name_size = u32(b, 0x1c), u32(b, 0x2c)
    if module_name_size:
        if module_name_offset < 0x100:
            raise FormatError("NSO module name overlaps fixed header")
        check_range(module_name_offset, module_name_size, len(b), "NSO module name")
        file_ranges.append((module_name_offset, module_name_size, "module_name"))
    for idx, name in enumerate(("text", "rodata", "data")):
        p = 0x10 + idx * 0x10
        off, addr, mem_size = struct.unpack_from("<III", b, p)
        file_size = u32(b, 0x60 + idx * 4)
        if file_size and off < 0x100:
            raise FormatError(f"NSO {name} payload overlaps fixed header")
        compressed = bool(flags & (1 << idx))
        compression = ("ZBIC (decoder unsupported)" if flags & (1 << 7) else "LZ4 (decoder unsupported)") if compressed else "none"
        if not file_size and mem_size:
            raise FormatError(f"NSO {name} has memory data but zero stored size")
        check_range(off, file_size, len(b), f"NSO {name} file")
        if mem_size and addr > 0xffffffff - mem_size:
            raise FormatError(f"NSO {name} memory range overflows 32-bit address space")
        file_ranges.append((off, file_size, name))
        memory_ranges.append((addr, mem_size, name))
        segs.append({"name": name, "file_offset": off, "file_size": file_size,
                     "memory_offset": addr, "memory_size": mem_size,
                     "compression": compression,
                     "executable": name == "text" and not compressed,
                     "mapping_status": "verified header fields; payload not decompressed" if compressed else "header-mapped"})
    no_overlap(file_ranges)
    no_overlap(memory_ranges)
    ro_size = u32(b, 0x28)
    ro_meta = {}
    for key, off_field, size_field in (("embedded", 0x88, 0x8c), ("dynamic_strings", 0x90, 0x94), ("dynamic_symbols", 0x98, 0x9c)):
        offset, size = u32(b, off_field), u32(b, size_field)
        if size:
            check_range(offset, size, ro_size, f"NSO {key} metadata within .rodata")
        ro_meta[key] = {"rodata_offset": offset, "size": size}
    hashes = {name: {"enabled": bool(flags & (1 << (3 + idx))),
                     "sha256_hex": b[0xa0 + idx * 0x20:0xc0 + idx * 0x20].hex()}
              for idx, name in enumerate(("text", "rodata", "data"))}
    return {"format": "NSO", "validation": "valid-subset", "version": u32(b, 4),
            "flags": flags, "build_id_hex": b[0x40:0x60].hex(),
            "module_name": {"file_offset": module_name_offset, "size": module_name_size},
            "execute_only_memory": bool(flags & (1 << 6)),
            "bss_size": u32(b, 0x3c), "segments": segs,
            "rodata_metadata": ro_meta, "segment_hashes": hashes,
            "unsupported": ["LZ4/Zbic decompression", "full loader semantics", "hash verification"]}


def inspect_nro(b: bytes) -> dict:
    if len(b) < 0x80 or b[0x10:0x14] != b"NRO0":
        raise FormatError("NRO requires NRO0 at 0x10 and complete 0x80-byte header")
    version, declared_size, flags = struct.unpack_from("<III", b, 0x14)
    if declared_size < 0x80 or declared_size > len(b):
        raise FormatError("NRO declared image size is outside file bounds")
    if flags & ~3:
        raise FormatError("NRO contains unknown flag bits")
    compressed = bool(flags & 2)
    segs, ranges = [], []
    for name, aoff in (("text", 0x20), ("rodata", 0x28), ("data", 0x30)):
        mem_off, size = struct.unpack_from("<II", b, aoff)
        # NRO load-image segment file offsets follow their memory offsets in the flat image.
        if not compressed:
            check_range(mem_off, size, declared_size, f"NRO {name}")
        ranges.append((mem_off, size, name))
        segs.append({"name": name, "file_offset": None if compressed else mem_off,
                     "file_size": None if compressed else size,
                     "memory_offset": mem_off, "memory_size": size,
                     "executable": name == "text" and not compressed,
                     "compression": "compressed (metadata only; decoding unsupported)" if compressed else "none",
                     "mapping_status": "memory range only; compressed file mapping unknown" if compressed else "NRO flat-image mapping"})
    no_overlap(ranges)
    ro_mem_off, ro_mem_size = struct.unpack_from("<II", b, 0x28)
    ro_metadata = {}
    for name, field_off in (("embedded", 0x68), ("dynamic_strings", 0x70), ("dynamic_symbols", 0x78)):
        rel, size = struct.unpack_from("<II", b, field_off)
        if size:
            check_range(rel, size, ro_mem_size, f"NRO {name} metadata within .rodata")
        ro_metadata[name] = {"rodata_offset": rel, "size": size}
    additional_header_offset = u32(b, 0x3c)
    additional_header = None
    if additional_header_offset:
        if additional_header_offset < 0x80:
            raise FormatError("NRO additional header overlaps fixed header")
        check_range(additional_header_offset, 0x80, len(b), "NRO additional header")
        if b[additional_header_offset:additional_header_offset + 4] != b"NRA0":
            raise FormatError("NRO additional header lacks NRA0 magic")
        compressed_size, hash_size, hash_offset = struct.unpack_from("<III", b, additional_header_offset + 0x10)
        check_range(hash_offset, hash_size, len(b), "NRO additional-header hash")
        additional_header = {"offset": additional_header_offset, "magic": "NRA0",
                             "compressed_size": compressed_size, "hash_size": hash_size,
                             "hash_offset": hash_offset,
                             "hash_hex": b[additional_header_offset + 0x60:additional_header_offset + 0x80].hex()}
    assets = None
    if declared_size < len(b) and b[declared_size:declared_size + 4] == b"ASET":
        check_range(declared_size, 0x38, len(b), "NRO ASET header")
        asset_version = u32(b, declared_size + 4)
        if asset_version != 0:
            raise FormatError("unsupported NRO ASET version")
        asset_sections = {}
        for key, off in (("icon", 8), ("nacp", 0x18), ("romfs", 0x28)):
            rel, size = struct.unpack_from("<QQ", b, declared_size + off)
            if size:
                check_range(rel, size, len(b) - declared_size, f"NRO ASET {key}")
                if rel < 0x38:
                    raise FormatError(f"NRO ASET {key} overlaps its header")
                if key == "nacp" and size != 0x4000:
                    raise FormatError("NRO ASET NACP section must be exactly 0x4000 bytes")
            asset_sections[key] = {"offset_from_aset": rel, "size": size,
                                   "file_offset": declared_size + rel if size else None}
        nonempty = [(x["offset_from_aset"], x["size"], name) for name, x in asset_sections.items() if x["size"]]
        no_overlap(nonempty)
        assets = {"offset": declared_size, "version": asset_version, "sections": asset_sections}
    return {"format": "NRO", "validation": "valid-subset", "version": version,
            "declared_image_size": declared_size, "flags": flags,
            "build_id_hex": b[0x40:0x60].hex(), "bss_size": u32(b, 0x38),
            "segments": segs,
            "ro_metadata": ro_metadata,
            "additional_header": additional_header, "assets": assets,
            "unsupported": ["compressed NRO decoding and hash verification", "full loader semantics"]}


def _inspect_sac(data: bytes, label: str) -> list[dict]:
    services = []
    pos = 0
    while pos < len(data):
        descriptor = data[pos]
        if descriptor & 0x78:
            raise FormatError(f"{label} SAC entry has nonzero reserved bits")
        name_len = (descriptor & 0x7) + 1
        end = pos + 1 + name_len
        if end > len(data):
            raise FormatError(f"{label} SAC entry at 0x{pos:x} exceeds its section")
        try:
            name = data[pos + 1:end].decode("ascii")
        except UnicodeDecodeError as exc:
            raise FormatError(f"{label} SAC service name is not ASCII") from exc
        if not name or b"\0" in data[pos + 1:end]:
            raise FormatError(f"{label} SAC entry has invalid service name")
        services.append({"name": name, "is_server": bool(descriptor & 0x80), "raw_descriptor": descriptor})
        pos = end
    return services


def _inspect_kernel_capabilities(data: bytes, label: str) -> list[dict]:
    if len(data) % 4:
        raise FormatError(f"{label} kernel-capability section is not 4-byte aligned")
    kinds = {3: "thread_info", 4: "enable_system_calls", 6: "memory_map", 7: "io_memory_map",
             10: "memory_region_map", 11: "enable_interrupts", 13: "misc_params",
             14: "kernel_version", 15: "handle_table_size", 16: "misc_flags"}
    entries = []
    for pos in range(0, len(data), 4):
        word = struct.unpack_from("<I", data, pos)[0]
        if word == 0xffffffff:
            entries.append({"offset": pos, "raw": word, "type": "unused"})
            continue
        cap_type = next((t for t in range(3, 17) if (word & ((1 << t) - 1)) == ((1 << t) - 1)
                         and not (word & (1 << t))), None)
        if cap_type not in kinds:
            raise FormatError(f"{label} unknown kernel-capability descriptor 0x{word:08x} at 0x{pos:x}")
        field = word >> (cap_type + 1)
        entry = {"offset": pos, "raw": word, "type": kinds[cap_type], "field": field}
        if cap_type == 3:
            entry["thread_info"] = {"lowest_priority": field & 0x3f, "highest_priority": (field >> 6) & 0x3f,
                                    "min_core": (field >> 12) & 0x3f, "max_core": (field >> 18) & 0x3f}
        elif cap_type == 4:
            entry["system_calls"] = {"index": (field >> 24) & 7,
                                     "enabled_ids": [((field >> 24) & 7) * 24 + bit for bit in range(24) if field & (1 << bit)]}
        elif cap_type == 6:
            entry["memory_map_fields"] = {"address_units": field & 0xffffff, "permission_read_only": bool(field & (1 << 24))}
        elif cap_type == 7:
            entry["io_memory_map_fields"] = {"begin_address_units": field & 0xffffff}
        elif cap_type == 10:
            entry["memory_region_map_fields"] = {"raw_region_bits": field}
        elif cap_type == 11:
            entry["interrupts"] = [field & 0x3ff, (field >> 10) & 0x3ff]
        elif cap_type == 13:
            entry["program_type"] = field & 7
        elif cap_type == 14:
            entry["kernel_version"] = {"major": (field >> 4) & 0x1fff, "minor": field & 0xf}
        elif cap_type == 15:
            entry["handle_table_size"] = field & 0x3ff
        elif cap_type == 16:
            entry["misc_flags"] = field & 0xffff
        entries.append(entry)
    return entries


def _inspect_aci_region(b: bytes, off: int, size: int, label: str) -> dict:
    check_range(off, size, len(b), f"NPDM {label}")
    region = b[off:off + size]
    if len(region) < 0x38 or region[:4] != b"ACI0":
        raise FormatError(f"NPDM {label} lacks a complete ACI0 header")
    program_id = struct.unpack_from("<Q", region, 0x10)[0]
    sections = {}
    for key, field_off in (("fac", 0x20), ("sac", 0x28), ("kernel_capabilities", 0x30)):
        sec_off, sec_size = struct.unpack_from("<II", region, field_off)
        if sec_size:
            check_range(sec_off, sec_size, len(region), f"NPDM {label} {key}")
            if sec_off < 0x38:
                raise FormatError(f"NPDM {label} {key} overlaps ACI0 header")
        sections[key] = {"offset": sec_off, "size": sec_size}
    no_overlap([(x["offset"], x["size"], name) for name, x in sections.items() if x["size"]])
    sac = sections["sac"]
    caps = sections["kernel_capabilities"]
    sections["sac"]["services"] = _inspect_sac(region[sac["offset"]:sac["offset"] + sac["size"]], label) if sac["size"] else []
    sections["kernel_capabilities"]["entries"] = _inspect_kernel_capabilities(region[caps["offset"]:caps["offset"] + caps["size"]], label) if caps["size"] else []
    return {"program_id": f"0x{program_id:016x}", "sections": sections}


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
        if idx < 3 and stored_size and off < 0x100:
            raise FormatError(f"KIP {name} payload overlaps fixed header")
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
    caps = _inspect_kernel_capabilities(b[0x80:0x100], "KIP")
    return {"format": "KIP", "validation": "valid-subset", "name": b[4:0x10].split(b"\0", 1)[0].decode("ascii", "replace"),
            "program_id": f"0x{struct.unpack_from('<Q', b, 0x10)[0]:016x}", "version": u32(b, 0x18),
            "flags": flags, "segments": segs, "kernel_capabilities": caps,
            "unsupported": ["BLZ decompression", "full kernel-capability policy semantics"]}


def inspect_npdm(b: bytes) -> dict:
    if len(b) < 0x80 or b[:4] != b"META":
        raise FormatError("NPDM requires META and complete 0x80-byte header")
    aci_off, aci_size, acid_off, acid_size = struct.unpack_from("<IIII", b, 0x70)
    sections = []
    aci_details = None
    acid_details = None
    for name, off, size in (("ACI", aci_off, aci_size), ("ACID", acid_off, acid_size)):
        if size:
            check_range(off, size, len(b), f"NPDM {name}")
            sections.append((off, size, name))
            expected = b"ACI0" if name == "ACI" else b"\0\0\0\0"  # ACID begins with signature.
            if name == "ACI" and b[off:off+4] != expected:
                raise FormatError("NPDM ACI section lacks ACI0 magic")
            if name == "ACID":
                if off < 0x80 or size < 0x238 or b[off+0x200:off+0x204] != b"ACID":
                    raise FormatError("NPDM ACID section lacks supported signature/header prefix")
                acid_struct = off + 0x200
                acid_size_field = u32(b, acid_struct + 4)
                if acid_size_field < 0x138 or acid_size_field > size - 0x100:
                    raise FormatError("NPDM ACID declared body size is invalid")
                acid_details = {"declared_size": acid_size_field,
                                "flags": u32(b, acid_struct + 0x0c),
                                "program_id_min": f"0x{struct.unpack_from('<Q', b, acid_struct + 0x10)[0]:016x}",
                                "program_id_max": f"0x{struct.unpack_from('<Q', b, acid_struct + 0x18)[0]:016x}"}
                for key, field_off in (("fac", 0x20), ("sac", 0x28), ("kernel_capabilities", 0x30)):
                    rel, sec_size = struct.unpack_from("<II", b, acid_struct + field_off)
                    check_range(rel, sec_size, size, f"NPDM ACID {key}")
                    if sec_size and rel < 0x238:
                        raise FormatError(f"NPDM ACID {key} overlaps ACID header")
                    acid_details[key] = {"offset_from_acid": rel, "size": sec_size}
                no_overlap([(x["offset_from_acid"], x["size"], name)
                            for name, x in acid_details.items() if isinstance(x, dict) and "offset_from_acid" in x and x["size"]])
                sac = acid_details["sac"]
                caps = acid_details["kernel_capabilities"]
                acid_details["sac"]["services"] = _inspect_sac(b[off + sac["offset_from_acid"]:off + sac["offset_from_acid"] + sac["size"]], "ACID") if sac["size"] else []
                acid_details["kernel_capabilities"]["entries"] = _inspect_kernel_capabilities(b[off + caps["offset_from_acid"]:off + caps["offset_from_acid"] + caps["size"]], "ACID") if caps["size"] else []
            elif name == "ACI":
                if off < 0x80:
                    raise FormatError("NPDM ACI section overlaps META header")
                aci_details = _inspect_aci_region(b, off, size, "ACI")
    no_overlap(sections)
    name = b[0x20:0x30].split(b"\0", 1)[0].decode("ascii", "replace")
    return {"format": "NPDM", "validation": "valid-subset", "name": name,
            "flags0": b[0x0c], "flags1": b[0x0d], "version": u32(b, 0x18),
            "stack_size": u32(b, 0x1c), "aci": {"offset": aci_off, "size": aci_size},
            "aci_details": aci_details,
            "acid": {"offset": acid_off, "size": acid_size, "signature_verified": False, "details": acid_details},
            "executable_regions": [],
            "unsupported": ["RSA signature verification", "FAC decoding", "full loader policy semantics"]}


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
