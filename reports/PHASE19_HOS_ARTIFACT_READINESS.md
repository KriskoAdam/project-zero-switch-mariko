# PROJECT ZERO Phase 19 — HOS Artifact Readiness

Date: 2026-10-31

## Result

Added a bounded, read-only JSON inspector for NSO, NRO, KIP1, NPDM and ELF. It computes a SHA-256, validates the implemented subset of each header/range contract, reports executable segment mappings as metadata, and can call the Phase 18 symbol-aware AArch64 ELF disassembler. It never executes input files. Synthetic inputs are constructed in memory during tests; no generated fixture is represented as firmware.

This is not a full Switch loader implementation. A successful `valid-subset` result means only that the fields listed by this parser passed its checks. It does not prove signature validity, loader acceptance, file provenance, or that an input came from Nintendo. Switch-compressed executable data is identified but not decompressed or disassembled.

## Format audit

| Format | Implemented and tested | Bounds / malformed behavior | Mapping and symbols | Explicit limitations |
|---|---|---|---|---|
| NSO0 | Fixed 0x100-byte header; version, flags, module ID, BSS; text/rodata/data offsets, memory offsets/sizes, stored sizes | Rejects truncated header, unknown flag bits, zero stored size for nonempty memory segment, file/address overflow, out-of-file payloads and overlapping file or memory ranges | Header-backed segments; text marked executable only if not compressed; no symbol table in NSO header | No LZ4 or 22.0+ Zbic decompression; no dynamic symbol parsing, full hash verification, relocation/loader emulation, or executable disassembly |
| NRO0 | 0x10-byte start prefix, `NRO0` header, version, declared image size, flags, module ID, BSS, three flat-image segment descriptors | Rejects short/invalid header, unknown flags, declared image outside file, unsupported compressed flag, invalid/overlapping segment ranges | Header-described flat image; text is identified as executable metadata, not blindly decoded. NRO has no ELF symbol table | No compressed NRO, ASET/NACP/RomFS parsing, MOD0/dynamic metadata, loader emulation or direct NRO disassembly. The NRO text mapping includes format-defined prefix/header bytes; this is not a claim that every byte is an instruction |
| KIP1 | 0x100-byte header; name, program ID, version, flags; text/ro/data/BSS descriptors and payload ranges | Rejects short header, unknown flags, out-of-file/overlapping payloads and uncompressed stored size exceeding memory size | Text marked executable only when uncompressed. No symbol table | No BLZ decompression, kernel capability decoding, loader validation or disassembly |
| NPDM | `META` 0x80-byte header; name, flags, version, stack size, ACI/ACID offsets and sizes | Rejects short header, out-of-bounds/overlapping sections, missing ACI magic, truncated ACID prefix or invalid declared ACID body size | Metadata only; no executable regions or symbols | Does not validate RSA signatures; does not decode FAC/SAC/KC or loader policy; size-zero optional sections accepted by this subset are not asserted to be semantically loadable |
| ELF | pyelftools parses class, endianness, architecture and PT_LOAD ranges; existing Phase 18 tool parses ELF function symbols and disassembles AArch64 using Capstone | pyelftools rejection is surfaced as a parser error; Phase 18 includes malformed symbol/range and limits checks | PT_LOAD mapping from ELF program headers; executable flags are metadata. Phase 18 decodes STT_FUNC ranges and separately labels entrypoint CFG heuristic; gaps remain undecoded | ELF parsing is not proof of console acceptance. Non-AArch64 ELF gets metadata only. Full relocation or loader semantics are not modeled |

Parser test functions: `inspect_nso`, `inspect_nro`, `inspect_kip`, `inspect_npdm`, `inspect_elf` and `inspect_bytes` in `scripts/inspect_switch_artifact.py`. They return a structured report or raise `FormatError`; CLI errors produce JSON with `validation: rejected` and exit code 2. Unexpected Python errors are not swallowed as a valid parse.

## Synthetic fixtures and test coverage

`tests/workspace-tests/test_switch_artifact_inspector.py` builds minimal test bytes at runtime (no binary fixtures committed). Coverage includes valid subset fixtures for all four Switch formats; truncated headers; out-of-range and overlapping regions; malformed NSO stored-size/compression metadata; unsupported compressed NRO; KIP compressed marking; NPDM section bounds/magic; unknown input; CLI JSON SHA-256 and synthetic labeling. Fixtures test parser behavior only. They are explicitly synthetic and do not encode any target firmware or real title metadata.

Automated results:

- Workspace suite: **25 passed** (includes 12 new format-inspector checks, 7 Phase 18 disassembler tests, and existing workspace checks).
- Lab suite: **11 passed** (synthetic model tests).
- Phase 14 validator: **6 passed** (synthetic/local evidence validator).
- Combined: **42 tests passed**.
- Python compile check: passed.
- `git diff --check`: passed.
- Runtime used: Python 3.14.7, Capstone 5.0.7, pyelftools 0.33, LIEF 1.0.0-d05b3499b. Note: `requirements.txt` pins Capstone 5.0.9, while the existing environment has 5.0.7; the test suite passed with 5.0.7, but a clean environment matching the pin was not verified in this run.

