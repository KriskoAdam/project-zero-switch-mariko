# Phase 7 — independent skeptical audit

## The result of an independent audit

Agent Skeptic independently looked at the current harness and resources and restarted `scripts/phase7_fs_abi_test.py` himself. Confirmed seven successful boundary tests and ASan reproduction `seekdir` with zero `filestat`. His verdict: index 255 is within the 256-byte fields described by these sources; a particular null dereference is real in the studied combination of resources. However, it did not confirm the authenticity or match of the package with the target build.

## Control questions and already verifiable evidence

- **Is 256 derived from source?** Yes for controlled ABI versions: `libsysbase_dirent.c:147` declares `filename[NAME_MAX+1]`; `syslimits.h:43` defines `NAME_MAX=255`; `dirent.h:27` defines `d_name[NAME_MAX+1]`. Callback prototype without size is in `iosupport.h:56`.
- **Is the harness circular?** The capacity is not chosen by the harness author: the script reads the value from the pinned headers and verifies the existence of the exact declaration in the source implementation. `readdir_r`, `seekdir` and `__dirnext` are extracted from the respective source. The skeptic pointed out that the presence of `.o` is checked in the script, but does not prove that the object was built from the given C source. Disassembling an object supports the capacity, but does not authenticate the resource-object relationship.
- **Does ASan cover the right boundary?** Yes for the source call path tested: callback gets a 256 byte auto field, helper gets a 255 byte limit, longest name accepted is 254 bytes and its NUL is at index 255. Tests of length 255 and no NUL expect `ENAMETOOLONG`.
- **Is it the same interface/version?** The source libnx copy is marked by the previous stage as commit `b156b4774fb2df7b93402169509266da7547fc4c`; newlib/devkitPro source comes from public distribution devkita64-newlib `4.6.0.20260123-4`. The libnx pin was not committed to this working directory via local Git metadata, so the commit identity relies on the existing project record; SHA-256 are lower in the register.
- **Does the conclusion not exceed the evidence?** The conclusion is limited to source ABI and host reproduction. It does not infer console functionality, exploitability or HOS 23.0.1 reach.
- **Another callback problem?** `seekdir` provably casts `NULL` to `filestat`; the libnx block dereferences it. Harness reproduces ASan error. A skeptic independently confirmed this. The range remains conditional on matching the resources with the real linked build and the HOS/Mariko behavior is not derived from it.

## Provenance

The package from the public mirror did not have a signature available; its hash identifies the content, not the publisher. A skeptic independently pointed out that the original archive, pacman database record, signature manifest and signature are missing from the tree; the script checks for the presence of the object, not its proven binding to the resource. Therefore, this is a reliable parsing of the supplied source texts and host reproduction, but not a cryptographically authenticated devkitPro runtime or proof of the target binary build.
