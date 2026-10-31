# PROJECT ZERO Phase 24 — HOS 23.0.1 Artifact Acquisition

Date: 2026-10-31  
Target: Nintendo Switch original-family V2 / Mariko T210B01, HOS 23.0.1  
Scope: Locate identifiable WebApplet and shared web-runtime artifacts through public sources and the local workspace. No console changes, key access, firmware extraction, or binary downloads were performed.

## Result

**No HOS executable artifact was acquired.** The project workspace contains no Nintendo NSO, NPDM, KIP, NCA, NSP, XCI, CNMT, or PFS0 input. The only `.nro` files found are PROJECT ZERO's own homebrew release. No WebApplet NSO, paired `main.npdm`, BrowserDll/SystemData, NetFront/OSS NRO, or 23.0.1 build manifest/hash set is available for static analysis. No files were placed in `artifacts/hos-23.0.1/`.

One useful version-metadata result emerged: the Switchbrew 23.0.1 change page lists only the `sdb` sysmodule and `SystemVersion:/file` as changed. Its title list reports BrowserDll (`0100000000000803`) at title version `v1543505072` / `23.0.0.1200`; WebApplet (`010000000000100A`) has a listed title update through `22.0.0` and is marked stubbed from `22.0.0+`. This suggests that a 23.0.1 update package may not contain changed WebApplet or BrowserDll executables and that a same-build runtime investigation may need the 23.0.0-era title artifacts. **This is community-maintained title/change metadata, not binary identity evidence:** it does not establish exact installed content, hashes, Mariko-specific differences, or whether data is byte-identical between 23.0.0 and 23.0.1. Do not treat it as an NSO or as confirmation that a file can be analyzed.

## Local artifact inventory

Search scope was the repository and its sibling `PROJECT_ZERO` tree:

```sh
find .. -type f \
  \( -iname '*.nso' -o -iname '*.npdm' -o -iname '*.nca' -o -iname '*.kip' \
     -o -iname '*.nro' -o -iname '*.nsp' -o -iname '*.xci' -o -iname '*.cnmt' \
     -o -iname '*.pfs0' \) -print
```

Output:

```text
../PROJECT_ZERO/apps/PROJECT_ZERO/PROJECT_ZERO.nro
../PROJECT_ZERO/apps/PROJECT_ZERO/release/switch/PROJECT_ZERO.nro
```

Both files are the project's homebrew app, not Nintendo firmware. No hash or parser run on them is presented as HOS evidence. The existing NSTool and project parser tests remain host/tool validation only (see Phase 22/23); no duplicate parser tests were run here.

## Public source and archive review

