# Phase 7 — records and reproduction identifiers

## Primary local resources

| Artifact | Exact Location / Identifier | SHA-256 |
|---|---|---|
| libnx source file | `references/vendor/libnx_fs_dev.c`; project reports commit `b156b4774fb2df7b93402169509266da7547fc4c` | `6a0138df373ffca4d1237854b5a3cd24742fc4ee696a122c4daeae2cf83ca2b4` |
| libnx FS header | `references/vendor/libnx_fs.h` (`FS_MAX_PATH=0x301`, `FsDirectoryEntry.name[FS_MAX_PATH]`) | `670740e6228674a0bb9d2cb1d4230a230d6cc867f423a68df827c083d4f24504` |
| devkitA64 newlib/libsysbase source | `references/vendor/devkita64-newlib-4.6.0.20260123-4/libsysbase_dirent.c` | `59c901f7a932339a91405f6e1f9e693f8015100e23ab785e9d660cf8b99a4ca6` |
| `sys/dirent.h` | `.../include/sys/dirent.h` | `11181982b8606dfe9a99630354ef148dd51654a8e8f0afe425430c9c6feb6ba5` |
| `sys/syslimits.h` | `.../include/sys/syslimits.h` | `e041fa4ea0dbef6e8bd41856b85f4bb5e85c5d5867ba21063763c6f68f77bdc7` |
| `sys/iosupport.h` | `.../include/sys/iosupport.h` | `750016fcdaf5cf5583fdd2387406edeb070c3a176d709c7f8f4c2ff25990b515` |
| AArch64 object `libsysbase_dirent.o` | `.../libsysbase_dirent.o` | `4b3b4fdb38ef370402120d9964d39f2b487e9c34ce1bf250c39eb3eb767fd7de` |

## Versioned public resources

- devkitA64 r30 source distribution: [buildscripts-devkitA64_r30.tar.gz](https://wii.leseratte10.de/devkitPro/devkitA64/r30%20(2026-06-10)/buildscripts-devkitA64_r30.tar.gz), retrieved 2026-10-30, SHA-256 `22291012955e42b877ff1a466a1acddcd4b4737d1c21bc83cf769102662c7811`. Contains patch `newlib-4.6.0.20260123-4.patch` (SHA-256 `6d5aba4356553c727765c98e7553d3784f31d361c856e220ef27cc26353fb88f`) and libsysbase source context.
- Package devkita64-newlib `4.6.0.20260123-4`: [package archive](https://wii.leseratte10.de/devkitPro/devkitA64/r29%20(2026-01)/devkita64-newlib-4.6.0.20260123-4-any.pkg.tar.zst), SHA-256 `fc97ba1009a94b68f8714c3cc548ef697ca82687b72fe0c05a7ca3df81beb53e`. `.PKGINFO` lists project name/version and packager Dave Murphy/devkitPro. An available signature file was not found; we do not mark the package as cryptographically verified.
- The devkitA64 r29.2 and r30 metapackages depend on `devkita64-newlib>=4.6.0.20260123-4` (data from their `.PKGINFO`). This binds the reviewed ABI package to these specific toolchain releases, not to every version.
- Comparison archives `4.5.0.20241231-2` SHA-256 `5c0e3f61e612ebcc4c5995c1545427a0760519bd2d6526c36846d47391e48355` and `4.6.0.20260123-3` SHA-256 `acfea04d318e775624b492d4470109b79111f380a2eba132e5c49dbacb8c4123` had the same relevant layout/signature in the investigated headers. The scope of the comparison is only these artifacts.
- Upstream [GNU Newlib 4.6.0.20260123](https://sourceware.org/pub/newlib/newlib-4.6.0.20260123.tar.gz), downloaded 2026-10-30, SHA-256 `6ff27e3bf022666f43f7802255be680eeff722ac181b1725d21e2e8318604ee3`. It does not contain the devkitPro `libsysbase` extension, so the upstream tarball alone is not sufficient to detect the callback buffer.

## Reproduction

From root `switch-research` run:

```sh
python3 scripts/phase7_fs_abi_test.py
```

The script prints the SHA-256 of the resources at runtime, compiles the host reproduction program via Apple clang with `-fsanitize=address,undefined`, and executes the `readdir_r` and `seekdir` tests. The record of results is in `PHASE7_TEST_RESULTS.md`. Host ARM64 target macOS is not Tegra/console proof.

## Classification of evidence

- **Strong source evidence:** 256-byte array declaration in exact newlib source; `NAME_MAX=255`; exact callback call-through; exact libnx helper and its rejection of names of length 255.
- **Strong reproducible proof on host:** ASan/UBSan test of exact extracted blocks confirms received boundaries and reproduces NULL dereference via `seekdir`.
- **Limitations:** missing verified signature of the devkitPro package, the entire target toolchain is not linked, there was no test on the console and the impact on a specific HOS build is not confirmed.
- **Overall decision:** D for separate specific error `seekdir`/`filestat`; for the original index-255 hypothesis, B, not A, holds.
