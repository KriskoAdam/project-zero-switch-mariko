# Phase 6 — analysis of public implementation

## Selected destination

The translation of the name of the directory entry in the **libnx** public library, namely `fsdev_convertfromfspath()` and its use in `fsdev_dirnext()`, is analyzed. It's real source code for homebrew on Nintendo Switch, not a Nintendo/Horizon OS implementation. The target was chosen because the helper, its caller, and the data structure `FsDirectoryEntry` are publicly available.

Upstream: [switchbrew/libnx](https://github.com/switchbrew/libnx), commit `b156b4774fb2df7b93402169509266da7547fc4c`, commit date 2026-10-19. Exact references: [helper](https://github.com/switchbrew/libnx/blob/b156b4774fb2df7b93402169509266da7547fc4c/nx/source/runtime/devices/fs_dev.c#L250-L257), [calling path and length check](https://github.com/switchbrew/libnx/blob/b156b4774fb2df7b93402169509266da7547fc4c/nx/source/runtime/devices/fs_dev.c#L1451-L1485), [FsDirectoryEntry](https://github.com/switchbrew/libnx/blob/b156b4774fb2df7b93402169509266da7547fc4c/nx/include/switch/services/fs.h#L58-L66).

## Contract and state flow

1. `fsdev_dirnext()` loads the entry into `FsDirectoryEntry` and selects the name `entry->name`.
2. The caller zeroes out the first `NAME_MAX` bytes of the destination `filename`.
3. `fsdev_convertfromfspath()` calculates the length via `strnlen(input, NAME_MAX)`, copies the bytes, and writes NUL to position `inlen + 1` if the input is shorter.
4. The caller returns `EILSEQ` for a negative length; at `units >= NAME_MAX` return `ENAMETOOLONG`; otherwise success.

Observable boundary behavior from the source code: at most `NAME_MAX-1` bytes without a preceding NUL continue as a successful name; exactly `NAME_MAX` bytes without NUL are copied by the helper and subsequently rejected by the caller. Helper does not validate UTF-8 itself: it copies bytes. The call comment talks about converting to UTF-8, but the upstream FS data encoding cannot be deduced from this function itself.

## Suspicion and result

Hypothesis: write `out[inlen+1]` can be off-by-one and corrupt memory at maximum name. In the checked harness, the exact helper from the pinned source file was tested, along with a destination buffer of size `NAME_MAX+1` and the same pre-zeroing as the caller does. For the longest received name (254 bytes at `NAME_MAX=255`), the record ends at index 255, which fits into the 256-byte buffer. An input of length 255 is rejected after the helper. Neither AddressSanitizer nor UndefinedBehaviorSanitizer showed an error in these cases.

**The hypothesis was not confirmed in the local 256-byte test buffer; the actual buffer size in the target ABI remains unverified.** `NAME_MAX=255` and buffer `NAME_MAX+1` are harness parameters, not values ​​derived from the pinned target newlib ABI. Since the `dirnext` callback only receives `char *filename` with no length, an upstream contract or the caller's newlib/libnx allocation path is required. Without this, OOB at index 255 cannot be confirmed or ruled out. Therefore, the test does not **reject** the hypothesis for real ABI; only rejects it for the explicitly constructed 256-byte case.

## Distinction of evidence

- **Source code:** pinned libnx implementation above.
- **Interface documentation:** public libnx headers define `FsDirectoryEntry` and public API; community [Switchbrew FS Services documentation](https://switchbrew.org/wiki/Filesystem_services) describes the Horizon interfaces. It's not Nintendo source code.
- **Own interpretation:** state flow and buffer boundary hypothesis.
- **Test:** host harness compiles exact helper body text; it doesn't run libnx on Switch or fsp-srv on Horizon.
- **Synthetic model:** not used.

The result is a reproducible feature of the tested public implementation, not a violation of the HOS contract and not a vulnerability discovery. This result is not carried over to HOS 23.0.1 or Mariko/T210B01.
