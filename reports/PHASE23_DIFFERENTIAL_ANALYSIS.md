# PROJECT ZERO Phase 23 — Differential Switch Format Analysis

Date: 2026-10-31  
Reference implementation: NSTool v1.9.2, source commit `e89ea84bd70c11b67ebec9153fb4a446f18a9d3d` (MIT).  
Scope: read-only parser comparison and bounded structural support. No HOS/Mariko executable was present or analyzed. Synthetic inputs and the project's own homebrew NRO are clearly distinguished below.

## Result

The PROJECT ZERO inspector now reads additional NSO segment metadata and compression flags, NRO compression/header/ASET ranges, KIP kernel-capability descriptors, and NPDM ACI/ACID service-access and kernel-capability lists. It also corrects an ACID header offset error found during source comparison: the RSA-2048 signature and public-key blocks occupy the first `0x200` bytes; `ACID` begins at `+0x200`, not `+0x100`.

The new structural decoding does not decompress LZ4, ZBIC, or BLZ; verify signatures or hashes; validate FAC semantics; or emulate Horizon's loader. It is not a security finding. No actual Horizon OS artifact was available.

## Source-level comparison

| Format | NSTool v1.9.2 source coverage | PROJECT ZERO before → after Phase 23 |
|---|---|---|
| NSO | `NsoHeader` describes the `0x100` header, segments, module-name fields, rodata embedded/dynamic metadata, three SHA-256 fields, LZ4 segment bits, and hash bits. The checked-in header enum stops at bits 0–5; it does not define ExecuteOnlyMemory bit 6 or ZBIC selector bit 7. `NsoProcess` decompresses marked LZ4 sections and can check flagged hashes. | Had basic segment offsets/sizes and a generic compressed label; did not expose module name, hashes, EOM, or rodata metadata. Now reports those fields, enforces payload/header boundaries, treats bits 0–2 as per-segment compression, and reports LZ4 vs ZBIC based on bit 7. ZBIC is metadata-only. A synthetic bit-7-only header now correctly leaves every segment uncompressed. |
| NRO | Parses the `0x80` NRO header, segments, module/build ID, NACP and standalone ASET inputs. Current parser rejects nonzero NRO flags, including the documented 23.0+ compression flag. | Previously rejected compressed flag 1<<1 and omitted ASET validation. Now preserves segment memory metadata while marking compressed file offsets unknown, parses the documented `NRA0` additional-header fields, validates uncompressed `.text/.ro/.data` ranges and rodata metadata, and bounds-checks appended ASET/icon/NACP/RomFS ranges. NACP must be the documented `0x4000` bytes. Payload decompression and NACP interpretation are not claimed. |
| KIP1 | Parses KIP header and segment metadata, displays kernel capabilities; `decompressData()` is explicitly unimplemented for BLZ. | Previously exposed segments but not capability descriptors. Now decodes the fixed 0x80-byte capability area into documented descriptor families and reports BLZ as unsupported. It does not decompress KIP segments or assess policy. |
| NPDM | Parses META, ACI, ACID, FAC, SAC and kernel-capability structures. ACID signature validation is optional and depends on keys; it is not used here. | Previously validated top-level ACI/ACID bounds and exposed Flags1 but did not parse SAC/KC. Now validates complete ACI0 and RSA-2048 ACID header prefixes, section bounds and overlaps; parses service names/server bits and the supported KC descriptor families in both ACI and ACID. It does not verify the ACID signature, decode FAC rights, or prove ACI permissions are authorized by ACID. |

### Source-confirmed details and disagreements

- Switchbrew documents NSO bit 6 as ExecuteOnlyMemory and bit 7 as the ZBIC algorithm selector since HOS 22.0. The selector chooses the compression method; per-segment bits 0–2 indicate which segments are compressed. Phase 22's text saying the Phase 19 parser rejected bit 7 was inaccurate: the code accepted bits through `0xff` and marked any bit-7 file as generically compressed. Phase 23 corrects both the historical statement and the implementation semantics.
- NSTool's `ThreadInfoEntry` uses four 6-bit fields: min/max priority and min/max CPU ID. Its output on the synthetic fixture was priorities 2–40, CPUs 0–3, matching the Phase 23 decoder. The current Switchbrew NPDM table expresses core-number fields as bits 16–23 and 24–31, which does not match NSTool's 6-bit field interpretation. We record the source disagreement and follow the executable reference's observed decoding for this parser, without claiming that a real HOS manifest has been validated.
- NSTool's NRO importer rejects all nonzero NRO flags in v1.9.2. Phase 23 follows the published 23.0+ flag description to report compressed metadata, but does not claim to parse/decompress compressed NRO content.
- NSTool's NPDM importer reads ACI and ACID structures. The ACID struct layout in its public header is `0x238` bytes: signature `0x100`, second RSA public-key block `0x100`, then ACID fields at `+0x200`. This directly exposed and fixed the project's previous `+0x100` magic assumption.
- NSTool parses KIP capability lists, but its BLZ decompression path is a stub. Recognition is not decompression support.

