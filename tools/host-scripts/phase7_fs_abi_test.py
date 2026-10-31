#!/usr/bin/env python3
"""Exercise the exact libnx filename callback block with the pinned devkitA64 ABI."""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIBNX_SOURCE = ROOT / "references/vendor/libnx_fs_dev.c"
LIBNX_FS_HEADER = ROOT / "references/vendor/libnx_fs.h"
ABI_ROOT = ROOT / "references/vendor/devkita64-newlib-4.6.0.20260123-4"
ABI_DIRENT = ABI_ROOT / "include/sys/dirent.h"
ABI_LIMITS = ABI_ROOT / "include/sys/syslimits.h"
ABI_IOSUPPORT = ABI_ROOT / "include/sys/iosupport.h"
ABI_OBJECT = ABI_ROOT / "libsysbase_dirent.o"
NEWLIB_DIRENT_SOURCE = ABI_ROOT / "libsysbase_dirent.c"


def extract_function(source: str, signature: str) -> str:
    match = re.search(signature, source)
    if not match:
        raise SystemExit(f"source function not found: {signature}")
    start = match.start()
    brace = source.find("{", match.start())
    depth = 0
    for pos in range(brace, len(source)):
        if source[pos] == "{":
            depth += 1
        elif source[pos] == "}":
            depth -= 1
            if depth == 0:
                return source[start : pos + 1]
    raise SystemExit("unterminated source function")


def extract_name_callsite(source: str) -> str:
    start = source.index("    /* convert name from fs-path to UTF-8 */")
    end_marker = "    return 0;"
    end = source.index(end_marker, start) + len(end_marker)
    return source[start:end]


def extract_between(source: str, start_marker: str, end_marker: str) -> str:
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    return source[start:end]


