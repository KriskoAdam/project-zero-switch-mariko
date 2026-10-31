#!/usr/bin/env python3
"""ASan/UBSan boundary sweep of the pinned libnx fsdev_getfspath source body."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "references/vendor/libnx_fs_dev.c"
OUTPUT = ROOT / "PROJECT_ZERO/results/phase8_path_truncation.json"
LIBNX_FS_HEADER = ROOT / "references/vendor/libnx_fs.h"
NEWLIB_LIMITS = ROOT / "references/vendor/devkita64-newlib-4.6.0.20260123-4/include/sys/syslimits.h"


def extract_function(source: str) -> str:
    match = re.search(r"static int\s+fsdev_getfspath\s*\([^)]*\)\s*\{", source)
    if not match:
        raise SystemExit("fsdev_getfspath source body not found")
    brace = source.find("{", match.start())
    depth = 0
    for pos in range(brace, len(source)):
        if source[pos] == "{":
            depth += 1
        elif source[pos] == "}":
            depth -= 1
            if depth == 0:
                return source[match.start():pos + 1]
    raise SystemExit("unterminated fsdev_getfspath source body")


def main() -> None:
    source_text = SOURCE.read_text()
    source_body = extract_function(source_text)
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    libnx_fs_text = LIBNX_FS_HEADER.read_text()
    newlib_limits_text = NEWLIB_LIMITS.read_text()
    fs_max_match = re.search(r"^#define\s+FS_MAX_PATH\s+0x([0-9a-fA-F]+)", libnx_fs_text, re.M)
    path_max_match = re.search(r"^#define\s+PATH_MAX\s+(\d+)", newlib_limits_text, re.M)
    if not fs_max_match or not path_max_match:
        raise SystemExit("could not derive path bounds from vendored target headers")
    fs_max_path = int(fs_max_match.group(1), 16)
    path_max = int(path_max_match.group(1))
    harness = f'''#include <errno.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define PATH_MAX {path_max}
#define FS_MAX_PATH {fs_max_path}
struct _reent {{ int _errno; }};
typedef struct {{ int placeholder; }} fsdev_fsdevice;
static char __nx_dev_path_buf[PATH_MAX+1];
static struct _reent test_reent;
static const char *fsdev_fixpath(struct _reent *r, const char *path, fsdev_fsdevice **device) {{
  (void)r; (void)device;
  /* Valid, normalized absolute ASCII paths; mirrors fixpath's bounded storage.
     Boundary test deliberately isolates the exact getfspath body under test. */
  size_t n = strnlen(path, PATH_MAX+1);
  if (n > PATH_MAX) {{ r->_errno = ENAMETOOLONG; return NULL; }}
  memcpy(__nx_dev_path_buf, path, n);
  __nx_dev_path_buf[n] = 0;
  return __nx_dev_path_buf;
}}
{source_body}
int main(void) {{
  char path[PATH_MAX+1];
  char out[FS_MAX_PATH];
  fsdev_fsdevice *device = (fsdev_fsdevice*)1;
  size_t first_mismatch = (size_t)-1;
  size_t mismatch_output_len = 0;
  for (size_t n = 0; n < PATH_MAX; ++n) {{
    path[0] = '/';
    memset(path+1, 'A' + (n % 26), n ? n-1 : 0);
    path[n] = 0;
    memset(out, 0xCC, sizeof(out));
    test_reent._errno = 0;
    int rc = fsdev_getfspath(&test_reent, path, &device, out);
    size_t got = strnlen(out, sizeof(out));
    if (rc != 0) {{ fprintf(stderr, "unexpected rejection len=%zu rc=%d errno=%d\\n", n, rc, test_reent._errno); return 2; }}
    if ((got != n || memcmp(out, path, n) != 0) && first_mismatch == (size_t)-1) {{
      first_mismatch = n; mismatch_output_len = got;
    }}
    if (got > FS_MAX_PATH-1) {{ fprintf(stderr, "output escaped destination capacity\\n"); return 3; }}
  }}
  /* Deterministic content/length mutation campaign over normalized ASCII paths. */
  uint32_t rng = 0x50484138u;
  for (unsigned trial = 0; trial < 10000; ++trial) {{
    rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5;
    size_t n = rng % PATH_MAX;
    path[0] = '/';
    for (size_t i = 1; i < n; ++i) {{
      rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5;
      path[i] = (char)('!' + (rng % 90));
    }}
    path[n] = 0;
    int rc = fsdev_getfspath(&test_reent, path, &device, out);
    size_t expected = n < FS_MAX_PATH-1 ? n : FS_MAX_PATH-1;
    if (rc != 0 || strnlen(out, sizeof(out)) != expected || memcmp(out, path, expected) != 0 || out[expected] != 0) {{
      fprintf(stderr, "mutational trial=%u len=%zu rc=%d\\n", trial, n, rc); return 5;
    }}
  }}
  if (first_mismatch == (size_t)-1) {{ fprintf(stderr, "expected truncation was not observed\\n"); return 4; }}
  printf("first_successful_truncation_input=%zu output_bytes=%zu return=0\\n", first_mismatch, mismatch_output_len);
  printf("max_swept_input=%d destination_capacity=%d\\n", PATH_MAX-1, FS_MAX_PATH);
  printf("seeded_mutations=10000 seed=0x50484138\\n");
  return 0;
}}
'''
    with tempfile.TemporaryDirectory(prefix="phase8-path-abi-") as temporary:
        c_path = Path(temporary) / "path_test.c"
        binary = Path(temporary) / "path_test"
        c_path.write_text(harness)
        subprocess.run([
            "clang", "-std=c11", "-D_DARWIN_C_SOURCE", "-Wall", "-Wextra", "-Werror",
            "-fsanitize=address,undefined", str(c_path), "-o", str(binary)
        ], check=True)
        run = subprocess.run([str(binary)], text=True, capture_output=True)
        if run.returncode != 0:
            failure = {
                "experiment": "libnx_fsdev_getfspath_path_boundary",
                "source_sha256": source_hash,
                "failure_exit_code": run.returncode,
                "stdout": run.stdout,
                "stderr": run.stderr,
            }
            OUTPUT.write_text(json.dumps(failure, indent=2) + "\n")
            raise SystemExit(f"sanitized harness failed; crash/failure captured at {OUTPUT}: {run.stderr.strip()}")
    output_lines = run.stdout.strip().splitlines()
    first_line = output_lines[0]
    observed_len = int(first_line.split("input=")[1].split()[0])
    output_len = int(first_line.split("output_bytes=")[1].split()[0])
    if (observed_len, output_len) != (fs_max_path, fs_max_path-1):
        raise SystemExit(f"unexpected boundary result: {run.stdout}")
    result = {
        "experiment": "libnx_fsdev_getfspath_path_boundary",
        "classification": "host_source_behavior_not_switch_vulnerability",
        "source_commit_recorded_by_project": "b156b4774fb2df7b93402169509266da7547fc4c",
        "source_file": str(SOURCE.relative_to(ROOT)),
        "source_sha256": source_hash,
        "libnx_fs_header_sha256": hashlib.sha256(LIBNX_FS_HEADER.read_bytes()).hexdigest(),
        "newlib_limits_header_sha256": hashlib.sha256(NEWLIB_LIMITS.read_bytes()).hexdigest(),
        "compiler": subprocess.run(["clang", "--version"], text=True, capture_output=True, check=True).stdout.splitlines()[0],
        "reproduction_command": ".venv/bin/python scripts/phase8_path_truncation_test.py",
        "sanitizers": ["AddressSanitizer", "UndefinedBehaviorSanitizer"],
        "input_domain": f"absolute ASCII path-shaped sweep 0..{path_max-1} plus 10000 deterministic ASCII content/length mutations",
        "mutation_seed": "0x50484138",
        "fixpath_stub_scope": "accepts and bounded-copies supplied strings; it does not validate or normalize; full UTF-8/device/cwd path resolver not included and random mutations are not all valid under it",
        "reproducer_minimized_input": "/" + "A" * (observed_len-1),
        "minimal_length_bytes": observed_len,
        "observed_output_length_bytes": output_len,
        "getfspath_return": 0,
        "output_equals_input": False,
        "stdout": run.stdout,
        "stderr": run.stderr,
        "limits": ["Host-only extracted function test", "No HOS/Mariko artifact or runtime", "No security impact demonstrated"],
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(run.stdout, end="")
    print(f"PASS ASan/UBSan; result={OUTPUT.relative_to(ROOT)}")
    print(f"source_sha256={source_hash}")


if __name__ == "__main__":
    main()
