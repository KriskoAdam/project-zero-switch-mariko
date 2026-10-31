# Phase 6 — independent skeptical review

## Control procedure

Independent Skeptic checked the source helper, harness and reports and ran himself:

```sh
.venv/bin/python scripts/phase6_fs_name_test.py
```

He confirmed that the script extracts and compiles the exact body of `fsdev_convertfromfspath()` from the pinned public source and that all five cases passed. This achievement only applies to the host harness on macOS.

## Found methodological limitations

1. The original name of one test claimed to verify caller rejection. However, the test only runs the helper and checks its return `NAME_MAX`; never calls the `units >= NAME_MAX` branch in `fsdev_dirnext()`. The title and result text have been corrected.
2. `NAME_MAX=255` and 256-byte output are specified by the harness, not derived from the pinned target newlib ABI. Helper also writes length 254 to index 255 upon input. Since the callback receives `char *` without length, the actual capacity must be documented by a separate upstream contract or call site.
3. Pre-zeroing in the harness is copied by the callsite. This correctly preserves the current usage context, but does not test the helper on its own without the caller precondition.
4. The UTF-8 case only verifies the copying of three bytes. It does not verify Unicode validation or conversion.
5. Oracle tests are explicit expected lengths and bytes. This is not a comparison with the independent Nintendo implementation.

## Modified conclusion after the audit

The host test did not show OOB in the 256 byte buffer. It does not determine whether the same write would overflow the destination buffer according to the actual newlib/libnx caller ABI; this hypothesis therefore remains open for target ABI. This is explicitly stated in `PHASE6_SOURCE_ANALYSIS.md` and `PHASE6_TEST_RESULTS.md`. The result does not belong to HOS or Mariko and does not provide proof of HOS 23.0.1.

## Proof level

E3 can only be used with the exact name **"pinned public libnx helper executed in host harness-e"**. This is not an E3 proof for the entire libnx runtime, HOS, Switch ABI, or target firmware. No E4/console evidence generated.
