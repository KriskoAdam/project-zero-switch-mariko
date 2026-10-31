# Research lab environment

Control: macOS 27.0.1, Apple Silicon arm64. Installations performed via pre-existing Homebrew; nothing is installed by system pip.

## Initial status when checking before installation

| Tool | Before installing | Status |
|---|---|---|
| Homebrew | available: /opt/homebrew | preserved |
| Git | 2.54.0 (Apple Git) | maintained by |
| Python | 3.14.7 | maintained by |
| Node.js | 24.22.2 | preserved; npm 11.19.1 |
| Apple Clang | /usr/bin/clang | available via Xcode Command Line Tools |
| CMake, Ninja | not found | installed later |
| LLVM | not found | installed later |
| pkg-config/pkgconf | not found | installed later |
| Java | runtime not found | installed OpenJDK 25 |
| Ghidra | not found | installed from NSA verified release 12.1.4 |

Node.js 24 is left with no duplicate installation. The LTS status must be confirmed at the end of the setup with the node -p process.release.lts command.

## Python isolation

Virtual Environment: .venv/ in the root project. Packages are pinned in requirements.txt: capstone 5.0.9, pyelftools 0.33, lief 1.0.0, construct 2.10.70. After a successful installation, the exact pip freeze versions will be added here.

## REA and Codex agents

REA MCP tools are present in this Codex session. This verifies that Codex can call REA tools, not that every optional provider/engine is installed or functional. REA CLI doctor was run through npx but at the time of writing had not yet returned a result. No analysis of Switch binaries is performed without a legally obtained firmware artifact.

Codex subagent support was verified by creating five separate research tasks; each returned findings. The results are in agents/ and the summary is in reports/AGENT_FINDINGS.md.

## Tools after setup

Add after completing Homebrew installation: exact versions, paths, SHA-256 Homebrew bottles, JDK and Ghidra; confirm Ghidra start and javac/java version. Homebrew bottle checksums were checked by Homebrew during installation; the exact versions and resulting state are in the section below and in manifests/toolchain.json.


## Verified status after installation

- CMake 4.4.5; Ninja 1.13.2; LLVM 23.1.4; pkg-config/pkgconf 3.0.10.
- Apple Clang 21.0.0 remains the system compiler; LLVM is available via /opt/homebrew/opt/llvm/bin without global linking.
- OpenJDK 25.0.5.0.3; Ghidra 12.1.4 from official NSA release ZIP, SHA-256 verified: ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db.
- Ghidra native components for macOS arm64 have been successfully built by the official Gradle task buildNatives.
- Node 24.22.2 reports LTS codename Krypton; the second Node version was not installed.
- Outv: pip 26.2.2; capstone 5.0.9, pyelftools 0.33, lief 1.0.0, construct 2.10.70. pip check: no bad requests. Package import successful.
- REA 6.8.0 CLI doctor: Codex registration aligned, skill 49 aligned. With GHIDRA_INSTALL_DIR and JAVA_HOME all relevant Ghidra checks (12.1.4, arm64 decompiler, headless, JDK 25) passed.
- Doctor generally reports environment_healthy=false due to other optional providers (e.g. Hopper/IDA/JADX) and registrations of other clients; those are not needed for this task.
- The REA MCP server running in the current Codex session was started before the configuration change. His diagnostics still show Ghidra as unconfigured until Codex is restarted and the server loads the completed env variables. After reboot, binary_session must be checked again.
- REA firmware parser provider on macOS is missing: REA marks it as unsupported_host and asks for Linux + Binwalk/Unblob. No firmware was analyzed here.
- Installed versions and hashes are also in manifests/toolchain.json.

### Checking for actual imported versions at Phase 13

Checking again directly via `./.venv/bin/python` found that the runtime imports do not match the manifest and the section above: Capstone **5.0.7** (manifest/requirements states 5.0.9), LIEF **1.0.0-d05b3499b** (manifest states 1.0.0), pyelftools 0.33 and Construct 2.10.70. This is a noted environment mismatch; packages were not installed during this phase. Use `pip freeze` from the same `.venv` at the next environment setup review and fix the lock/manifest depending on whether the versions are intentionally pinned or just declared.

### Missing or out of range

- REA optional Hopper, IDA and JADX engines are not installed/configured; are not needed for ARM64 static analysis in this project.
- REA firmware regional parser/extractor has unsupported_host status on macOS; its documentation requires Linux and an external Binwalk/Unblob.
- npx rea-agents@latest failed to load from npm registry (DNS ENOTFOUND). Used existing REA 6.8.0 in Codex cache and active MCP server.
- Ghidra/Java are set in the existing Codex MCP env configuration, but the live server is loaded only after a Codex restart.
- A legally obtained HOS 23.0.1 artifact was not supplied; the target-specific analysis therefore remains unperformed.
