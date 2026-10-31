# PROJECT ZERO Phase 18 — ARM64 Disassembler Repair Validation

**Date:** 2026-10-31
**Sample:** adjacent workspace file `../PROJECT_ZERO/apps/PROJECT_ZERO/PROJECT_ZERO.elf` (PROJECT ZERO homebrew build; not Nintendo firmware)
**Required SHA-256:** `9798cc4c8c2089c859f372f2bc3edfbc23a0d3d32512ed086f2aea12f6aea3bd`
**Observed SHA-256:** `9798cc4c8c2089c859f372f2bc3edfbc23a0d3d32512ed086f2aea12f6aea3bd`

## Implementation

Updated `scripts/inspect_arm64_binary.py` to:

- Parse ELF64 little-endian AArch64 symbol tables with pyelftools and use executable-section `STT_FUNC` ranges.
- Infer a zero-sized `STT_FUNC` range only to the next function symbol in that section, or to the executable section end; mark the range as inferred.
- Validate section/segment membership and integer bounds. Skip and report malformed/out-of-section symbols.
- Merge overlapping symbol ranges, preserve their names/provenance, and decode each instruction address at most once.
- Follow control flow from function entries instead of linearly sweeping the entire executable segment. Direct unconditional/conditional branches are followed within the range; returns and indirect branches terminate the path. Direct calls continue at the return site and are not mistaken for in-function code.
- When an ELF entrypoint is not covered by an `STT_FUNC`, follow only its bounded control-flow path to the next function boundary or executable-region end. This output is explicitly marked `entrypoint-control-flow-heuristic`.
- Report the remaining file-backed executable bytes under `undecoded_executable_regions`, with an explicit note that they could be data, padding, unreachable code, or truncated by limits.
- Preserve the `--max-instructions`, `--max-bytes`, JSON output, read-only behavior, ELF/Mach-O inputs, and universal Mach-O handling. No linear sweep is performed for Mach-O; its entrypoint is analyzed heuristically.

### Important property of the supplied ELF

The sample's ELF symbol table identifies `_start` as **`STT_NOTYPE`, value `0`, size `0`**, not as `STT_FUNC`. No `STT_FUNC` range covers address `0x80`. A symbol-backed claim for `_start` would therefore be false. The repaired tool uses the ELF entrypoint and its direct branch target, reports that range as a heuristic, and separately uses actual `STT_FUNC` ranges for the functions that are present. This is the evidence-based way to reach `0x80` without hardcoding sample offsets or pretending a function symbol exists.

## Before / after

### Before

Command used in Phase 17:

```sh
../.venv/bin/python scripts/inspect_arm64_binary.py \
  ../PROJECT_ZERO/apps/PROJECT_ZERO/PROJECT_ZERO.elf --max-instructions 16
```

The old segment-linear decoder emitted:

```text
0x0: b #0x80
0x4: udf #0xf0
0x8: uaddwt z8.h, z26.h, z13.b
instruction_count: 3
```

The words at `0x4` and `0x8` are embedded data. The scan stopped before the actual code at `0x80`.

### After

Exact command:

```sh
../.venv/bin/python scripts/inspect_arm64_binary.py \
  ../PROJECT_ZERO/apps/PROJECT_ZERO/PROJECT_ZERO.elf \
  --max-instructions 32 --max-bytes 256
```

Selected output:

```text
sha256: 9798cc4c8c2089c859f372f2bc3edfbc23a0d3d32512ed086f2aea12f6aea3bd
entrypoint_range: name=_start start=0x0 end=0xe0 source=entrypoint-control-flow-heuristic
0x0:  b    #0x80
0x80: cmp  x0, #0
0x84: ccmn x1, #1, #4, ne
0x88: b.eq #0x90
0x8c: b    #0x13f1c
...
instruction_count: 32
 decoded_bytes: 128
instructions at 0x4 or 0x8: none
first undecoded range: [0x4, 0x80), 124 bytes
```

`0x80` is reached by following the branch encoded at the ELF entrypoint, not by skipping a fixed prefix. The output distinguishes the entrypoint heuristic from the actual symbol-backed ranges in JSON.

## Independent comparison

### Apple `objdump`

Command:

```sh
objdump -d ../PROJECT_ZERO/apps/PROJECT_ZERO/PROJECT_ZERO.elf > /tmp/pz18-objdump.txt
```

Exit code was `0`; Apple LLVM 21.0.0 identified `elf64-littleaarch64`. Selected output:

```text
0:  14000020  b 0x80 <_start+0x80>
4:  f0 00 00 00  .word 0x000000f0
8:  48 4f 4d 45  .word 0x454d4f48
c:  42 52 45 57  .word 0x57455242
80: f100001f  cmp x0, #0x0
84: ba411824  ccmn x1, #0x1, #0x4, ne
88: 54000040  b.eq 0x90 <_start+0x90>
```

Agreement: the branch and target instructions match the repaired output. `objdump` explicitly classifies the embedded words as `.word`; the repaired CFG traversal leaves them undecoded.

