# Scripts

- check_environment.sh reports installed local tool versions and pinned Python packages.
- Do not put firmware acquisition, console access, payload execution, keys, or device-secret extraction into this project.


## Phase 3 analysis helpers

Run from the project root with `.venv/bin/python`:

- Create a SHA-256 manifest for an existing directory: `.venv/bin/python scripts/create_sha256_manifest.py references -o manifests/references.json`. Sensitive firmware, key, dump, binary and serial-named files are skipped by default. `--include-sensitive` is an explicit opt-in; do not use it for private/proprietary console material.
- Inspect metadata: `.venv/bin/python scripts/inspect_binary_metadata.py /path/to/lawful-binary -o reports/metadata.json`. Emits SHA-256, size, format, architectures, sections and symbols where LIEF supports them.
- Disassemble a bounded ARM64 executable segment: `.venv/bin/python scripts/inspect_arm64_binary.py /path/to/lawful-binary --max-instructions 10000 --max-bytes 4194304`. Static output only; limits bound reported work, not a full firmware parser.
- Compare two generated manifests: `.venv/bin/python scripts/compare_manifests.py manifests/before.json manifests/after.json`.
- Run unit tests: `.venv/bin/python -m unittest discover -s tests -v`.

All inspection is read-only with respect to input binaries. The scripts do not defeat encryption, unpack proprietary firmware, extract keys, execute the target, or access a console.
