# PROJECT ZERO — Phase 8 experimental result

## The result in a nutshell

The new reproducible finding is **silent path shortening in libnx `fsdev_getfspath()`**. With a destination constant of `FS_MAX_PATH=769`, the function copies up to 768 bytes of content, NUL pads it, and returns `0`. The shortest input where the output no longer equals the input is 769 bytes. Test found entry `"/" + "A"*768`; after calling it got a successful result with 768 bytes.

It's **libnx public library behavior**, not proof of a Horizon OS bug. The code is executed in an application that already uses libnx; therefore it requires homebrew already running and **does not provide a first entry point**. The available evidence does not show a link with Mariko/T210B01 or HOS 23.0.1. The result does not change the estimate of the possibility to obtain the first homebrew input by software.

## Exact classification of the find

- **A — requires homebrew already running:** yes. `fsdev_getfspath()` is a library function that executes in a process using libnx.
- **B — layer:** libnx/SDK library. We have found no evidence that this is a fault of the Nintendo system itself.
- **C — Mariko/HOS 23.0.1:** unproven. The source is a public libnx implementation; the test runs on macOS and does not use the console or HOS artifacts.
- **D — confirmation without protection bypass:** yes, by source test on host. We do not claim an impact on the target system.
- **Safety range:** so far only mismatch/correctness problem during long journeys. Out-of-bounds logging, information leakage, privilege escalation, and HOS impacting are not demonstrated. Callers typically pass fixed `FS_MAX_PATH` output fields, so the specific calling case and effect on the filesystem operation must be demonstrated before a security impact can be attributed.

## Source proof and reproduction

The project source file lists libnx commit `b156b4774fb2df7b93402169509266da7547fc4c`, SHA-256 `6a0138df373ffca4d1237854b5a3cd24742fc4ee696a122c4daeae2cf83ca2b4`. In `references/vendor/libnx_fs_dev.c`:

- `fsdev_fixpath()` accepts a normalized path to `__nx_dev_path_buf[PATH_MAX+1]`, checking the `PATH_MAX` boundary (lines 150–232).
- `fsdev_getfspath()` propagates `fsdev_fixpath()` failure, otherwise copies `FS_MAX_PATH-1` bytes and sets the last byte of the target to NUL, then returns success (lines 235–247).
- `FS_MAX_PATH` is `0x301`, so 769, in `references/vendor/libnx_fs.h`.
- The public declaration `fsdevTranslatePath()` in `references/vendor/libnx_fs_dev.h:76–77` documents the output buffer as `FS_MAX_PATH` bytes. Therefore, the call actually has a 769-byte ABI buffer, while retaining at most 768 bytes of data plus NUL.

The reproduction script extracts the exact body `fsdev_getfspath()` from the source file and derives `FS_MAX_PATH` and `PATH_MAX` from the vended target headers; it also writes their hashes. The stub for `fsdev_fixpath()` only accepts and copies input; it does not **validate nor normalize** itself. Therefore, the experiment isolates the target copy and **does not verify** the UTF-8 parser, device prefix, device lookup, or CWD folding. Longitudinal sweep uses absolute paths with ASCII `A`; the second campaign makes 10,000 seeded content/length changes (`0x50484138`), not all of which would pass real validation (eg some contain a colon). Both parts run with ASan and UBSan. The shortest sweep mismatch is 769 bytes.

Starting from the root of the project:

```sh
python3 scripts/phase8_path_truncation_test.py
```

Expected output:

```text
first_successful_truncation_input=769 output_bytes=768 return=0
max_swept_input=1023 destination_capacity=769
seeded_mutations=10000 seed=0x50484138
PASS ASan/UBSan; result=PROJECT_ZERO/results/phase8_path_truncation.json
```

Harness: `scripts/phase8_path_truncation_test.py`. Machine record: `PROJECT_ZERO/results/phase8_path_truncation.json`. The campaign also writes failure/crash output to the same JSON file. Apple Clang's full libFuzzer runtime library is missing on this guest (`libclang_rt.fuzzer_osx.a`), so reproducible sweep and seeded mutations were used instead of coverage-guided libFuzzer.

## Proven analytical tools

- REA responded and opened `libsysbase_dirent.o`; detected architecture is AArch64/ARM64, SHA-256 `4b3b4fdb38ef370402120d9964d39f2b487e9c34ce1bf250c39eb3eb767fd7de`.
- Ghidra 12.1.4 via REA parsed symbols including `seekdir`. Decompiling `seekdir` from the object shows a local field of 256 bytes and calling `__dirnext(..., 0)` for the stat pointer. This independently confirms the object code of the older Phase 7 trace, not the new Mariko/HOS find. REA analysis was closed.
- Host Apple clang 21.0.0 supports ASan/UBSan. LibFuzzer linking failed because the Clang runtime library is missing.
- Capstone 5.0.7, LIEF 1.0.0-d05b3499b, pyelftools 0.33 and Construct 2.10.70 are available in `.venv`. Using `.venv/bin/python -m unittest discover -s tests -v` passed 6/6 tests. `python3 -m unittest discover -s PROJECT_ZERO/tests -v` passed 11/11 synthetic tests. System `python3` does not have Capstone/LIEF; project reversal tools must be run with `.venv/bin/python`.

## Independent verification and remaining limits

The skeptic also independently ran the final version of the script and confirmed all 10,000 mutations, ASan/UBSan and the result 769→768 with a return of 0. He confirmed that the script derives `FS_MAX_PATH` and `PATH_MAX` from the target headers and stores their hashes. He pointed out the stub not validating the real resolver/UTF-8/device/cwd and that the mutated inputs might not all be valid under the real resolver. Its result: a reproducible library correctness anomaly, not standalone evidence of vulnerability or relevance to the first entry point.

Hash of headers in the record: `libnx_fs.h` — `670740e6228674a0bb9d2cb1d4230a230d6cc867f423a68df827c083d4f24504`; newlib `sys/syslimits.h` — `e041fa4ea0dbef6e8bd41856b85f4bb5e85c5d5867ba21063763c6f68f77bdc7`.

## Termination criterion


The specific next call site to check correctness is `fsdev_rename()` (`libnx_fs_dev.c:1275–1289`): the old path goes to the local `char fs_path_old[FS_MAX_PATH]`, the new path to the internal TLS buffer. This is not yet proof of a bug or a security effect; one must first verify whether the long path will pass through the real resolver and what the HOS filesystem operation with a 768-byte prefix will do. This trail should only be investigated further if such concrete evidence arises.

This track is closed for Phase 8 after: (1) a stable iteration of the boundary and 10,000 seeded cases without ASan/UBSan error, (2) an independent iteration by the Skeptic, and (3) confirmation that the entire experiment did not show a connection to the first entry point. Further work on this truncation only makes sense for a specific call site that uses a longer path, assumes full output, and exhibits a security impact.