def main() -> None:
    src_bytes = LIBNX_SOURCE.read_bytes()
    src = src_bytes.decode()
    fs_header = LIBNX_FS_HEADER.read_text()
    dirent = ABI_DIRENT.read_text()
    limits = ABI_LIMITS.read_text()
    iosupport = ABI_IOSUPPORT.read_text()

    name_max_match = re.search(r"^#define\s+NAME_MAX\s+(\d+)\b", limits, re.M)
    fs_path_match = re.search(r"^#define\s+FS_MAX_PATH\s+0x([0-9a-fA-F]+)\b", fs_header, re.M)
    if not name_max_match or not fs_path_match:
        raise SystemExit("could not resolve NAME_MAX or FS_MAX_PATH from pinned headers")
    name_max = int(name_max_match.group(1))
    fs_max_path = int(fs_path_match.group(1), 16)
    if not re.search(r"char\s+d_name\s*\[\s*NAME_MAX\s*\+\s*1\s*\]", dirent):
        raise SystemExit("pinned ABI does not declare d_name[NAME_MAX+1]")
    if not re.search(r"int\s*\(\*dirnext_r\)\s*\(struct _reent\s*\*r,\s*DIR_ITER\s*\*dirState,\s*char\s*\*filename,\s*struct stat\s*\*filestat\)", iosupport):
        raise SystemExit("pinned devoptab callback signature changed")
    if name_max != 255:
        raise SystemExit(f"unexpected target NAME_MAX={name_max}")

    helper = extract_function(src, r"static ssize_t fsdev_convertfromfspath\s*\([^)]*\)\s*\{")
    callsite = extract_name_callsite(src)
    if not all(p.exists() for p in (ABI_OBJECT, NEWLIB_DIRENT_SOURCE, ABI_DIRENT, ABI_LIMITS, ABI_IOSUPPORT)):
        raise SystemExit("pinned ABI evidence artifact missing")
    newlib_src = NEWLIB_DIRENT_SOURCE.read_text()
    dirnext = extract_function(newlib_src, r"static int __dirnext\s*\([^)]*\)\s*\{")
    dirreset = extract_function(newlib_src, r"static int __dirreset\s*\([^)]*\)\s*\{")
    readdir_r = extract_function(newlib_src, r"int readdir_r\s*\([^)]*\)\s*\{")
    seekdir = extract_function(newlib_src, r"void seekdir\s*\([^)]*\)\s*\{")
    if "char filename[NAME_MAX+1];" not in readdir_r:
        raise SystemExit("pinned readdir_r callback buffer changed")
    if "char filename[NAME_MAX+1];" not in seekdir or "__dirnext (dirp->dirData, filename, NULL)" not in seekdir:
        raise SystemExit("pinned seekdir callback behavior changed")
    stat_block = extract_between(src, "    /* fill in the stat info */", "    /* convert name from fs-path to UTF-8 */")

    # Compile the exact target header layout, devkitPro __dirnext/readdir_r/
    # seekdir source, and the libnx stat/name callback blocks. Shims supply
    # only host _reent/devoptab declarations.
    harness = f'''#include <errno.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
struct _reent {{ int _errno; void *deviceData; }};
static struct _reent test_reent;
#define _REENT (&test_reent)
#undef errno
#define errno (test_reent._errno)
#include "{ABI_DIRENT}"
#define FS_MAX_PATH {fs_max_path}
typedef struct {{
  char name[FS_MAX_PATH]; uint8_t pad[3]; int8_t type; uint8_t pad2[3]; int64_t file_size;
}} FsDirectoryEntryForHarness;
enum {{ FsDirEntryType_Dir = 0, FsDirEntryType_File = 1 }};
static FsDirectoryEntryForHarness source_entry;
typedef struct devoptab_t {{
  void *deviceData;
  int (*dirnext_r)(struct _reent *, DIR_ITER *, char *, struct stat *);
  int (*dirreset_r)(struct _reent *, DIR_ITER *);
}} devoptab_t;
static int tested_fsdev_dirnext(struct _reent *, DIR_ITER *, char *, struct stat *);
static int test_dirreset(struct _reent *r, DIR_ITER *d) {{ (void)r; (void)d; return 0; }}
static const devoptab_t test_device = {{ .deviceData = NULL, .dirnext_r = tested_fsdev_dirnext, .dirreset_r = test_dirreset }};
const devoptab_t *devoptab_list[] = {{ &test_device }};
{helper}
static int tested_fsdev_dirnext(struct _reent *r, DIR_ITER *dirState, char *filename, struct stat *filestat) {{
  ssize_t units;
  FsDirectoryEntryForHarness *entry = &source_entry;
  (void)dirState;
{stat_block}
{callsite}
}}
{dirreset}
{dirnext}
{readdir_r}
{seekdir}
_Static_assert(NAME_MAX == {name_max}, "NAME_MAX must come from pinned ABI");
_Static_assert(sizeof(((struct dirent *)0)->d_name) == NAME_MAX + 1, "ABI dirent field capacity mismatch");
_Static_assert(sizeof(((DIR *)0)->fileData.d_name) == NAME_MAX + 1, "DIR result buffer capacity mismatch");
static int run_case(const char *label, size_t len, int terminate, int expected_rc, int expected_errno) {{
  DIR_ITER state = {{0}}; DIR dir = {{0}}; struct dirent entry = {{0}};
  struct dirent *result = NULL;
  memset(source_entry.name, 'Q', sizeof(source_entry.name));
  if (terminate) source_entry.name[len] = 0;
  test_reent._errno = 0; state.device = 0; dir.dirData = &state;
  int rc = readdir_r(&dir, &entry, &result);
  if (rc != expected_rc || test_reent._errno != expected_errno) {{
    fprintf(stderr, "FAIL %s rc=%d errno=%d expected=%d/%d\\n", label, rc, test_reent._errno, expected_rc, expected_errno); return 1;
  }}
  if (rc == 0) {{
    if (result != &entry || strnlen(entry.d_name, sizeof(entry.d_name)) != len || entry.d_name[len] != 0 || memcmp(entry.d_name, source_entry.name, len) != 0) {{
      fprintf(stderr, "FAIL %s output mismatch\\n", label); return 1;
    }}
  }} else if (result != NULL) {{
    fprintf(stderr, "FAIL %s returned an entry after callback failure\\n", label); return 1;
  }}
  printf("PASS %s (callback capacity=%d rc=%d errno=%d)\\n", label, NAME_MAX+1, rc, test_reent._errno);
  return 0;
}}
static int seekdir_null_probe(void);
int main(int argc, char **argv) {{
  if (argc > 1 && strcmp(argv[1], "--seekdir-null-probe") == 0)
    return seekdir_null_probe();
  static const uint8_t utf8[] = {{0xE2, 0x82, 0xAC, 0}};
  int failed = 0;
  memset(source_entry.name, 0, sizeof(source_entry.name));
  failed |= run_case("empty", 0, 1, 0, 0);
  memset(source_entry.name, 0, sizeof(source_entry.name)); memcpy(source_entry.name, "switch", 7);
  failed |= run_case("short ASCII", 6, 1, 0, 0);
  memset(source_entry.name, 0, sizeof(source_entry.name)); memcpy(source_entry.name, utf8, sizeof(utf8));
  failed |= run_case("multibyte UTF-8 bytes", 3, 1, 0, 0);
  memset(source_entry.name, 'a', sizeof(source_entry.name)); source_entry.name[NAME_MAX-2] = 0;
  failed |= run_case("NAME_MAX - 2", NAME_MAX-2, 1, 0, 0);
  memset(source_entry.name, 'b', sizeof(source_entry.name)); source_entry.name[NAME_MAX-1] = 0;
  failed |= run_case("NAME_MAX - 1", NAME_MAX-1, 1, 0, 0);
  memset(source_entry.name, 'c', sizeof(source_entry.name)); source_entry.name[NAME_MAX] = 0;
  failed |= run_case("NAME_MAX terminated input rejected by callback", NAME_MAX, 1, ENAMETOOLONG, ENAMETOOLONG);
  memset(source_entry.name, 'd', sizeof(source_entry.name));
  failed |= run_case("no NUL in helper input bound", NAME_MAX, 0, ENAMETOOLONG, ENAMETOOLONG);
  return failed ? 1 : 0;
}}
static int seekdir_null_probe(void) {{
  DIR_ITER state = {{0}}; DIR dir = {{0}};
  state.device = 0; dir.dirData = &state; dir.position = 0;
  source_entry.type = FsDirEntryType_File;
  seekdir(&dir, 1);
  return 0;
}}
'''
    with tempfile.TemporaryDirectory(prefix="phase7-fs-abi-") as temp:
        tmp = Path(temp)
        # Header include shims avoid mixing the cross-target libc headers with
        # macOS headers; the exact target sys/dirent.h and sys/syslimits.h stay
        # the definitions under test.
        shim = tmp / "shim"
        shim_sys = shim / "sys"
        shim_sys.mkdir(parents=True)
        (shim_sys / "iosupport.h").write_text(
            "#ifndef __iosupp_h__\n#define __iosupp_h__\n"
            "typedef struct DIR_ITER { int device; void *dirStruct; } DIR_ITER;\n"
            "#endif\n"
        )
        (shim_sys / "syslimits.h").write_text(f'#include "{ABI_LIMITS}"\n')
        # Rewrite quoted target header include to resolve sub-includes through
        # the shims and then the pinned target syslimits header.
        harness = harness.replace(f'#include "{ABI_DIRENT}"', f'#include "{ABI_DIRENT}"')
        cfile = tmp / "phase7_fs_abi_test.c"
        binary = tmp / "phase7_fs_abi_test"
        cfile.write_text(harness)
        subprocess.run(
            ["clang", "-std=c11", "-D_DEFAULT_SOURCE", "-Wall", "-Wextra", "-Werror", "-Wno-sign-compare", "-fsanitize=address,undefined", "-I", str(shim), str(cfile), "-o", str(binary)],
            check=True,
        )
        subprocess.run([str(binary)], check=True)
        probe = subprocess.run([str(binary), "--seekdir-null-probe"], text=True, capture_output=True)
        diagnostic = probe.stdout + probe.stderr
        if probe.returncode == 0 or "AddressSanitizer" not in diagnostic:
            raise SystemExit("seekdir NULL filestat path did not produce the expected ASan report")
        asan_line = next((line.strip() for line in diagnostic.splitlines() if "AddressSanitizer:" in line), "AddressSanitizer diagnostic captured")
        print(f"REPRODUCED seekdir NULL filestat dereference (child_rc={probe.returncode}; {asan_line})")

    print(f"ABI NAME_MAX={name_max}; d_name capacity={name_max+1}; FS_MAX_PATH={fs_max_path}")
    for path in (LIBNX_SOURCE, LIBNX_FS_HEADER, ABI_DIRENT, ABI_LIMITS, ABI_IOSUPPORT, NEWLIB_DIRENT_SOURCE, ABI_OBJECT):
        print(f"SHA256 {path.relative_to(ROOT)} {hashlib.sha256(path.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
