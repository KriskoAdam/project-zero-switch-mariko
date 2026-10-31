# PROJECT ZERO — Phase 10: GO / NO-GO

## Decision: NO-GO for target system analysis

**The project must wait for a new eligible target artifact or reproducible public result.** The local inventory contains zero HOS/BootROM/stock-app binaries. The only corresponding AArch64 object is `libsysbase_dirent.o` from the SDK/runtime distribution; it's not a Nintendo code. The public libnx sources and synthetic PROJECT_ZERO tests do not replace the HOS executable.

## Status of analytical tools

- **Ghidra 12.1.4** is installed locally, with AArch64 analysis; was used on the ELF64 AArch64 object, not on the HOS.
- **REA 6.8.0** is available in the Codex session. `open_binary` worked with an ELF object. REA firmware region analysis/extraction on this macOS was marked `unsupported_host` in the existing registry; REA does not offer a container loader in the current HOS configuration.
- **Capstone, LIEF, pyelftools and Construct** are in `.venv`. The inventory test confirmed that they can work with regular ARM64/ELF code or as a general design library; they do not open encrypted Nintendo containers themselves.
- **Switch container tools** such as `hactool`, `hactoolnet`, `hacpack`, `nstool` and `ninfs` were not found in PATH or local `tools/` inventory. Additionally, installing or using a decryption/extraction tool would not be within the currently permitted scope.
- **Python package versions differ between distribution metadata and import module:** pip metadata reports Capstone 5.0.9 and LIEF 1.0.0; runtime `__version__` reports Capstone 5.0.7 and LIEF `1.0.0-d05b3499b` in this process. Both were successfully imported and used on the available ELF object. This contradiction must be resolved only with the next real target artifact; we are not installing anything duplicate now.

## Conditions for reopening

Proceed only after receiving the minimum eligible package described in [artifact requirements](PHASE10_ARTIFACT_REQUIREMENTS.md): unchanged unencrypted stock executable, HOS 23.0.1 build identity, trusted hash/origin, and associated permissions/IPC metadata. Or after publishing a new public result that is reproducible and explicitly covers Mariko/T210B01 and HOS 23.0.1.

Until such an input exists, **do not create a synthetic replacement for Nintendo code and do not start further experiments**. Phase 7/8 SDK findings remain in history but do not change this gate.
