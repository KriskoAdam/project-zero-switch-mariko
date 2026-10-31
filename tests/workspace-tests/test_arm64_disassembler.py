import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('inspect_arm64_binary', ROOT / 'scripts' / 'inspect_arm64_binary.py')
TOOL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TOOL)


def make_elf(path: Path, symbols=(), text_size=0x100) -> Path:
    """Build a tiny valid AArch64 ELF with executable bytes and an optional symtab."""
    text = bytearray(text_size)
    # b 0x80 at entrypoint; bytes at 0x4 and 0x8 are deliberate embedded data.
    text[0:4] = bytes.fromhex('20000014')
    text[4:8] = bytes.fromhex('f0000000')
    text[8:16] = b'HOMEBREW'
    if text_size >= 0x88:
        text[0x80:0x84] = bytes.fromhex('e00300aa')  # mov x0, x0
        text[0x84:0x88] = bytes.fromhex('c0035fd6')  # ret

    names = ['']
    name_offsets = {'': 0}
    for name, _value, _size, _kind in symbols:
        if name not in name_offsets:
            name_offsets[name] = sum(len(n.encode()) + 1 for n in names)
            names.append(name)
    strtab = b'\0'.join(n.encode() for n in names) + b'\0'
    symtab = bytearray(24)  # null symbol
    for name, value, size, kind in symbols:
        st_info = kind & 0xF
        symtab.extend(struct.pack('<IBBHQQ', name_offsets[name], st_info, 0, 1, value, size))

    shstr = b'\0.text\0.symtab\0.strtab\0.shstrtab\0'
    sh_name = {'text': 1, 'symtab': 7, 'strtab': 15, 'shstrtab': 23}
    text_off = 0x100
    sym_off = text_off + len(text)
    sym_off = (sym_off + 7) & ~7
    str_off = sym_off + len(symtab)
    shstr_off = str_off + len(strtab)
    shoff = (shstr_off + len(shstr) + 7) & ~7
    shentsize = 64
    shnum = 5
    ident = b'\x7fELF' + bytes([2, 1, 1, 0]) + bytes(8)
    ehdr = struct.pack('<16sHHIQQQIHHHHHH', ident, 2, 183, 1, 0, 64, shoff, 0,
                       64, 56, 1, shentsize, shnum, 4)
    phdr = struct.pack('<IIQQQQQQ', 1, 5, text_off, 0, 0, len(text), len(text), 0x1000)
    blob = bytearray(ehdr + phdr)
    blob.extend(bytes(text_off - len(blob)))
    blob.extend(text)
    blob.extend(bytes(sym_off - len(blob)))
    blob.extend(symtab)
    blob.extend(strtab)
    blob.extend(shstr)
    blob.extend(bytes(shoff - len(blob)))
    blob.extend(bytes(64))  # null section
    blob.extend(struct.pack('<IIQQQQIIQQ', sh_name['text'], 1, 6, 0, text_off, len(text), 0, 0, 4, 0))
    blob.extend(struct.pack('<IIQQQQIIQQ', sh_name['symtab'], 2, 0, 0, sym_off, len(symtab), 3, 1, 8, 24))
    blob.extend(struct.pack('<IIQQQQIIQQ', sh_name['strtab'], 3, 0, 0, str_off, len(strtab), 0, 0, 1, 0))
    blob.extend(struct.pack('<IIQQQQIIQQ', sh_name['shstrtab'], 3, 0, 0, shstr_off, len(shstr), 0, 0, 1, 0))
    path.write_bytes(blob)
    return path


class Arm64DisassemblerTests(unittest.TestCase):
    def test_embedded_data_is_not_linear_decoded_as_function_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = make_elf(Path(tmp) / 'embedded.elf', [('_start', 0, 0x88, 2)])
            result = TOOL.analyze(path)
        addresses = {row['address'] for row in result['instructions']}
        self.assertIn('0x0', addresses)
        self.assertIn('0x80', addresses)
        self.assertNotIn('0x4', addresses)
        self.assertNotIn('0x8', addresses)
        self.assertEqual(result['instructions'][0]['source'], 'symbol-backed')
        self.assertGreater(len(result['undecoded_executable_regions']), 0)

    def test_missing_function_symbols_uses_entrypoint_cfg_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = make_elf(Path(tmp) / 'no-symbols.elf')
            result = TOOL.analyze(path)
        self.assertEqual(result['function_symbol_count'], 0)
        self.assertEqual(result['entrypoint_range']['source'], 'entrypoint-control-flow-heuristic')
        self.assertEqual([x['address'] for x in result['instructions']], ['0x0', '0x80', '0x84'])
        self.assertTrue(all(x['source'] == 'entrypoint-control-flow-heuristic' for x in result['instructions']))

    def test_zero_sized_function_infers_bound_from_next_function(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = make_elf(Path(tmp) / 'zero-sized.elf', [('_start', 0, 0, 2), ('next', 0x88, 8, 2)])
            result = TOOL.analyze(path)
        inferred = [r for r in result['symbol_ranges'] if '._start.' in r['symbols'] or '_start' in r['symbols']]
        self.assertTrue(inferred)
        self.assertIn('symbol-backed-inferred-zero-size', inferred[0]['source'])
        self.assertEqual(inferred[0]['end'], '0x88')

    def test_overlapping_symbols_are_merged_without_duplicate_instructions(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = make_elf(Path(tmp) / 'overlap.elf', [('_start', 0, 0x88, 2), ('alias', 0x80, 8, 2)])
            result = TOOL.analyze(path)
        group = next(r for r in result['symbol_ranges'] if '_start' in r['symbols'])
        self.assertIn('alias', group['symbols'])
        self.assertEqual(group['overlap_count'], 1)
        addresses = [x['address'] for x in result['instructions']]
        self.assertEqual(len(addresses), len(set(addresses)))

    def test_malformed_out_of_section_symbol_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = make_elf(Path(tmp) / 'bad-range.elf', [('bad', 0x200, 0x20, 2)])
            result = TOOL.analyze(path)
        self.assertTrue(any(x['name'] == 'bad' for x in result['skipped_symbols']))

    def test_instruction_and_byte_limits(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = make_elf(Path(tmp) / 'limits.elf', [('_start', 0, 0x88, 2)])
            by_insn = TOOL.analyze(path, max_instructions=1, max_bytes=100)
            by_bytes = TOOL.analyze(path, max_instructions=100, max_bytes=4)
        self.assertEqual(by_insn['instruction_count'], 1)
        self.assertEqual(by_insn['decoded_bytes'], 4)
        self.assertEqual(by_bytes['instruction_count'], 1)
        self.assertEqual(by_bytes['decoded_bytes'], 4)

    def test_invalid_elf_input_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'invalid.elf'
            path.write_bytes(b'not an executable')
            with self.assertRaises(ValueError):
                TOOL.analyze(path)


if __name__ == '__main__':
    unittest.main()