## Differential experiments

NSTool was the independently built macOS binary from Phase 22 (`/tmp/pz22-nstool/bin/nstool`, v1.9.2). It was run without `-k`, `-y`, extraction options, or keys. Its startup warned that `prod.keys` and `title.keys` were absent; no keys were accessed. Fixtures below were generated in memory by `tests/workspace-tests/test_switch_artifact_inspector.py`, written only under `/tmp`, and contain no Nintendo data.

| Input | NSTool result | PROJECT ZERO result | Interpretation |
|---|---|---|---|
| Local `../PROJECT_ZERO/apps/PROJECT_ZERO/PROJECT_ZERO.nro`, SHA-256 `55ac62855d2675b77d69e255cc3652eb0b6c090190c49125213cac65263cd0e7` | `--showlayout` exit 0; image size `0x51000`; text `0/0x3c000`, ro `0x3c000/0x10000`, data `0x4c000/0x5000`, BSS `0xc000`; ASET/NACP displayed | CLI valid-subset; same image/segment metadata, BSS, ModuleId; ASET icon/NACP/RomFS boundaries checked | Agreement on real local homebrew input only. It is not Nintendo firmware. |
| Synthetic ACI NPDM | `-t meta` exit 0; ProgramID `0x010000000000100a`; SAC `svc(isSrv)`; thread priority 2–40, CPU 0–3 | Same ProgramID, `svc` server bit and decoded thread values | Agreement on a constructed structural fixture; no signature or loader validity claim. |
| Synthetic ACID NPDM | `-v -t meta` exit 0; ProgramID range `...1000`–`...1fff`; SAC `svc`; thread priority 1–20, CPU 0–2 | ACID parsed from `+0x200`, same SAC/KC values; signature result explicitly false/unverified | Confirms the corrected offset against the independent source parser, not cryptographic validity. |
| Synthetic KIP1 capability fixture | `-t kip` exit 0; thread priority 5–32, CPU 1–4 | Same decoded values | Agreement on the exercised descriptor. |
| Synthetic standalone ASET with a 0x4000-byte NACP | `-t aset` exit 0 and NACP parsed | NRO-appended ASET ranges accepted and bounded; NACP content not decoded | Header and section-geometry comparison; the interface modes differ. |
| Synthetic NSO basic fixture | `-t nso --showlayout` exit 0; segment file offsets/sizes agree | Basic segment mapping and newly exposed metadata parsed | No ZBIC-compressed content tested. NSTool v1.9.2's flag definitions omit bits 6–7. |

Reproduction commands (from this repository root; temporary inputs are generated by the test helper):

```sh
../.venv/bin/python -m unittest discover -s tests/workspace-tests -p 'test_switch_artifact_inspector.py' -v
../.venv/bin/python scripts/inspect_switch_artifact.py ../PROJECT_ZERO/apps/PROJECT_ZERO/PROJECT_ZERO.nro
../.venv/bin/python - <<'PY'
import importlib.util
from pathlib import Path
p = Path('tests/workspace-tests/test_switch_artifact_inspector.py')
s = importlib.util.spec_from_file_location('phase23_fixtures', p)
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
for name, data in {
    'pz23-aci.npdm': m.npdm_with_sac_and_caps(),
    'pz23-acid.npdm': m.npdm_with_acid_sac_and_caps(),
    'pz23-nso.nso': m.nso(),
    'pz23-kip.kip': m.kip(),
    'pz23-assets.bin': m.nro_with_assets()[len(m.nro()):],
}.items():
    Path('/tmp', name).write_bytes(data)
PY
cd /tmp/pz22-nstool
HOME=/tmp/pz22-clean-home ./bin/nstool --showlayout /absolute/path/to/PROJECT_ZERO.nro
HOME=/tmp/pz22-clean-home ./bin/nstool -t meta /tmp/pz23-aci.npdm
HOME=/tmp/pz22-clean-home ./bin/nstool -v -t meta /tmp/pz23-acid.npdm
HOME=/tmp/pz22-clean-home ./bin/nstool -t kip /tmp/pz23-kip.kip
HOME=/tmp/pz22-clean-home ./bin/nstool -t aset /tmp/pz23-assets.bin
HOME=/tmp/pz22-clean-home ./bin/nstool -t nso --showlayout /tmp/pz23-nso.nso
```

