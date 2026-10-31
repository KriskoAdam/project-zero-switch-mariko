# PROJECT ZERO — Phase 9: audit of available artifacts

## Inventory for the target platform

Repeated local inventory in `switch-research` found **0 Nintendo target files** with extensions `.nso`, `.nro`, `.kip`, `.nca`, `.xci`, `.romfs`, `.nsp`, `.kip1` or `.kip2` (with the exception of unrelated Ghidra preview/build files that were excluded from the target artifact inventory). There is no BootROM/IROM dump, HOS kernel, system module, stock application or WebKit binary.

| Local artifact | Identity | What | enables What | does not
|---|---|---|---|
| `references/vendor/libnx_fs_dev.c` | Project source lists libnx commit `b156b4774fb2df7b93402169509266da7547fc4c`; SHA-256 `6a0138df373ffca4d1237854b5a3cd24742fc4ee696a122c4daeae2cf83ca2b4` | Read the public libnx implementation and test it on the guest. | Code in stock HOS/title, console vulnerability or Mariko compatibility. |
| `references/vendor/libnx_fs.h` | SHA-256 `670740e6228674a0bb9d2cb1d4230a230d6cc867f423a68df827c083d4f24504` | SDK public data types/constants. | Implementation of HOS filesystem service. |
| `references/vendor/devkita64-newlib-4.6.0.20260123-4/libsysbase_dirent.c` and related headers | `NAME_MAX=255`, callback contract; content from devkitA64 distribution | Parse newlib/devkitPro runtime calls. | That a specific retail application or HOS uses this version. The package did not have a verifiable signature; provenance is conditional in Phase 7 records. |
| `libsysbase_dirent.o` | ELF64 AArch64 relocatable, SHA-256 `4b3b4fdb38ef370402120d9964d39f2b487e9c34ce1bf250c39eb3eb767fd7de` | Ghidra/REA decompilation of one library object unit. | Nintendo system module or HOS 23.0.1 code. |
| `PROJECT_ZERO/` | Local Python models, oracle, seeded synthetic tests and their JSON/SQLite results | Validate framework on predefined model errors. | Real behavior of Nintendo services or fuzzing target binaries. |
| Phase 7/8 harnesses | Extract public libnx/newlib source bodies and host shims, ASan/UBSan | Reproduce the exact properties of a given source in a constrained host model. | Target build, HOS syscall/IPC, mariko CPU/firmware behavior. |

## Functionality of the analytical environment

- **REA 6.8.0** is available in this Codex link. **Ghidra 12.1.4** via REA successfully opened and analyzed the above AArch64 ELF object. Dossier `seekdir` only confirmed the behavior of this newlib object unit; REA did not analyze VOC.
- **pyelftools 0.33** confirmed by ELF64, `EM_AARCH64`, `ET_REL`. **LIEF 1.0.0-d05b3499b** recognized `ARCH.AARCH64`, `FILE_TYPE.REL` and 26 sections. **Capstone 5.0.7** decoded 301 instructions from executable `.text.*` sections; the first attempt at the standard `.text` section found nothing because this object uses named sections after functions. This is an SDK/runtime object analysis, not Nintendo code.
- **Python 3.14.7** in `.venv` imports Capstone **5.0.7**, LIEF **1.0.0-d05b3499b**, pyelftools **0.33** and Construct **2.10.70**. Project tests of tools passed in this virtual environment.
- **Apple Clang 21.0.0** performs host ASan/UBSan tests. LibFuzzer runtime for macOS is missing on this machine; Phase 8 therefore used seeded mutations, not coverage-guided fuzzing.
- REA firmware analysis on macOS was marked `unsupported_host` in the previous environment report; in any case, the input HOS artifact is missing.

## What is needed for a meaningful analysis of HOS 23.0.1

A **specific, legally shareable and unaltered stock HOS 23.0.1 executable artifact** with a trusted origin would have the most informational value: for example, a specific system module or stock applet from a build, with a published/verifiable hash or provided by an authorized researcher. It requires metadata that identifies the HOS build, title/module name, architecture, version, integrity, and documented permissions/IPC access.

If only the SDK source is analyzed, the result remains at the level of the declared API. If only the encrypted firmware container is analyzed, the code will not be verified without a legitimately obtained decrypted artifact. **We do not request or obtain console keys, pull firmware, or use a console dump.** Unless Nintendo/author of authorized research provides a usable artifact, further binary analysis of the target platform is not possible within the current boundaries.

## Proof limit

There is evidence in the tree for the public libnx/newlib source and one SDK/runtime ELF object. There is no proof for the Nintendo code. Therefore, all claims about Mariko/HOS 23.0.1 in the reachability map are tied to previous public documentation reports; the benchmark analysis of HOS binaries and the target runtime test did not take place locally.
