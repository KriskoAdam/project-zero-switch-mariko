#!/usr/bin/env python3
"""Create a SHA-256 manifest for files already present on disk; never fetches files."""
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

EXCLUDED_PARTS = {'.venv', '.git', '__pycache__', 'samples'}
EXCLUDED_SUFFIXES = {'.nca', '.nsp', '.xci', '.keys', '.bin', '.dump', '.dmp', '.romfs', '.exefs', '.firmware', '.fw'}

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def iter_files(root: Path, include_sensitive: bool = False):
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in EXCLUDED_PARTS for part in rel.parts):
            continue
        if not include_sensitive and (path.suffix.lower() in EXCLUDED_SUFFIXES or 'serial' in path.name.lower()):
            continue
        yield path

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('-o', '--output', type=Path, required=True)
    p.add_argument('--include-sensitive', action='store_true', help='explicitly include normally excluded firmware/key suffixes')
    a = p.parse_args()
    root = a.root.resolve()
    if not root.is_dir():
        p.error(f'not a directory: {root}')
    rows=[]
    for path in iter_files(root, a.include_sensitive):
        rows.append({'path': str(path.relative_to(root)), 'size': path.stat().st_size, 'sha256': digest(path)})
    out={'schema_version':1,'created_utc':datetime.now(timezone.utc).isoformat(),'root':str(root),'files':rows}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2)+'\n')
    print(f'wrote {len(rows)} entries to {a.output}')
    return 0
if __name__ == '__main__': raise SystemExit(main())
