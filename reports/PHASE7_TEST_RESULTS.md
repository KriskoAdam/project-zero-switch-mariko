# Phase 7 — reproducible test results

## Environment

- Host: macOS Apple Silicon.
- Compiler: Apple clang 21.0.0 (`clang-2100.3.34.2`), target `arm64-apple-darwin27.0.0`.
- Python: 3.14.7.
- Command: `python3 scripts/phase7_fs_abi_test.py` from root `switch-research`.
- Sanitizers: `-fsanitize=address,undefined`; build with `-Wall -Wextra -Werror`.

## Method

Harness loads a local copy of the pinned libnx source and extracts the exact helper, `stat` padding block, and name conversion block. Extracts the exact implementations of `__dirnext`, `readdir_r` and `seekdir` from the public devkitA64/newlib source distribution. It compiles them with the target ABI header `sys/dirent.h` and small host shim declarations for `_reent`/devoptab. This tests the call flow including the reset, callback, return code and result record, not just the isolated body of the helper.

The input `FsDirectoryEntry` is supplied as a controlled test object; it is not obtained from the console or proprietary firmware. `struct stat` host and shim types are not full implementations of target libc. The test therefore documents indexing and the source callback contract, not the identical behavior of the entire target system.

## Output

```text
PASS empty (callback capacity=256 rc=0 errno=0)
PASS short ASCII (callback capacity=256 rc=0 errno=0)
PASS multibyte UTF-8 bytes (callback capacity=256 rc=0 errno=0)
PASS NAME_MAX - 2 (callback capacity=256 rc=0 errno=0)
PASS NAME_MAX - 1 (callback capacity=256 rc=0 errno=0)
PASS NAME_MAX terminated input rejected by callback (callback capacity=256 rc=63 errno=63)
PASS no NUL in helper input bound (callback capacity=256 rc=63 errno=63)
REPRODUCED seekdir NULL filestat dereference (child_rc=-6; AddressSanitizer:DEADLYSIGNAL)
ABI NAME_MAX=255; d_name capacity=256; FS_MAX_PATH=769
```

Number `63` is host value `ENAMETOOLONG`; the report does not transfer this number to the target ABI. Test cases NAME_MAX and non-NULL confirm rejection by callback, not successful write of index 256: helper gets length 255 and terminator adds only when `inlen < len`.

ASan thread `seekdir` ended with signal (`-6`) with ASan diagnostics. The exact diagnostic text may vary between runs. UBSan/ASan did not find an overflow in seven instances of `readdir_r`, including the longest successfully received name.

## End of test

With a resource-documented 256-byte buffer, the write to index 255 is in range. Seven contract tests passed. A separate `seekdir` path detected a null dereference in the resource combination examined. The test is hosted; an ARM64 console build was not created and validation was not performed on the Switch.
