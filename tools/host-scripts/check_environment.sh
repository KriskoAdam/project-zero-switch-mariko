#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
printf 'Repository: %s\n' "$ROOT"
printf 'OS: '; uname -srm
printf 'Git: '; git --version
printf 'Python: '; python3 --version
for tool in node clang cmake ninja pkg-config; do
  if command -v "$tool" >/dev/null 2>&1; then printf '%s: %s\n' "$tool" "$("$tool" --version 2>&1 | head -n 1)"; else printf '%s: MISSING\n' "$tool"; fi
done
if command -v gh >/dev/null 2>&1; then gh --version | head -n 1; else echo 'GitHub CLI: optional, missing'; fi
if [ -n "${GHIDRA_INSTALL_DIR:-}" ] && [ -d "$GHIDRA_INSTALL_DIR" ]; then printf 'Ghidra: %s\n' "$GHIDRA_INSTALL_DIR"; else echo 'Ghidra: optional, not configured'; fi
