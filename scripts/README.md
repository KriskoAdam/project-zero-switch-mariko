# Host-side scripts

These scripts inspect local manifests and legally available host-side artifacts. They do not communicate with a Switch or acquire firmware/keys. Run Python tools with the project's isolated environment after installing `requirements.txt`. `create_sha256_manifest.py` excludes sensitive file classes; inspect outputs before publishing. The host-environment setup helpers are in `tools/host-scripts/`.

`inspect_switch_artifact.py INPUT` emits JSON with a SHA-256 and bounded structural checks for NSO, NRO, KIP1, NPDM and ELF. `--disassemble` forwards supported AArch64 ELF inputs to `inspect_arm64_binary.py`; Switch-format payloads are not decompressed or disassembled. `--synthetic` is only a provenance label for test fixtures. The parser's documented limits and reproduction commands are in `reports/PHASE19_HOS_ARTIFACT_READINESS.md`.
