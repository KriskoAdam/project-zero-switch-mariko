# Phase 6 — register of evidence

## Classification

Scale used from `PROJECT_ZERO/README.md`: E0 = hypothesis; E1/E2 = previous results of synthetic models; E3+ requires a named public or legally delivered artifact and an analysis bound to its hash. Therefore, Phase 6 marks the **E3 result for the pinned public libnx helper feature on the host harness-e**, not E3 for Nintendo. There is no E4 evidence for Horizon/Mariko.

## Resources

| URL | Date / Version | Evidence Type | Trust and Scope |
|---|---|---|---|
| https://github.com/switchbrew/libnx/tree/b156b4774fb2df7b93402169509266da7547fc4c | commit `b156b4774fb2df7b93402169509266da7547fc4c`, 2026-10-19 | Public source, pinned commit | High for the exact contents of this commit; it is not a Nintendo implementation of |
| https://github.com/switchbrew/libnx/blob/b156b4774fb2df7b93402169509266da7547fc4c/nx/source/runtime/devices/fs_dev.c#L250-L257 | same version | Helper source code | High for helper logic |
| https://github.com/switchbrew/libnx/blob/b156b4774fb2df7b93402169509266da7547fc4c/nx/source/runtime/devices/fs_dev.c#L1451-L1485 | same version | Caller and error branch source code | High for branches shown; not for caller buffer ABI |
| https://github.com/switchbrew/libnx/blob/b156b4774fb2df7b93402169509266da7547fc4c/nx/include/switch/services/fs.h#L58-L66 | same version | Public header/data structure | High for declared `FsDirectoryEntry`; does not exhibit HOS behavior |
| https://switchbrew.org/wiki/Filesystem_services | page checked 2026-10-30 | IPC Community Reverse-Engineering Documentation | Medium; useful for FS service map, not official spec or test of target FW |

## Local artifacts and integrity

| File | SHA-256 | Meaning |
|---|---|---|
| `references/vendor/libnx_fs_dev.c` | `6a0138df373ffca4d1237854b5a3cd24742fc4ee696a122c4daeae2cf83ca2b4` | Full upstream copy of the file from the specified commit |
| `references/vendor/LIBNX_LICENSE.md` | `5b6675f85016009624d29c9222201d3c0fc6a2d5c59253367f27d3e15011cdb2` | Upstream Source License |
| `scripts/phase6_fs_name_test.py` | `8bffb6c7d66c345c48929fbeba94d89fd36b8f274ffd552ccffd92d5f967a7ee` | Reproduction test script |

## What the evidence does not support

Neither Nintendo source code nor HOS binaries were analyzed; a legal artifact from HOS 23.0.1 was not supplied; libnx build for target was not proven; not tested on Mariko/T210B01; no privilege boundary or exploitative impact was demonstrated. The result does not tell about Switch 2, Erista, HOS 23.0.1 or homebrew option.
