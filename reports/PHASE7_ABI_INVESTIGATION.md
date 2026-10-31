# Phase 7 — ABI and call chain

## Conclusion to the main hypothesis

For the examined combination of libnx `b156b4774fb2df7b93402169509266da7547fc4c` and the publicly available devkitA64 package `devkita64-newlib 4.6.0.20260123-4`, `filename` has a capacity of **256 bytes** when called from `readdir_r`. `NAME_MAX` is 255 bytes and the newlib source declares `char filename[NAME_MAX+1]` locally. Index 255 is therefore valid in this particular callback buffer. The helper writes to index 255 only when entering with `inlen=254`; an input of length 255 is rejected before returning successfully and without writing a NUL to index 256.

Decision for the buffer question: **B — safe according to the documented ABI contract**. However, the overall Phase 7 trace revealed a separate issue in the `seekdir` path; therefore, we report the overall decision as **D — other specific issue**.

## Call chain and size origin

1. The devkitPro header `include/sys/iosupport.h` declares `dirnext_r(struct _reent *, DIR_ITER *, char *filename, struct stat *filestat)`; the size is not passed in the callback type itself. In this ABI, it is provided by the caller.
2. The libsysbase source from newlib/devkitPro implements `__dirnext()` and passes the same callback pointer (`libsysbase_dirent.c:67–82`).
3. `readdir_r()` creates the automatic field `char filename[NAME_MAX+1]` (`:140–148`) and calls `__dirnext(..., filename, st)` (`:158`). Subsequently, it limits the length to `sizeof(filename)` (`:175`) and copies to `entry->d_name` (`:180`).
4. The `sys/syslimits.h` header defines `NAME_MAX 255` as the maximum number of bytes in the name. `sys/dirent.h` declares `d_name[NAME_MAX+1]` (256 bytes). So the contract is 255 bytes of the name plus NUL, not a 255-byte total buffer.
5. `opendir()` creates a `DIR` object and iterator state; its exact allocations are not the source of the callback buffer. `filename` is a local field on the stack in each call to `readdir_r` or `seekdir`, not a libnx-allocated field.
6. `seekdir()` declares the same field as `filename[NAME_MAX+1]`, but calls `__dirnext(..., filename, NULL)` (`:212–231`). This reveals a conflict with the examined libnx callback.
7. Libnx `fsdev_dirnext()` first writes `filestat->st_ino` (`references/vendor/libnx_fs_dev.c:1456`) and then zero-initializes `NAME_MAX` name bytes (`:1471`), calls `fsdev_convertfromfspath(..., NAME_MAX)` (`:1472`) and returns at `units >= NAME_MAX` `ENAMETOOLONG` (`:1479`). With valid maximum received `inlen=254` helper sets `filename[255] = 0`; 256-byte capacity covers it.

## Versions and provenance restrictions

Package `devkita64-newlib 4.6.0.20260123-4` is listed as a dependency of metapackages devkitA64 r29.2 and r30. The devkita64-newlib packages `4.5.0.20241231-2`, `4.6.0.20260123-3` and `4.6.0.20260123-4` have the same `NAME_MAX`, `d_name` and callback definitions in the compared headers; in `-4`, `iosupport.h` also changed elsewhere, not in the `dirnext_r` signature. This documents these specific releases, not every historical newlib/devkitPro version.

The official devkitPro packaging host was unavailable when resourcing; the public mirror repository provided the package and buildscript. The package was not cryptographically verified: `.sig` was not found next to it and the build metadata shows `options=!sign`. SHA-256 identifies downloaded bytes, but does not prove the publisher by itself. The corresponding upstream newlib tarball from Sourceware does not contain the devkitPro `libsysbase` ABI plugins. The devkitPro source patch therefore serves as a public reproducible source, with the specified trust restriction.

## Another concrete clue

`seekdir()` in this newlib source passes `NULL` as `filestat`, but libnx `fsdev_dirnext()` dereferences it without checking. Host reproduction with exact source blocks and ASan showed this path as a null dereference. It is a specific mismatch of calling contracts, independent of the buffer overflow issue. Not yet proof of console reach, successful exploit, HOS 23.0.1 reach, or confirmation that a specific app/SDK path will trigger this combination.

Next separate trace: check the boundary between `PATH_MAX=1024` and `FS_MAX_PATH=769` in `fsdev_fixpath()` / `fsdev_getfspath()` and see if the long path is silently shortened. It is not yet classified as a security flaw.