## Regression tests and results

Added in-memory fixtures/tests for NSO module name, rodata metadata, hash flags, EOM/ZBIC bit interpretation, header overlap and malformed ranges; NRO compressed metadata, NRA0 header, appended ASET section offsets, NACP size and overlap/bounds; KIP capability descriptor families and fixed header overlap; NPDM ACI/ACID SAC entries, server bit, KC descriptor families, complete ACID prefix, section overlap and invalid declared size. Fixtures are synthetic tests, not HOS evidence.

Commands run:

```sh
../.venv/bin/python -m unittest discover -s tests/workspace-tests -p 'test_switch_artifact_inspector.py' -v
../.venv/bin/python -m py_compile scripts/inspect_switch_artifact.py tests/workspace-tests/test_switch_artifact_inspector.py
../.venv/bin/python -m unittest discover -s tests/workspace-tests -v
../.venv/bin/python -m unittest discover -s lab/tests -v
../.venv/bin/python tools/phase14-mtp/test_validate_phase14.py
git diff --check
```

Results: format-inspector suite **20 passed**; full workspace suite **33 passed**; lab suite **11 passed**; Phase 14 validator **6 passed**; Python compile check passed; `git diff --check` passed. Total across test suites: **50 passed**. The synthetic lab tests are not Switch evidence.

## Limits / research impact

- No HOS 23.0.1 WebApplet NSO, matching NPDM, BrowserDll/SystemData, or build identity was found. No HOS reverse engineering or vulnerability claim was made.
- The parser reports metadata and structural validity only. It does not decompress NSO LZ4/ZBIC, NRO compression, or KIP BLZ; verify segment hashes or ACID RSA signatures; decode FAC permissions; model loader policy; or execute analyzed files.
- NSTool v1.9.2 is an independent public implementation, but predates recent format fields and itself has unsupported paths. Agreement on a synthetic fixture or our own homebrew binary is not proof of full format compliance.
- The Phase 23 code improves pre-analysis triage and makes metadata boundaries visible. It does not change the feasibility of reaching stock Mariko/HOS 23.0.1.

## References

| Source | Date/type | Confidence and use |
|---|---|---|
| https://github.com/jakcron/nstool/tree/stable | Public OSS source, MIT; exact local source commit listed above, accessed 2026-10-31 | High for inspected implementation behavior; limited by version and its own stubs. |
| https://github.com/jakcron/nstool/blob/stable/deps/libpietendo/include/pietendo/hac/define/aci.h | Public NSTool dependency header, accessed 2026-10-31 | High for checked-out packed ACID/ACI structure sizes and field placement. |
| https://github.com/jakcron/nstool/blob/stable/deps/libpietendo/src/hac/KernelCapabilityControl.cpp | Public NSTool dependency implementation, accessed 2026-10-31 | High for the tested descriptor type dispatch; not a Nintendo specification. |
| https://switchbrew.org/wiki/NSO | Community format documentation, accessed 2026-10-31 | Medium; flags, segment header and metadata reference. |
| https://switchbrew.org/wiki/NRO | Community format documentation, accessed 2026-10-31 | Medium; NRO fields, 23.0+ compression flag, NRA0 and ASET layout. |
| https://switchbrew.org/wiki/KIP1 | Community format documentation, accessed 2026-10-31 | Medium; KIP header/capability area and BLZ note. |
| https://switchbrew.org/wiki/NPDM | Community format documentation, accessed 2026-10-31 | Medium; META/ACI/ACID/SAC/KC structure reference, with noted ThreadInfo bit-field disagreement. |
| https://switchbrew.org/wiki/NACP | Community format documentation, accessed 2026-10-31 | Medium; fixed-size application-control property section used to validate ASET geometry. |
