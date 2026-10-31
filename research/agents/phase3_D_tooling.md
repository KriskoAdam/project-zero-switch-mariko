# Agent D — REA and Ghidra: Independent Readiness Check

## Observed results

- Host: macOS 27.0.1, arm64. `scripts/check_environment.sh` successfully reported Git 2.54.0, Python 3.14.7, Node 24.22.2 (LTS codename Krypton), Apple Clang 21.0.0, CMake 4.4.5, Ninja 1.13.2, LLVM 23.1.4, pkg-config 3.0.10, OpenJDK 25.0.5.0.3, and Ghidra 12.1.4.
- `.venv` contains capstone 5.0.9, pyelftools 0.33, lief 1.0.0, and construct 2.10.70. `pip check` reports “No broken requirements found.”
- `analyzeHeadless` is executable. `Ghidra/Features/Decompiler/build/os/mac_arm_64/decompile` is a Mach-O arm64 binary, produced by a successful native build. The `analyzeHeadless --help` check displayed usage; it did not import or run a target.
- The live REA MCP `binary_session` responded: server 6.8.0, no target open, Ghidra provider `available`, and no failed checks. This is a direct observation of the active session after restarting the server; it does not establish analysis of a Switch artifact.
- The REA CLI doctor previously confirmed Codex registration `aligned`, 49 aligned skills, Ghidra 12.1.4/JDK 25, and arm64 platform. Doctor reports `environment_healthy=false` because of other optional providers and registrations for other clients; this does not mean the relevant Ghidra provider failed.
- `npx rea-agents@latest` could not be downloaded during Phase 2 because DNS returned `ENOTFOUND`; the already configured REA 6.8.0 is in use. It was not reinstalled here.

## Primary technical sources

- NSA Ghidra Getting Started: https://github.com/NationalSecurityAgency/ghidra/blob/master/GhidraDocs/GettingStarted.md — macOS, Java requirements, and the `buildNatives` procedure for native components.
- NSA Ghidra release 12.1.4: https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build — official SHA-256 `ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db`, matching the local archive used for installation.
- REA firmware workflow: https://github.com/morluto/rea/blob/main/docs/firmware-analysis.md — the firmware-region workflow is verified on Linux x64; it requires caller-provided Binwalk 3.1.x or Unblob 26.6.x and `prlimit`. The active REA inventory on macOS reports it as `unsupported_host`.

## Scope and evidence quality

Ghidra/REA are ready for supported, user-supplied static binary targets. The project contains no target HOS 23.0.1 artifact, and no Switch firmware analysis was performed. Therefore, no claim can be made that architecture, symbols, 23.0.0→23.0.1 changes, or Mariko binary contents were measured. Without an artifact, there is no REA evidence ID for the console.

Evidence for installation and versions: high confidence, based on local commands and program launch. Evidence for REA Ghidra provider availability: high confidence for the current server inventory. The conclusion that the REA firmware workflow does not support this host is based on its capability remediation and documentation. None of these observations is evidence of a vulnerability or Mariko/HOS 23.0.1 exploitability.

## Open questions

1. Which legally obtained, trusted, user-supplied ARM64 HOS 23.0.1 binaries can be analyzed without keys or decryption? None have been supplied so far.
2. REA's firmware-container analysis requires a separately supported host (for example, Linux x64 according to its documentation); that workflow was not evaluated here.
3. Static analysis of an individual binary can inventory code, but cannot by itself establish runtime exploitability, a successful chain, or compatibility with the exact Switch V2 unit.
