#!/usr/bin/env python3
"""Compile the exact libnx helper body with a small host-side boundary harness."""
from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "references/vendor/libnx_fs_dev.c"
NAME_MAX = 255  # newlib target constant; used by fsdev_dirnext at the call site


def extract_function(source: str) -> str:
    match = re.search(r"static ssize_t fsdev_convertfromfspath\s*\([^)]*\)\s*\{", source)
    if not match:
        raise SystemExit("helper not found in pinned upstream source")
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
    raise SystemExit("unterminated helper body")


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    source = source_bytes.decode()
    helper = extract_function(source)
    harness = r"""
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#define NAME_MAX 255
""" + helper + r"""
static int check(const char *label, const uint8_t *in, size_t inlen,
                 ssize_t expected_len, int should_be_string) {
    uint8_t out[NAME_MAX + 1];
    memset(out, 0xA5, sizeof(out));
    memset(out, 0, NAME_MAX); /* exact caller preparation in fsdev_dirnext */
    ssize_t got = fsdev_convertfromfspath(out, (uint8_t *)in, NAME_MAX);
    if (got != expected_len) {
        fprintf(stderr, "%s: got length %zd expected %zd\n", label, got, expected_len);
        return 1;
    }
    if (got >= 0 && (size_t)got != inlen) {
        fprintf(stderr, "%s: copied length %zd expected %zu\n", label, got, inlen);
        return 1;
    }
    if (should_be_string && (out[inlen] != 0 || strlen((char *)out) != inlen)) {
        fprintf(stderr, "%s: expected NUL-terminated %zu-byte result\n", label, inlen);
        return 1;
    }
    if (got >= 0 && memcmp(out, in, inlen) != 0) {
        fprintf(stderr, "%s: byte content changed\n", label);
        return 1;
    }
    printf("PASS %s (result=%zd)\n", label, got);
    return 0;
}
int main(void) {
    uint8_t zero[] = {0};
    uint8_t ascii[] = "switch";
    uint8_t utf8[] = {0xE2, 0x82, 0xAC, 0};
    uint8_t max_minus_one[NAME_MAX];
    uint8_t max_no_nul[NAME_MAX];
    memset(max_minus_one, 'x', sizeof(max_minus_one)); max_minus_one[NAME_MAX-1] = 0;
    memset(max_no_nul, 'y', sizeof(max_no_nul));
    int failed = 0;
    failed |= check("empty", zero, 0, 0, 1);
    failed |= check("ascii", ascii, 6, 6, 1);
    failed |= check("UTF-8 bytes copied", utf8, 3, 3, 1);
    /* fsdev_dirnext rejects units >= NAME_MAX after the helper returns. */
    failed |= check("largest accepted length", max_minus_one, NAME_MAX-1, NAME_MAX-1, 1);
    failed |= check("helper returns NAME_MAX for unterminated NAME_MAX input", max_no_nul, NAME_MAX, NAME_MAX, 0);
    return failed ? 1 : 0;
}
"""
    with tempfile.TemporaryDirectory(prefix="phase6-fs-") as temp:
        cfile = Path(temp) / "fs_name_test.c"
        binary = Path(temp) / "fs_name_test"
        cfile.write_text(harness)
        subprocess.run(
            ["clang", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Wno-sign-compare", "-fsanitize=address,undefined", str(cfile), "-o", str(binary)],
            check=True,
        )
        subprocess.run([str(binary)], check=True)
    print(f"SOURCE_SHA256 {hashlib.sha256(source_bytes).hexdigest()}")
    print(f"SOURCE {SOURCE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
