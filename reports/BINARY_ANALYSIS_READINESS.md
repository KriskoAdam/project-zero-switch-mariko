# Readiness for binary analysis

## Proven skills

- Ghidra 12.1.4, JDK 25, analyzeHeadless and native ARM64 decompiler were verified; build of native components passed.
- REA 6.8.0 MCP replies in Codex conversation; Codex registration is aligned.
- Python venv imports Capstone 5.0.9, pyelftools 0.33, LIEF 1.0.0 and Construct 2.10.70; pip check without bad requests.
- Utilities generate SHA-256 manifest, read ELF/Mach-O/PE metadata via LIEF, disassemble limited ARM64 executable segments via Capstone and compare manifests.

## What was actually analyzed

- Synthetic ARM64 Mach-O fixture created locally via Apple Clang; the script identified ARM64 and decoded 5 instructions.
- Local /usr/bin/true used for metadata parser; detected by Mach-O x86_64.
- SHA-256 manifest of local scripts; comparing the manifest with itself gave an empty diff.
- Unit tests: 6/6 passed.
- Ghidra headless --help startup printed usage; was not opening the target file.

## What was not analyzed

- HOS 23.0.1, Mariko Boot ROM, firmware partitions or Nintendo system modules.
- There is no legal target artifact supplied. Keys were not obtained; decryption, unpacking and target execution did not take place.
- REA firmware provider on macOS returns unsupported_host; REA documentation requires Linux and external Binwalk/Unblob.
- The active REA server was started before adding JAVA_HOME and GHIDRA_INSTALL_DIR. CLI doctor confirmed provider checks with these routes; a live MCP session will need a Codex restart.

Examples and limits are in [scripts/README.md](../scripts/README.md). Sensitive names, firmware and keys are ignored by default in manifests and Gite.