| Source | Date / type | Finding | Integrity, license, and decision | Confidence |
|---|---|---|---|---|
| [Nintendo 23.0.1 System Update Information](https://www.nintendo.com/en-gb/Support/Troubleshooting/Nintendo-Switch-System-Update-Information-1445507.html) | Accessed 2026-10-31; official support page | Confirms 23.0.1 release date 2026-10-01 and says updates are made available through the internet to the console. Lists a functional fix; publishes no component binary, manifest, or executable hash. | Official version/date evidence. No downloadable research artifact exposed by this page. | High for release notes; none for binary contents. |
| [Switchbrew 23.0.1 change page](https://switchbrew.org/wiki/23.0.1) | Page edited 2026-10-01; community reverse-engineering changelog | Lists `sdb` as the updated sysmodule and `SystemVersion:/file` as the RomFS change; security-flaws field remains unfilled. | Not a binary or official Nintendo manifest. No hash or exact component build identity. | Medium for community-observed title delta. |
| [Switchbrew Title list](https://switchbrew.org/wiki/Title_list) | Accessed 2026-10-31; community title/version catalog | Lists BrowserDll ID `0100000000000803` at `23.0.0.1200`, with its shared-data role and OSS NRO/buildinfo contents; lists WebApplet ID `010000000000100A` updated through `22.0.0`, marked stubbed at 22.0.0+. | Identifies relevant title/version metadata, not installed bytes, hash, architecture, or exact HOS 23.0.1 executable. | Medium for catalog entry; low for exact-build binary inference. |
| [Switchbrew Internet Browser](https://switchbrew.org/wiki/Internet_Browser) | Accessed 2026-10-31; community technical documentation | Documents WebApplet, WifiWebAuthApplet and shared BrowserDll/SystemData context; establishes why an applet executable alone is insufficient. | No 23.0.1 NSO, NPDM, or BrowserDll payload is linked. | Medium for documented architecture; not target binary evidence. |
| [Nintendo Switch System Update reports (NinUpdates)](https://yls8.mtheall.com/ninupdates/reports.php) and the linked 2026-10-01 HOS report | Accessed 2026-10-31; third-party parsed update metadata | Search results expose a 23.0.1 update report and title-list references. Exact per-component WebApplet/BrowserDll executable hashes were not located. Direct titlelist query could not be retrieved in this run. | Metadata lead only; no binary acquired and no independent integrity check. | Low/medium; parser/database is not Nintendo-authenticated. |
| [THZoria/NX_Firmware release 23.0.1](https://github.com/THZoria/NX_Firmware/releases/tag/23.0.1) | GitHub release dated 2026-10-01; third-party firmware archive | Publishes an automatically generated `Firmware 23.0.1.zip` release. The release tag is GitHub-verified for its publisher identity. Earlier release listing search surfaced archive SHA-256 `5337647d78584d046b6c8f46792a07c3701d7ee68473620d5008f18fc7604781`; this value was not recalculated locally. | Not downloaded: the GitHub signature authenticates the release publisher, not Nintendo authorization or a clear redistribution license. A firmware archive/container would not itself be an unencrypted NSO. | High that the release page exists; low for authorized provenance and binary identity. |
| [Darthsternie's Switch Firmware Archive](https://darthsternie.net/switch-firmwares/) | Accessed 2026-10-31; third-party mirror index | Lists 23.0.1 as a 324 MB package with publisher-posted MD5 `910bd0b523553c2a97254b654392976d`; its page says entries may be dumps from game-card/system partitions or Nintendo CDN. | Not downloaded: source chain and distribution authorization are not established. MD5 was not independently checked and is not a cryptographic identity proof. | High for what its page claims; low for provenance. |
| [NSTool source](https://github.com/jakcron/nstool) / [nxdumptool source](https://github.com/DarkMatterCore/nxdumptool) | Public open-source format/tool repositories; previously pinned/tested in Phases 22–23 | Provide format handling and extraction-tool source, not a redistributable HOS 23.0.1 WebApplet data set. | NSTool v1.9.2 is MIT-licensed and already built locally. No firmware input or key material was used. | High for tool-source availability; no target artifact evidence. |
| GitHub searches for `HOS 23.0.1 WebApplet NSO NPDM BrowserDll`, title ID `010000000000100A`, and firmware manifests | Search performed 2026-10-31; public repo/history search | Found archive mirrors and source/tools, but no clearly licensed dataset containing a matching unencrypted WebApplet + NPDM + BrowserDll/OSS set with target version/build hashes. | Archive listings were not treated as permission to redistribute proprietary firmware; no download performed. | Bounded negative search only; absence is not proof of nonexistence. |

The open-source [Switchbrew mirror of the title list](https://github.com/backupbrew/switchbrew/blob/master/Title%20list.txt) and older [Eliboa system-title catalog](https://www.eliboa.com/switch/system_titles.php) were also reviewed as cross-checks. The latter only covers historical versions through 14.1.1 and cannot identify 23.0.1 artifacts. Neither supplies executable files.

## Artifact status and minimum inputs

| Requested item | Status | Minimum usable evidence still needed |
|---|---|---|
| WebApplet `010000000000100A` executable | Missing; no 23.0.1 binary/hash. Catalog says last title update 22.0.0 and stubbed from 22.0.0+. | Authorized, unencrypted executable bytes with source chain, title/version, SHA-256, and an identity link to the target installation/build. If it is a stub, establish that from the actual content rather than the catalog label. |
| Paired `main.npdm` | Missing | Same-title/same-build NPDM bytes and hash, with a credible pairing record. |
| BrowserDll `0100000000000803` / shared SystemData | Missing | Same target runtime content including `buildinfo/buildinfo.dat` and relevant OSS NROs; hashes, title version, and provenance. Catalog lists 23.0.0.1200, not an exact binary hash. |
| NetFront / OSS NRO components | Missing | The exact shared-data files and their build/version identity; the generic catalog entry is not sufficient. |
| Build/update manifest and exact identities | Missing | A legitimate manifest or independently verifiable title metadata associating the files to HOS 23.0.1 and the original Switch platform. Nintendo's public support note does not provide one. |
| Mariko-specific evidence | Missing | Evidence linking the analyzed executable/content and observed behavior to T210B01. Filename, title ID, or firmware version alone is insufficient. |

### Legitimate acquisition paths

1. Nintendo's public supported update route updates a user's console but does not expose a research file set on the cited official support page.
2. An owner may provide an already-legitimately-held artifact and its provenance for analysis, provided no keys or circumvention-derived contents are included in the handoff. None was present in the inspected workspace.
3. A future public research dataset can be used if its publisher provides clear redistribution permission, exact version/title identity, and verifiable hashes. No matching dataset was found in this search.

This phase did not attempt console extraction, decryption, key discovery, or access-control circumvention. It did not download third-party firmware archives. A public encrypted container without authorized decryption inputs is not an analyzable NSO and is not reported as one.

## Analysis performed and not performed

No candidate Nintendo artifact passed acquisition and identity gates, so no NSTool or PROJECT ZERO parser was run against HOS. There are no HOS hashes, segment maps, imports/exports, NPDM service permissions, BrowserDll dependencies, or disassembly results to report. Existing parser readiness is the Phase 23 bounded subset only; it does not establish full firmware-container support.

The concrete new result is the public version delta above: available community metadata currently points to 23.0.0-era BrowserDll and older/stubbed WebApplet title records, while the 23.0.1 page lists only `sdb` and `SystemVersion:/file` changes. This narrows what version set to request next but does not replace the missing binary identity and bytes.

## Next decision

**Artifact gate remains closed.** Do not spend effort extending parsers or synthesizing HOS inputs. The next evidence-producing step is to obtain a legitimately provided, unencrypted candidate set (or a clear-license public dataset) containing the WebApplet title content, matching NPDM, BrowserDll SystemData/OSS NROs, and hashes/build metadata. Until then, only community title/version metadata can be refined; exact static analysis of HOS 23.0.1 and Mariko-specific claims remain impossible.
