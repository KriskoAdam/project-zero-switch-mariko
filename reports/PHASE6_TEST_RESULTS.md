# Phase 6 — test results

## Tested object

The exact body of `fsdev_convertfromfspath()` is extracted at runtime from `references/vendor/libnx_fs_dev.c` by function name. The harness does the same zeroing of the first `NAME_MAX` bytes as `fsdev_dirnext()` in the source before the call. The helper is tested, not the entire libnx library or the Horizon service.

Source commit: `b156b4774fb2df7b93402169509266da7547fc4c` (2026-10-19). SHA-256 source: `6a0138df373ffca4d1237854b5a3cd24742fc4ee696a122c4daeae2cf83ca2b4`. Harness: `scripts/phase6_fs_name_test.py`, SHA-256 `8bffb6c7d66c345c48929fbeba94d89fd36b8f274ffd552ccffd92d5f967a7ee`.

## Reproduction

In the root folder `switch-research`:

```sh
python3 scripts/phase6_fs_name_test.py
```

The script creates a temporary C harness, extracts the exact function body, compiles it with system Apple Clang with `-fsanitize=address,undefined`, and runs it. Environment used: Apple Clang 21.0.0; `NAME_MAX=255` is an explicit value used to simulate the target newlib interface.

## Run result

```text
PASS empty (result=0)
PASS ascii (result=6)
PASS UTF-8 bytes copied (result=3)
PASS largest accepted length (result=254)
PASS helper returns NAME_MAX for unterminated NAME_MAX input (result=255)
SOURCE_SHA256 6a0138df373ffca4d1237854b5a3cd24742fc4ee696a122c4daeae2cf83ca2b4
SOURCE references/vendor/libnx_fs_dev.c
```

ASan/UBSan did not issue diagnostics. The last test directly tests only the helper; does not call or simulate branch `units >= NAME_MAX` in `fsdev_dirnext()`. `NAME_MAX=255` and the 256-byte output buffer are explicit harness parameters, not values ​​derived from the pinned target newlib ABI. Helper writes the index 255 when the received length is 254. Without confirming the actual buffer capacity of the caller, it is not possible to decide from this run whether it is an OOB on the target.

## Interpretation

The test reproduced the byte copying and resulting helper lengths. The suspected OOB did not show up in the local 256 byte buffer, but for the actual target caller the ABI remains **undecided**. `filename` allocation contract, filesystem response, service error code, ARM64 build or console run failed to verify. It is not a test of HOS 23.0.1.
