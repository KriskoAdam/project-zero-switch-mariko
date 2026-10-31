# Host-side scripts

These scripts inspect local manifests and legally available host-side artifacts. They do not communicate with a Switch or acquire firmware/keys. Run Python tools with the project's isolated environment after installing `requirements.txt`. `create_sha256_manifest.py` excludes sensitive file classes; inspect outputs before publishing. The host-environment setup helpers are in `tools/host-scripts/`.
