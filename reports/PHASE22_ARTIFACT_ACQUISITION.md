# PROJECT ZERO Phase 22 — Public Artifact and Tool Acquisition

Date: 2026-10-31  
Scope: public, legally distributable analysis tools and target artifact availability for WebApplet / BrowserDll on HOS 23.0.1. No firmware package, console secret, or proprietary executable was acquired.

## Outcome

No publicly available, clearly licensed and integrity-verifiable HOS 23.0.1 WebApplet/BrowserDll executable set was identified. The workspace search found no target NSO, matching NPDM, KIP, NCA/ExeFS, build identity, or BrowserDll/SystemData. Nintendo's public 23.0.1 update information is a release note, not a binary distribution or executable hash manifest. Third-party firmware archives were excluded because their licensing and authorization provenance were not clear. Consequently, no target binary was disassembled and no target vulnerability conclusion follows from this phase.

One useful public tool was acquired and built: NSTool v1.9.2, MIT-licensed, source commit `e89ea84bd70c11b67ebec9153fb4a446f18a9d3d`. Its source and build are outside the repository at `/tmp/pz22-nstool`; no executable or synthetic fixture is presented as HOS. NSTool provides an independent implementation for a bounded subset of NSO/NRO/NPDM parsing and made several format-version gaps in the project's Phase 19 inspector measurable.

## Artifact inventory and provenance

