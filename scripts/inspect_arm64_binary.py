#!/usr/bin/env python3
"""Read-only ARM64 instruction inventory for ELF or Mach-O binaries.

ELF code is decoded from STT_FUNC symbol ranges. When the ELF entrypoint is
not covered by a function symbol, a separate control-flow-guided heuristic is
used for that entrypoint only. Uncovered executable bytes are reported, never
silently treated as instructions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import lief
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
from capstone.arm64 import ARM64_OP_IMM
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection

MAX_U64 = (1 << 64) - 1


def _merge_ranges(ranges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge overlapping (not merely adjacent) symbol intervals safely."""
    merged: list[dict[str, Any]] = []
    for item in sorted(ranges, key=lambda r: (r['start'], r['end'], r['name'])):
        if not merged or item['start'] >= merged[-1]['end']:
            merged.append({
                'start': item['start'], 'end': item['end'],
                'symbols': [item['name']], 'sources': [item['source']],
                'overlap_count': 0,
            })
            continue
        current = merged[-1]
        current['end'] = max(current['end'], item['end'])
        if item['name'] not in current['symbols']:
            current['symbols'].append(item['name'])
        if item['source'] not in current['sources']:
            current['sources'].append(item['source'])
        current['overlap_count'] += 1
    return merged


