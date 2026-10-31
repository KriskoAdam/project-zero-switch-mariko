# PROJECT ZERO Phase 26 — BrowserDll and openWeb Artifact Acquisition

Date: 2026-10-31  
Target: original Nintendo Switch / HOS 23.0.1, with Mariko relevance assessed separately  
Scope: Seek actual BrowserDll and openWeb binary artifacts, validate local availability, and use public update metadata to establish exact candidate revisions and 23.0.1 carry-forward evidence. No firmware, keys, or proprietary executable bytes were downloaded or extracted.

## Outcome

**No actual HOS binary artifacts were obtained.** The workspace and the Phase 25 local backup search contain no BrowserDll NCA/SystemData, openWeb NCA/NSO/NPDM, NetFront NRO, or firmware container. There are therefore no local target-binary SHA-256 values and no NSTool, PROJECT ZERO parser, or Ghidra run against HOS files. The only `.nro` files remain the PROJECT ZERO homebrew application.

The public NinUpdates database provides more than title names: its 23.0.0 entry links generated text outputs from NCA/NPDM inspection for the exact BrowserDll and openWeb title revisions. Those reports identify components, module metadata, the parsed openWeb NPDM service/SVC list, and BrowserDll RomFS NRO paths. They are **derived text reports, not binaries**; they do not include the executable bytes or an independently computed hash for the NSO/NRO content. They appear to derive from third-party processing of an update package; source provenance and redistribution license for binaries are not established. We used only non-secret metadata fields and did not copy the public-key/signature or encrypted key-area values into this report.

## Exact component identities and HOS 23.0.1 relationship

| Component | Title ID | 23.0.0 candidate revision | Public report evidence | 23.0.1 status |
|---|---|---|---|---|
| BrowserDll SystemData | `0100000000000803` | `v1543505072` / `23.0.0.1200` | NinUpdates 2026-09-10 title list links a Meta NCA report and a Data NCA report for this ID/revision. The Data NCA report says NCA3, Content Type Data, Title ID matches, SDK 23.2.2.0, content size `0x2838800`, RomFS section, and records the files extracted by that report's processing. | The 2026-10-01 23.0.1 NinUpdates title list enumerates changed-title outputs for IDs `0100000000000039`, `0100000000000809`, and `0100000000000816`; it does not list `0803`. Switchbrew's 23.0.1 change page lists `sdb` and `SystemVersion:/file`. This supports that the 23.0.1 update did not replace BrowserDll and the effective candidate remains the 23.0.0.1200 content. It is not a byte-for-byte comparison with the user's console. |
| openWeb applet executable and paired NPDM | `0100000000001043` | `v1543505072` / `23.0.0.1200` | NinUpdates links `getinfo.info` and `main_npdm_parseout.info` for this exact title/revision. Module path reports `openweb.nss`, 64-bit, FS SDK 23.2.2, 279 symbols, and pointer authentication / CFI build marked yes. Parsed NPDM states title name `openWeb`, title ID `0100000000001043`, version `23.0.0-0 (1543503872)`, and application type Applet. | The same 23.0.1 update title list does not list `1043`, and the Switchbrew 23.0.1 changelog does not identify an openWeb update. This is strong public evidence that the 23.0.0.1200 openWeb component was carried forward into HOS 23.0.1, but no exact installed content hash or Mariko device read-back was obtained. |

The component revision is not the full HOS version. `23.0.0.1200` is the title revision listed for both components; the parsed openWeb NPDM reports its own version field as `23.0.0-0`. No source reviewed provides a Nintendo-signed manifest that binds these exact binaries to this particular Mariko console.

## BrowserDll contents identified from the public NCA report

The BrowserDll Data NCA report for `0100000000000803/v1543505072` lists these paths under `nro/netfront`:

- `core_0/Default/cfi_nocfi/`: `cairo_wkc.nro.lz4`, `libfont.nro.lz4`, `oss_wkc.nro.lz4`, `peer_wkc.nro.lz4`, `webkit_wkc.nro.lz4`
- `core_3/Default/cfi_nncfi/`: the same five NRO names
- `buildinfo/buildinfo.dat`

The same listing includes browser support data such as certificate bundles, effective-TLD data, ICU data, media-control resources, URL blocklists, fonts, layouts, and message resources. Switchbrew documents that web applets share the BrowserDll SystemData OSS NROs. The path names show separate CFI directory variants, but are not sufficient to infer selection conditions or implementation semantics.

The NCA report also gives the 32-hex content identifiers in filenames (`7f186be8…` for a Meta NCA and `6c9e6a19…` for a Data NCA). These are **not SHA-256 checksums**; no raw NCA was present to hash. The report describes standard crypto and an encrypted NCA. No update container or decryptable payload was downloaded.

## openWeb NPDM metadata from the public parsed report

The NinUpdates `main_npdm_parseout.info` for `0100000000001043/v1543505072` reports:

- META/ACI0 title identity: `openWeb`, `0100000000001043`; NPDM version `23.0.0-0 (1543503872)`; retail flag set; applet application type; main-thread priority 40 and stack size `0x10000`.
- Service access entries include `appletAE`, `bsd:a`, `fsp-srv`, `hid`, `nifm:s`, `ns:web`, `nvdrv:a`, `sfdnsres`, `ssl`, `set`, `set:sys`, `time:u`, and others. This is the **declared access-control list in a generated parse report**, not proof each service is used or reachable in every applet launch mode.
- The generated SVC list includes `svcMapPhysicalMemoryUnsafe` and `svcUnmapPhysicalMemoryUnsafe` (plus common memory, thread, IPC, and synchronization SVCs). Their presence in a parsed allowed-SVC list alone does not demonstrate arbitrary physical-memory access, successful invocation, a kernel defect, or an exploit primitive. No SVC was called on hardware.
- Filesystem access-control output includes several content mount permissions and system-save-data entries. This is not evidence that the web applet can read arbitrary user files or that any data was accessed.