| Item | Result | Provenance / integrity |
|---|---|---|
| HOS 23.0.1 WebApplet NSO | Not found locally; not acquired | Nintendo's [23.0.1 update information](https://www.nintendo.com/en-gb/Support/Troubleshooting/Nintendo-Switch-System-Update-Information-1445507.html) publishes update notes but no executable package/hash. No authorized public executable source located. |
| Matching WebApplet NPDM and build identity | Not found; not acquired | Required to associate process permissions and exact build with an executable. No target identifier/hash manifest found. |
| BrowserDll / shared SystemData | Not found; not acquired | Required because the applet executable alone does not represent the shared web runtime documented by [Switchbrew Internet Browser](https://switchbrew.org/wiki/Internet_Browser). |
| Other HOS NSO/KIP/NCA/ExeFS artifacts | Not found in repository workspace | `find .. -type f` searches for `.nso`, `.npdm`, `.kip`, `.nca`, `*webapplet*`, and `*browserdll*` returned only the Phase 21 report. Existing app ELF/NRO are the project's own homebrew build, not Nintendo firmware. |
| NSTool source | Acquired from public upstream and built locally | [Repository](https://github.com/jakcron/nstool), stable commit `e89ea84bd70c11b67ebec9153fb4a446f18a9d3d`; upstream `LICENSE` is MIT, SHA-256 `68e8ed4fb647105e40e447c0cb76e09ac91b846533d17069a62711fcf1ea6bf8`. Source was cloned with history; its complete-history fetch reported unavailable historical submodule revisions, but the pinned stable commit and its recursive submodules were present. |
| NSTool build | Successful macOS build | `NSTool v1.9.2`; binary SHA-256 `b9341e27760a481799fb8aae091b4f2ba13ebf414aba45275e598412fe406a01`. Build: `make deps -j4 && make -j4`. Compiler emitted dependency deprecation/unused-variable warnings; no build failure. |
| NSTool submodules | Pinned public source dependencies | libfmt `b03b081e026ceb1226b45de926babe629d6c0688` (MIT); liblz4 `561775a11e00cbd21a45031c64068cb5e1242608` (BSD-2-Clause); mbedTLS `74346376dd035e9fbc161cdb80afc646b72fde86` (Apache-2.0); libpietendo `5d50d02f8f3b8918bdfbbb599b8c4c1628660d89` (MIT); libtoolchain `578d170f5b294e4a9feb3cc2d504896e846f204e` (MIT). No Nintendo firmware content was part of these dependencies. |

The console's USB/MTP interface is not treated as a source of system executables. No keys were supplied to NSTool and no signature verification, extraction, decryption, or console interaction was performed.

## Read-only parser experiments

NSTool was run in an isolated working directory with an empty temporary HOME. Startup emitted warnings that `prod.keys` and `title.keys` were absent. Those warnings are recorded as observed output; no key material was read. Commands below did not use `-k`, `-y`, extraction options, or any key value.

| Input | SHA-256 | Test/result |
|---|---|---|
| `../PROJECT_ZERO/apps/PROJECT_ZERO/PROJECT_ZERO.nro` | `55ac62855d2675b77d69e255cc3652eb0b6c090190c49125213cac65263cd0e7` | `nstool --showlayout` succeeded. Parsed local app NRO image size `0x51000`; sections `.text` offset `0`, size `0x3c000`, `.ro` offset `0x3c000`, size `0x10000`, `.data` offset `0x4c000`, size `0x5000`, BSS `0xc000`; NACP title `PROJECT ZERO`, version `0.1.0`. This is a homebrew artifact, not HOS. |
| `/tmp/pz22-fixtures/synthetic_uncompressed.nso` | `221cf6405387dfb572c7861305c6fea47132106aff8c162ae7f235234fe26af0` | Synthetic minimal NSO layout parsed successfully. Not firmware and not a complete loadable program. |
| `/tmp/pz22-fixtures/synthetic_lz4.nso` | `8f0360325e4bba84f7ae81846f85af96a112688b418b02c0ebb5868f510dc13f` | Synthetic LZ4 NSO parsed; `.text` is reported as compressed and the decompressed memory size is shown. This checks a constructed fixture only. |
| `/tmp/pz22-fixtures/synthetic_zbic_flag.nso` | `77319c2ed72bff2ed760db6aaeba826b911123cc8a12880efcf49f7fadd372ee` | Synthetic header with ZBIC flag bit set exited successfully, but NSTool did not mark the segment compressed. This establishes a parser flag-coverage gap; it does not test actual ZBIC data. |
| `/tmp/pz22-fixtures/synthetic_minimal.npdm` | `a97b3cbcc5cba510c8c9c154466ed136688d22f80ea83322381a53df29053cf2` | Synthetic minimal META structure parsed. It is not asserted to be semantically valid or loadable. |
| `/tmp/pz22-fixtures/synthetic_hos23_meta.npdm` | `88fe44f4caff4f16d9a7f7364eb2b412403c49fe9173e5d38faf25b23f14f554` | Constructed to exercise documented 23.0+ metadata fields. NSTool reports `ProcessAddressSpace: unk_0x04` and omits Flags1, despite the fixture setting those fields. Synthetic parser-compatibility test only. |
| `/tmp/pz22-fixtures/truncated.npdm` | `2d1edf729cc53756834657ce399b1568debd59b0ceddce5da39b86750d59fbd0` | Truncated synthetic META rejected with exit 1 (`Input file type was undetermined`). |

Fixtures were created under `/tmp` solely for parser tests and are intentionally not checked into the repository or represented as Nintendo artifacts. The corresponding format references are community documentation: [NSO](https://switchbrew.org/wiki/NSO), [NRO](https://switchbrew.org/wiki/NRO), [KIP1](https://switchbrew.org/wiki/KIP1), and [NPDM](https://switchbrew.org/wiki/NPDM). NSTool is an independent implementation, not an authoritative Nintendo specification.

## Independent implementation comparison and gaps

The repository's Phase 19 inspector was compared with NSTool on the local uncompressed homebrew NRO and constructed NSO/NPDM fixtures. On the uncompressed NRO, both recognize the basic image size and segment ranges. The comparison did not include a real Nintendo binary. Where unsupported metadata is ignored, this is reported as a disagreement, not resolved by assumption.

| Area | Observed limitation / disagreement | Evidence boundary |
|---|---|---|
| NSO ZBIC | NSTool v1.9.2's NSO flag definitions and processing cover the earlier LZ4 segment flags, not the ZBIC bit documented for later NSO revisions. A bit-7 synthetic header was accepted without a compressed marker. The project parser rejects unknown compression bits. | No ZBIC-compressed bytes were tested. A separate public implementation lead is [nxdumptool commit `441e5c0`](https://github.com/DarkMatterCore/nxdumptool/commit/441e5c0), described as adding ZBIC segment support; source/build validation of that commit was outside this experiment. |
| KIP1 | NSTool's KIP processing contains an explicit `NotImplementedException` for decompression. Recognition/metadata support is not compressed KIP support. The project parser also does not decompress BLZ. | No KIP fixture was used to claim decompression. Format documentation identifies the compression family; no HOS KIP was available. |
| NRO 23+ compression | NSTool's NRO header rejects nonzero flags as unsupported. The project Phase 19 parser likewise rejects compressed NRO flags. Public [NRO format notes](https://switchbrew.org/wiki/NRO) document a compression flag for 23.0+. | No compressed NRO payload was tested. |
| NPDM 23+ fields | In the synthetic documented address-space value `4` / Flags1 case, NSTool prints unknown address-space value and omits Flags1; Phase 19 retains raw Flags1 bytes but does not decode its semantics. Switchbrew's [NPDM notes](https://switchbrew.org/wiki/NPDM) document the 23.0+ fields. | This establishes a versioned metadata decoder gap, not a discrepancy observed in a real process manifest. |
| NSO LZ4 | NSTool successfully recognized and decompressed a small constructed LZ4 segment. The Phase 19 parser reports compression metadata but does not decompress. | One basic synthetic block only; no adversarial fuzzing or target compatibility claim. |

Other public leads reviewed: [Switchbrew format pages](https://switchbrew.org/wiki/Main_Page) (technical documentation, community-maintained); [NSTool source and history](https://github.com/jakcron/nstool) (MIT); [nxdumptool source history](https://github.com/DarkMatterCore/nxdumptool) (public source lead, not executed here); and [Nintendo's update information](https://www.nintendo.com/en-gb/Support/Troubleshooting/Nintendo-Switch-System-Update-Information-1445507.html) (official release notes). Search results for third-party firmware archives did not establish a clear redistribution license or authorized origin; those archives were not downloaded. No public research dataset with both an explicit redistributable license and an identified WebApplet 23.0.1 binary was found in this bounded search.

## Reproduction

From the repository root, the local app check is:

```sh
/tmp/pz22-nstool/bin/nstool --showlayout ../PROJECT_ZERO/apps/PROJECT_ZERO/PROJECT_ZERO.nro
```

For the external parser build, the source is at `/tmp/pz22-nstool`, pinned to the commit above:

```sh
cd /tmp/pz22-nstool
make deps -j4
make -j4
bin/nstool --showlayout /path/to/known-input.nro
```

The temporary fixture files listed above are local generated test inputs and are not committed. To reproduce the internal format test suite:

```sh
../.venv/bin/python -m unittest discover -s tests/workspace-tests -p 'test_switch_artifact_inspector.py' -v
```

## Readiness decision

**Tooling is ready for metadata-level triage of legally available, unencrypted NSO/NRO/NPDM subsets, but is not yet a reliable full HOS 23.0.1 loader/decompressor pipeline.** Before interpreting WebApplet code, the minimum target set is: (1) an authorized, unencrypted WebApplet executable with provenance and SHA-256, (2) its matching NPDM and exact build/title identity, and (3) same-build BrowserDll plus relevant shared SystemData/runtime modules. A source package or encrypted container alone cannot provide executable code to the current disassembler. An official source/manifest establishing the exact build and hashes is also needed to validate identity. This project will wait for a legitimate artifact or reproducible public technical result; it will not source firmware through circumvention or substitute synthetic data.

## Source list and evidence quality

| Source | Date / type | Confidence and scope |
|---|---|---|
| https://github.com/jakcron/nstool/tree/stable | Accessed 2026-10-31; public upstream source/history and MIT license | High for the checked-out source revision and license; medium for advertised coverage until exercised. Exact checked-out commit and hashes are listed above. |
| https://switchbrew.org/wiki/NSO | Accessed 2026-10-31; community format documentation | Medium; useful format description, not a Nintendo-published specification. |
| https://switchbrew.org/wiki/NRO | Accessed 2026-10-31; community format documentation | Medium; used to identify newer flags, not to validate any target binary. |
| https://switchbrew.org/wiki/KIP1 | Accessed 2026-10-31; community format documentation | Medium; does not establish that this project's parser supports decompression. |
| https://switchbrew.org/wiki/NPDM | Accessed 2026-10-31; community format documentation | Medium; newer metadata-field reference, not exact-build evidence. |
| https://switchbrew.org/wiki/Internet_Browser | Accessed 2026-10-31; community reverse-engineering documentation | Medium/low for exact 23.0.1 implementation; establishes why shared browser artifacts matter, not their presence. |
| https://www.nintendo.com/en-gb/Support/Troubleshooting/Nintendo-Switch-System-Update-Information-1445507.html | Accessed 2026-10-31; official update notes | High for listed release information; does not publish the system executable or its hashes. |
| https://github.com/DarkMatterCore/nxdumptool/commit/441e5c0 | Accessed 2026-10-31; public source-history lead | Medium as a lead; no local build or independent reproduction in this phase. |