def _subtract_ranges(start: int, end: int, covered: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Return the half-open gaps in [start, end) after unioning covered ranges."""
    cursor = start
    gaps: list[tuple[int, int]] = []
    for left, right in sorted(covered):
        left, right = max(start, left), min(end, right)
        if right <= cursor:
            continue
        if left > cursor:
            gaps.append((cursor, left))
        cursor = max(cursor, right)
        if cursor >= end:
            break
    if cursor < end:
        gaps.append((cursor, end))
    return [(a, b) for a, b in gaps if b > a]


def _in_region(address: int, regions: list[dict[str, Any]]) -> dict[str, Any] | None:
    for region in regions:
        if region['start'] <= address < region['end']:
            return region
    return None


def _elf_sections(elf: ELFFile) -> list[dict[str, Any]]:
    sections = []
    for index, section in enumerate(elf.iter_sections()):
        if not section['sh_flags'] & 0x4:  # SHF_EXECINSTR
            continue
        start = int(section['sh_addr'])
        size = int(section['sh_size'])
        if size > 0 and start <= MAX_U64 - size:
            sections.append({'index': index, 'start': start, 'end': start + size, 'name': section.name})
    return sections


def _symbol_ranges(elf: ELFFile, regions: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, str]], list[dict[str, Any]]]:
    sections = {s['index']: s for s in _elf_sections(elf)}
    functions: list[dict[str, Any]] = []
    labels: list[dict[str, str]] = []
    skipped: list[dict[str, Any]] = []

    tables = [s for s in elf.iter_sections() if isinstance(s, SymbolTableSection)]
    raw_symbols = []
    for table in tables:
        try:
            for symbol in table.iter_symbols():
                name = symbol.name or '<unnamed>'
                value, size = int(symbol['st_value']), int(symbol['st_size'])
                shndx = symbol['st_shndx']
                stype = symbol['st_info']['type']
                if stype == 'STT_FUNC':
                    raw_symbols.append({'name': name, 'value': value, 'size': size, 'shndx': shndx})
                elif name != '<unnamed>' and isinstance(shndx, int):
                    labels.append({'name': name, 'value': value, 'shndx': shndx})
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            skipped.append({'name': '<symbol table>', 'reason': f'malformed symbol table: {type(exc).__name__}'})

    # Infer safe upper bounds for zero-sized functions from the next function
    # in the same executable section; otherwise use that section's end.
    by_section: dict[int, list[dict[str, Any]]] = {}
    for item in raw_symbols:
        if not isinstance(item['shndx'], int) or item['shndx'] not in sections:
            skipped.append({'name': item['name'], 'reason': 'not in a known executable section'})
            continue
        by_section.setdefault(item['shndx'], []).append(item)

    for section_index, items in by_section.items():
        sec = sections[section_index]
        ordered_values = sorted({x['value'] for x in items if sec['start'] <= x['value'] < sec['end']})
        for item in items:
            start, declared = item['value'], item['size']
            if start < sec['start'] or start >= sec['end'] or start > MAX_U64:
                skipped.append({'name': item['name'], 'reason': 'function start is outside its executable section'})
                continue
            if declared < 0 or declared > MAX_U64 or start > MAX_U64 - declared:
                skipped.append({'name': item['name'], 'reason': 'malformed function size or address overflow'})
                continue
            if declared == 0:
                next_values = [v for v in ordered_values if v > start]
                end = min(next_values[0] if next_values else sec['end'], sec['end'])
                source = 'symbol-backed-inferred-zero-size'
            else:
                end = start + declared
                source = 'symbol-backed'
                if end > sec['end']:
                    end = sec['end']
                    source = 'symbol-backed-clipped-to-section'
            region = _in_region(start, regions)
            if region is None:
                skipped.append({'name': item['name'], 'reason': 'function start has no file-backed executable bytes'})
                continue
            end = min(end, region['end'])
            if end <= start:
                skipped.append({'name': item['name'], 'reason': 'empty range after validation'})
                continue
            functions.append({'name': item['name'], 'start': start, 'end': end, 'source': source})
    return functions, labels, skipped


def _imm_target(insn) -> int | None:
    for operand in insn.operands:
        if operand.type == ARM64_OP_IMM:
            return int(operand.imm)
    return None


def _decode_reachable(blob: bytes, base: int, start: int, end: int, md: Cs,
                      max_instructions: int, max_bytes: int, already: set[int],
                      source: str, symbols: list[str]) -> tuple[list[dict[str, Any]], int]:
    """Decode only instructions reachable from a range entry; do not linear-sweep data."""
    queue = [start]
    found: dict[int, dict[str, Any]] = {}
    used_bytes = 0
    while queue and len(already) + len(found) < max_instructions and used_bytes < max_bytes:
        address = queue.pop()
        if address in already or address in found or not (start <= address < end):
            continue
        offset = address - base
        if offset < 0 or offset >= len(blob):
            continue
        remaining_budget = max_bytes - used_bytes
        code = blob[offset:min(len(blob), offset + min(end - address, remaining_budget))]
        insns = list(md.disasm(code, address, count=1))
        if not insns:
            continue
        insn = insns[0]
        if insn.size <= 0 or address + insn.size > end or insn.size > remaining_budget:
            continue
        found[address] = {
            'address': hex(address), 'mnemonic': insn.mnemonic,
            'operands': insn.op_str, 'size': insn.size,
            'source': source, 'symbols': symbols,
        }
        used_bytes += insn.size
        mnemonic = insn.mnemonic.lower()
        next_address = address + insn.size
        target = _imm_target(insn)
        if mnemonic in {'ret', 'eret', 'br'}:
            continue
        if mnemonic == 'b':
            if target is not None and start <= target < end:
                queue.append(target)
            continue
        if mnemonic.startswith('b.') or mnemonic in {'cbz', 'cbnz', 'tbz', 'tbnz'}:
            if target is not None and start <= target < end:
                queue.append(target)
            if next_address < end:
                queue.append(next_address)
            continue
        # Calls return to the following instruction. Do not enter callees here;
        # they are separately analyzed through their own symbol ranges.
        if next_address < end:
            queue.append(next_address)
    return list(found.values()), used_bytes


def _analyze_elf(path: Path, max_instructions: int, max_bytes: int) -> dict[str, Any]:
    try:
        with path.open('rb') as stream:
            elf = ELFFile(stream)
            if elf.elfclass != 64 or not elf.little_endian or elf.header['e_machine'] != 'EM_AARCH64':
                raise ValueError('ELF must be 64-bit little-endian AArch64')
            regions = []
            for segment in elf.iter_segments():
                if segment['p_type'] != 'PT_LOAD' or not int(segment['p_flags']) & 1:  # PF_X
                    continue
                data = segment.data()
                start = int(segment['p_vaddr'])
                if data and start <= MAX_U64 - len(data):
                    regions.append({'start': start, 'end': start + len(data), 'data': data})
            functions, labels, skipped = _symbol_ranges(elf, regions)
            entry = int(elf.header['e_entry'])
            entry_range = None
            if _in_region(entry, regions) and not any(f['start'] <= entry < f['end'] for f in functions):
                region = _in_region(entry, regions)
                section = next((s for s in _elf_sections(elf) if s['start'] <= entry < s['end']), None)
                boundary_candidates = [f['start'] for f in functions if f['start'] > entry and f['start'] < region['end']]
                end = min(boundary_candidates) if boundary_candidates else region['end']
                names = [x['name'] for x in labels if x['value'] == entry]
                name = '_start' if '_start' in names else (names[0] if names else '<ELF entrypoint>')
                entry_range = {'name': name, 'start': entry,
                               'end': end, 'source': 'entrypoint-control-flow-heuristic',
                               'section': section['name'] if section else None}

            ranges = _merge_ranges(functions)
            if entry_range and entry_range['end'] > entry_range['start']:
                ranges.append({'start': entry_range['start'], 'end': entry_range['end'],
                               'symbols': [entry_range['name']], 'sources': [entry_range['source']],
                               'overlap_count': 0})
                ranges = _merge_ranges([
                    {'start': r['start'], 'end': r['end'], 'name': name, 'source': src}
                    for r in ranges for name in r['symbols'] for src in r['sources']
                ])
            ranges.sort(key=lambda x: (x['start'], x['end']))

            md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
            md.detail = True
            all_instructions: dict[int, dict[str, Any]] = {}
            decoded_bytes = 0
            public_ranges = []
            for item in ranges:
                starts = [x['start'] for x in functions if item['start'] <= x['start'] < item['end']]
                if entry_range and item['start'] <= entry_range['start'] < item['end']:
                    starts.append(entry_range['start'])
                sources = item['sources']
                if any(s == 'entrypoint-control-flow-heuristic' for s in sources):
                    source = 'entrypoint-control-flow-heuristic'
                elif all(s == 'symbol-backed' for s in sources):
                    source = 'symbol-backed'
                else:
                    source = '+'.join(sorted(set(sources)))
                names = item['symbols']
                for seed in sorted(set(starts)):
                    if len(all_instructions) >= max_instructions or decoded_bytes >= max_bytes:
                        break
                    region = _in_region(seed, regions)
                    if region is None:
                        continue
                    ins, used = _decode_reachable(region['data'], region['start'], seed, item['end'], md,
                                                  max_instructions, max_bytes - decoded_bytes,
                                                  set(all_instructions), source, names)
                    decoded_bytes += used
                    for row in ins:
                        all_instructions[int(row['address'], 16)] = row
                public_ranges.append({'start': hex(item['start']), 'end': hex(item['end']),
                                      'symbols': names, 'source': source,
                                      'source_details': sources,
                                      'overlap_count': item['overlap_count']})

            instructions = [all_instructions[k] for k in sorted(all_instructions)]
            decoded_intervals = [(a, a + row['size']) for a, row in all_instructions.items()]
            undecoded = []
            for region in regions:
                for left, right in _subtract_ranges(region['start'], region['end'], decoded_intervals):
                    undecoded.append({'start': hex(left), 'end': hex(right), 'size': right-left,
                                      'reason': 'not decoded: embedded data, padding, unreachable bytes, or analysis limits'})
            return {
                'format': 'ELF', 'architecture': 'AArch64', 'entrypoint': hex(entry),
                'function_symbol_count': len(functions), 'symbol_ranges': public_ranges,
                'entrypoint_range': ({'name': entry_range['name'], 'start': hex(entry_range['start']),
                                      'end': hex(entry_range['end']), 'source': entry_range['source']}
                                     if entry_range else None),
                'skipped_symbols': skipped, 'instruction_count': len(instructions),
                'decoded_bytes': decoded_bytes,
                'disassembly_source': 'symbol-backed ranges plus entrypoint CFG heuristic when needed; no linear sweep',
                'instructions': instructions, 'undecoded_executable_regions': undecoded,
            }
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
        raise ValueError(f'cannot analyze ELF: {exc}') from exc


def _analyze_macho(binary: lief.MachO.Binary, max_instructions: int, max_bytes: int) -> dict[str, Any]:
    """Conservative Mach-O fallback: only follow the image entrypoint, if present."""
    regions = []
    for section in binary.sections:
        if section.size and (section.flags & lief.MachO.Section.FLAGS.PURE_INSTRUCTIONS or '__text' in section.name):
            data = bytes(section.content)
            if data:
                regions.append({'start': int(section.virtual_address), 'end': int(section.virtual_address)+len(data), 'data': data})
    entry = int(binary.entrypoint)
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    md.detail = True
    rows = []
    if region := _in_region(entry, regions):
        rows, _ = _decode_reachable(region['data'], region['start'], entry, region['end'], md,
                                    max_instructions, max_bytes, set(), 'entrypoint-control-flow-heuristic', ['<Mach-O entrypoint>'])
    decoded = {int(x['address'], 16): x['size'] for x in rows}
    gaps = []
    for region in regions:
        for left, right in _subtract_ranges(region['start'], region['end'], [(a, a+s) for a,s in decoded.items()]):
            gaps.append({'start': hex(left), 'end': hex(right), 'size': right-left,
                         'reason': 'not decoded: embedded data, padding, unreachable bytes, or analysis limits'})
    return {'format':'Mach-O','architecture':str(binary.header.cpu_type),'entrypoint':hex(entry),
            'function_symbol_count':0,'symbol_ranges':[], 'entrypoint_range':None,
            'skipped_symbols':[], 'instruction_count':len(rows), 'decoded_bytes':sum(decoded.values()),
            'disassembly_source':'entrypoint CFG heuristic; no linear sweep',
            'instructions':sorted(rows,key=lambda x:int(x['address'],16)),
            'undecoded_executable_regions':gaps}


def analyze(path: Path, max_instructions: int = 10000, max_bytes: int = 4*1024*1024) -> dict[str, Any]:
    if max_instructions < 1 or max_bytes < 4:
        raise ValueError('limits must be positive and max-bytes at least 4')
    raw = path.read_bytes()
    parsed = lief.parse(str(path))
    if parsed is None:
        raise ValueError('unsupported or malformed binary')
    if raw.startswith(b'\x7fELF'):
        analysis = _analyze_elf(path, max_instructions, max_bytes)
    elif isinstance(parsed, lief.MachO.FatBinary):
        slices = []
        for binary in parsed:
            item = _analyze_macho(binary, max_instructions, max_bytes)
            item['architecture'] = str(binary.header.cpu_type)
            slices.append(item)
        instructions = []
        undecoded = []
        for item in slices:
            instructions.extend({**row, 'architecture': item['architecture']} for row in item['instructions'])
            undecoded.extend({**row, 'architecture': item['architecture']} for row in item['undecoded_executable_regions'])
        analysis = {
            'format': 'Mach-O Universal', 'architecture': [x['architecture'] for x in slices],
            'entrypoint': None, 'function_symbol_count': 0, 'symbol_ranges': [],
            'entrypoint_range': None, 'skipped_symbols': [],
            'instruction_count': len(instructions),
            'decoded_bytes': sum(x['decoded_bytes'] for x in slices),
            'disassembly_source': 'per-slice entrypoint CFG heuristic; no linear sweep',
            'instructions': instructions, 'undecoded_executable_regions': undecoded,
            'slices': slices,
        }
    elif isinstance(parsed, lief.MachO.Binary):
        analysis = _analyze_macho(parsed, max_instructions, max_bytes)
    else:
        raise ValueError('unsupported binary format; expected ELF or Mach-O')
    import capstone
    return {'path':str(path.resolve()), 'sha256':hashlib.sha256(raw).hexdigest(),
            'capstone_version':'.'.join(map(str,capstone.cs_version())),
            'limits':{'max_instructions':max_instructions,'max_bytes':max_bytes}, **analysis,
            'note':'Static disassembly only. Undecoded executable bytes are not evidence of code absence or presence.'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('binary', type=Path)
    parser.add_argument('--max-instructions', type=int, default=10000)
    parser.add_argument('--max-bytes', type=int, default=4*1024*1024)
    parser.add_argument('-o','--output', type=Path)
    args = parser.parse_args()
    try:
        result = analyze(args.binary, args.max_instructions, args.max_bytes)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    output = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.write_text(output)
    else:
        print(output, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