Exact commands, run from repository root:

```sh
../.venv/bin/python -m unittest discover -s tests/workspace-tests -v
../.venv/bin/python -m unittest discover -s lab/tests -v
../.venv/bin/python tools/phase14-mtp/test_validate_phase14.py
../.venv/bin/python -m py_compile scripts/inspect_switch_artifact.py scripts/inspect_arm64_binary.py tests/workspace-tests/test_switch_artifact_inspector.py tests/workspace-tests/test_arm64_disassembler.py
git diff --check
```

## Actual local input checks

The repository inventory found only these executable-looking local inputs in the adjacent PROJECT_ZERO app build:

| Path | SHA-256 | Meaning |
|---|---|---|
| `../PROJECT_ZERO/apps/PROJECT_ZERO/PROJECT_ZERO.elf` | `9798cc4c8c2089c859f372f2bc3edfbc23a0d3d32512ed086f2aea12f6aea3bd` | Host-side AArch64 homebrew build artifact; not Nintendo firmware |
| `../PROJECT_ZERO/apps/PROJECT_ZERO/PROJECT_ZERO.nro` | `55ac62855d2675b77d69e255cc3652eb0b6c090190c49125213cac65263cd0e7` | Locally built PROJECT_ZERO homebrew NRO; not a stock HOS executable |
| `../PROJECT_ZERO/apps/PROJECT_ZERO/release/switch/PROJECT_ZERO.nro` | Not independently parsed in this run | Release copy of homebrew NRO; not HOS |

Reproduction commands:

```sh
../.venv/bin/python scripts/inspect_switch_artifact.py ../PROJECT_ZERO/apps/PROJECT_ZERO/PROJECT_ZERO.nro
../.venv/bin/python scripts/inspect_switch_artifact.py ../PROJECT_ZERO/apps/PROJECT_ZERO/PROJECT_ZERO.elf --disassemble
```

The NRO JSON reports the format-declared image size (331,776 bytes), header version 0, flags 0, BSS 49,152 bytes, and three flat-image ranges. The complete file is 357,104 bytes because NRO assets may follow the declared image size. Those values identify the local app build, not Horizon OS. The ELF path produces PT_LOAD metadata and invokes the repaired Phase 18 analyzer; its function symbols are symbol-backed, and the `_start` fallback remains clearly marked heuristic. Neither run analyzed Nintendo system code.

## Independent validation and disagreements

Format layouts were compared field-by-field against the public Switchbrew descriptions: [NSO0](https://switchbrew.org/wiki/NSO), [NRO0](https://switchbrew.org/wiki/NRO), [KIP1](https://switchbrew.org/wiki/KIP1), and [NPDM](https://switchbrew.org/wiki/NPDM). These are community-maintained technical references, not Nintendo specifications. The local environment did not contain an independent Switch-format parser or a legally supplied HOS sample for cross-parser comparison. Therefore this phase reports no independent implementation agreement for NSO/NRO/KIP/NPDM. No discrepancies were silently reconciled.

For ELF/AArch64, Phase 18 separately compared the host sample's decoded instructions with Apple `objdump` and Ghidra; see `reports/PHASE18_DISASSEMBLER_VALIDATION.md`. These checks do not validate HOS compatibility.

## Readiness and missing artifacts

There is no locally available, verified HOS 23.0.1 NSO/KIP/NPDM, NCA/ExeFS executable, or corresponding manifest/build identity in the project. The app ELF/NRO is not a substitute. A meaningful stock-system reverse-engineering pass needs an **authorized, legally obtained, integrity-verifiable and target-identified unencrypted executable** (or a legitimately available public source/research artifact) and its associated NPDM/metadata. For a container, its format, encryption state, hashes and provenance must be established before interpreting its contents. The project will not obtain or decrypt proprietary firmware, extract keys, or modify the console.

Even with a suitable executable, static analysis cannot establish runtime reachability or exploitability on Mariko/HOS 23.0.1. A reproducible public finding or safe, authorized target evidence would still be needed for those claims.

## Commit and publication

The Phase 18/19 implementation and its evidence updates were committed locally. A push was attempted with `git push origin main` and failed because this environment could not resolve `github.com`. `gh auth status` also reports the configured token is invalid. No remote update was made; the local commit is available for a later authenticated push.

## Sources

- NSO layout and compression flags: https://switchbrew.org/wiki/NSO — community format documentation; accessed 2026-10-31.
- NRO layout, flags and additional header: https://switchbrew.org/wiki/NRO — community format documentation; accessed 2026-10-31.
- KIP1 header, segment descriptors and BLZ note: https://switchbrew.org/wiki/KIP1 — community format documentation; accessed 2026-10-31.
- NPDM META/ACID/ACI layout: https://switchbrew.org/wiki/NPDM — community format documentation; accessed 2026-10-31.
- ELF structure parsing: pyelftools 0.33 in the repository's isolated virtual environment; AArch64 disassembly was run with installed Capstone 5.0.7 (the project pin is 5.0.9; see environment note above).