### Ghidra 12.1.4

A full automatic analysis was attempted with a 45-second per-file timeout. It reached DWARF analysis and timed out at 45 seconds; the log says analysis was **not completed**. Ghidra's process exit code was 0 despite the `ERROR REPORT`, so that exit code is not counted as a successful full analysis.

To compare the actual loader/disassembler without waiting for full DWARF analysis, Ghidra was run in import-only mode with a short post-script. Ghidra relocates this PIE image's `.text` to `0x100000`; normalize those addresses by subtracting the image base when comparing with the ELF-relative report.

Post-script used for this check:

```java
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;

public class PZ18Inspect extends GhidraScript {
    @Override protected void run() throws Exception {
        Address entry = currentProgram.getImageBase();
        DisassembleCommand command = new DisassembleCommand(entry, null, true);
        println("disassemble_success=" + command.applyTo(currentProgram, monitor));
        for (long offset : new long[] {0, 4, 8, 0x80, 0x84, 0x88}) {
            Address address = currentProgram.getImageBase().add(offset);
            Instruction i = currentProgram.getListing().getInstructionAt(address);
            println(String.format("%#x: %s", currentProgram.getImageBase().getOffset()+offset,
                i == null ? "<no instruction>" : i.toString()));
        }
    }
}
```

Command:

```sh
export JAVA_HOME=/opt/homebrew/opt/openjdk@25/libexec/openjdk.jdk/Contents/Home
export PATH="$JAVA_HOME/bin:$PATH"
export JAVA_TOOL_OPTIONS='-Duser.home=/tmp/pz18-ghidra-home'
../tools/ghidra_12.1.4_PUBLIC/support/analyzeHeadless \
  /tmp/pz18-ghidra-project PZ18GhidraCheck2 \
  -import ../PROJECT_ZERO/apps/PROJECT_ZERO/PROJECT_ZERO.elf \
  -noanalysis -overwrite -scriptPath /tmp -postScript PZ18Inspect.java
```

Observed output:

```text
.text start=00100000 end=0013bb4f execute=true
disassemble_success=true status=null
0x100000: b 0x00100080
0x100004: <no instruction>
0x100008: <no instruction>
0x100080: cmp x0,#0x0
0x100084: ccmn x1,#0x1,#0x4,ne
0x100088: b.eq 0x00100090
```

Agreement after normalizing the image base: Ghidra and the repaired script both identify the branch from offset `0` to `0x80`, leave offsets `4` and `8` as non-instructions, and decode the same code at offsets `0x80`–`0x88`. The textual immediate formatting differs, but the targets and operations agree. This confirms loader/disassembler agreement for these bytes only; Ghidra's full DWARF/auto-analysis run did not finish.

## Regression tests

Added `tests/workspace-tests/test_arm64_disassembler.py`. It builds small synthetic ELF fixtures locally; these fixtures are test inputs, not firmware. Coverage:

1. Embedded data within an executable segment is not decoded as part of `_start`; entry branch and target code remain visible.
2. Missing function symbols use only entrypoint-guided control flow and label the output heuristic.
3. Zero-sized function symbols receive a bounded inferred range.
4. Overlapping symbols are merged without duplicate instruction addresses.
5. Out-of-section/malformed function ranges are skipped and reported.
6. Instruction and byte limits are enforced.
7. Invalid ELF input raises a clean error.

Focused command and result:

```sh
../.venv/bin/python -m unittest -v tests/workspace-tests/test_arm64_disassembler.py
# Ran 7 tests — OK
```

All existing project tests were also run:

```sh
../.venv/bin/python -m unittest discover -s lab/tests -v
../.venv/bin/python -m unittest discover -s tests/workspace-tests -v
(cd tools/phase14-mtp && ../../../.venv/bin/python -m unittest -v test_validate_phase14.py)
```

Results: 11 lab tests + 13 workspace tests + 6 MTP validator tests = **30 passed**. `git diff --check` also passed.

## Limitations

- This validates behavior on one local homebrew ELF and small synthetic ELF fixtures. It does **not** establish Nintendo HOS, NSO, NRO, KIP, or Mariko compatibility.
- The supplied ELF does not mark `_start` as `STT_FUNC`; reaching `0x80` therefore uses the clearly labeled ELF-entrypoint CFG heuristic. The script does not fabricate a function symbol.
- Zero-sized function bounds inferred to the next function or section end are explicitly approximate. They are used only as bounded CFG regions and carry an inferred provenance label.
- CFG recovery only follows recognized direct ARM64 branch forms. Indirect control flow, jump tables, exception tables, literal-pool semantics, and code/data distinctions that are not represented by symbols or reachable control flow remain incomplete.
- Undecoded ranges may contain valid but unreachable code, data, padding, or code omitted by the requested limits.
- Full Ghidra auto-analysis timed out in DWARF processing; comparison used Ghidra's successful ELF import and direct disassembly command rather than completed auto-analysis.
