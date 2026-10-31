#!/bin/sh
# Optional helper: set the repository root and add locally available tools.
RESEARCH_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
export RESEARCH_ROOT
if [ -n "${JAVA_HOME:-}" ] && [ -d "$JAVA_HOME/bin" ]; then PATH="$JAVA_HOME/bin:$PATH"; fi
export PATH
printf 'Research root: %s\n' "$RESEARCH_ROOT"
printf 'Optional Ghidra path: set GHIDRA_INSTALL_DIR if installed locally.\n'