These observations are technically useful for scoping future review, but the raw NPDM is not available locally, the project parser did not independently parse it, and no executable code or service IPC was inspected. No vulnerability is claimed.

## Search and acquisition log

### Local sources

The project/sibling project tree and Phase 25 search of `/Users/adamkrisko/Downloads`, `/Users/adamkrisko/Desktop`, and `/Users/adamkrisko/Documents` found no matching firmware containers or browser artifacts. No matching backup was found. Candidate search terms and formats included both title IDs, BrowserDll/openWeb/NetFront/WebApplet names, `.nca`, `.nso`, `.npdm`, `.nro`, `.nsp`, `.xci`, `.cnmt`, and `.pfs0`.

### Public sources searched

| Source | What it contains | Acquisition decision |
|---|---|---|
| [NinUpdates 23.0.0 Switch report](https://yls8.mtheall.com/ninupdates/reports.php?date=2026-09-10_05-05-06&sys=hac) and [23.0.0 title list](https://yls8.mtheall.com/ninupdates/titlelist.php?date=2026-09-10_05-05-06&reg=G&sys=hac&tid=0100000000000045) | Per-title text outputs, including BrowserDll NCA summaries/file-path listing and openWeb `getinfo`/NPDM parser output. | Used as third-party metadata evidence only. No raw firmware or executable download link was exposed in the reviewed title-list page; outputs do not provide file SHA-256. No clear license for underlying proprietary binaries. |
| [NinUpdates 23.0.1 report](https://yls8.mtheall.com/ninupdates/reports.php?date=2026-10-01_01-02-36&sys=hac) and [23.0.1 title list](https://yls8.mtheall.com/ninupdates/titlelist.php?date=2026-10-01_01-02-36&sys=hac) | Changed-title listing exposes `sdb` (`010...0039`), SystemVersion (`010...0809`), and SystemUpdate metadata (`010...0816`); it does not list BrowserDll `0803` or openWeb `1043`. | Used to establish the update delta by public title metadata. Does not prove bytes in the console's installed storage. |
| [Switchbrew 23.0.0](https://switchbrew.org/wiki/23.0.0), [23.0.1](https://switchbrew.org/wiki/23.0.1), [title list](https://switchbrew.org/wiki/Title_list), and [Internet Browser](https://switchbrew.org/wiki/Internet_Browser) | Documents title revisions, update deltas, BrowserDll's shared OSS NRO role, and browser architecture. | Technical documentation only; no binary or independently verifiable per-file digest. |
| [Atmosphère issue 2872](https://github.com/Atmosphere-NX/Atmosphere/issues/2872) | Community reports about applet behavior on 23.0.0 and interaction with BrowserDll/NetFront paths. | Supporting lead only; not used to claim exact binary identity or vulnerability. |
| [Nintendo official update information](https://www.nintendo.com/en-gb/Support/Troubleshooting/Nintendo-Switch-System-Update-Information-1445507.html) | Official 23.0.1 release date and end-user change note; directs system update through the console. | Official update path, but no host-side firmware package, per-title manifest, or browser binary hash. |
| Third-party firmware mirrors and GitHub firmware releases | Public listings for HOS packages exist. | Not downloaded: clear redistribution authorization/licensing and independently verifiable source chain were not demonstrated. A package name/checksum posted by a mirror is not an official Nintendo signature or an analyzable NSO. |

## What was actually analyzed

No binary artifact was acquired or analyzed with NSTool or PROJECT ZERO. The actual inputs reviewed were publicly hosted parser-output text and community version/change metadata. This supports the following narrower statements:

1. The best candidate for HOS 23.0.1 is openWeb `0100000000001043` plus its title-matched NPDM at revision `23.0.0.1200`, paired with BrowserDll `0100000000000803` at revision `23.0.0.1200`.
2. Public update deltas for 23.0.1 do not list either target title as changed, supporting carry-forward from 23.0.0.
3. The openWeb parse output exposes a useful declared service/SVC map and a build-info claim (`64-bit`, `openweb.nss`, SDK 23.2.2, 279 symbols, PAC/CFI yes).
4. BrowserDll metadata identifies NetFront/WebKit NRO filenames, including LZ4-suffixed variants in CFI-related directories.

None of these provides executable-region bytes, import tables, actual symbol names, disassembly, per-file SHA-256, or direct confirmation of the user's T210B01 console content. The version-to-HOS relationship is established by update-title delta metadata, not by reading a 23.0.1 console or authenticating the package cryptographically.

## Decision and next step

**The artifact gate remains closed for code analysis.** Public sources provide reproducible component metadata but not a legally cleared, locally analyzable binary set. Do not feed the `.info` reports to binary parsers or label them as NSO/NRO analysis. The minimum next input is an authorized, unencrypted BrowserDll Data NCA/SystemData extraction and openWeb executable + matching NPDM with provenance and byte hashes, or an explicitly redistributable research dataset containing those files. Until such input exists, the next safe action is to preserve the exact public metadata URLs and wait; no additional parser work or synthetic test is justified.
