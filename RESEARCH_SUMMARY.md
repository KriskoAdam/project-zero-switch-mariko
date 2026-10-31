# PROJECT ZERO — Unified Research Summary

**Last consolidated:** 2026-10-31  
**Target:** stock original Nintendo Switch V2 / Mariko, user-reported HOS 23.0.1  
**Goal:** identify and independently validate a software-only route from stock firmware to unsigned native code/homebrew, without a modchip.

> **Current verdict: NO JAILBREAK DEMONSTRATED.** No vulnerability, exploit primitive, privilege escalation, kernel exploit, or complete stock-to-homebrew chain has been confirmed on Mariko / HOS 23.0.1 by this project. This is a statement about the evidence collected, not proof that no undisclosed vulnerability exists.

This file replaces the repository's many overlapping narrative phase reports. It is the single maintained narrative record of project findings. Source code, tests, machine-readable results, and sanitized raw captures remain in their existing locations as supporting evidence.

## 1. Target and confidence boundaries

- The target is described by the owner as a Nintendo Switch V2 running HOS 23.0.1.
- Mariko / T210B01 / Tegra214 is the research target, but the exact silicon identity of the physical console has **not** been independently verified.
- The HOS 23.0.1 version is owner-reported and also appeared as a device-version string in MTP DeviceInfo. That string is device-provided metadata, not cryptographic firmware attestation.
- USB VID/PID and product strings identify a Nintendo Switch USB function, not a particular Switch revision or SoC.
- Erista V1, Mariko V2, Switch Lite, OLED, and Switch 2 findings are not interchangeable. Compatibility must be demonstrated for the exact target.

## 2. Executive findings

| Area | What is established | What is not established | Current decision |
|---|---|---|---|
| Boot chain / Mariko | Public technical documentation describes Mariko BootROM differences and mitigation of the original Fusée Gelée route. | No new stock software entry point or boot-chain bypass on this console. | No software-only boot path demonstrated. |
| Wi-Fi Web Auth / browser | A benign local page ran in a physical stock applet session; ordinary DOM/network APIs were observed. Public metadata identifies openWeb and BrowserDll candidate components. | No browser RCE, sandbox escape, native bridge, exact target binary analysis, or Mariko-specific vulnerability. | Best current software-surface research lead, blocked by executable artifacts. |
| USB / MTP | Physical USB enumeration and standard read-only MTP metadata operations were observed. | No system-file access, writable storage, arbitrary command interface, exploit primitive, or homebrew path. | Closed/deprioritized absent new evidence. |
| libnx / homebrew ABI | A host-side callback-capacity hypothesis was checked against a public library contract and closed within the tested scope. | No stock HOS bug; it requires homebrew already running. | Not a first-entry candidate. |
| Differential/model lab | The framework detected intentionally injected defects in synthetic models and minimized their traces. | These are not Horizon OS defects and provide no Mariko evidence. | Tooling validation only. |
| Binary inspection tooling | Host-side ELF disassembly and bounded NSO/NRO/KIP/NPDM metadata parsers have tests and differential checks on synthetic fixtures and local homebrew. | No complete Horizon loader, full decompression/signature validation, or HOS executable disassembly. | Useful pre-analysis tooling, not a firmware finding. |
| Public exploit research | Reviewed public claims including ns2jb/SmileBASIC and historical Switch vulnerabilities with platform-scope cautions. | No reproducible public chain matching Mariko / T210B01 + HOS 23.0.1. | Recheck only when new primary evidence appears. |

## 3. Physical console observations

### 3.1 Wi-Fi Web Auth applet

A benign local test page was opened in the stock Wi-Fi authentication applet during a user-confirmed physical session. Correlated logs recorded ordinary DOM, Fetch/XHR and WebSocket behavior. The passive bridge inventory checked selected property names and prototype descriptors to a bounded depth; it did not call bridge methods or read accessor values.

A later probe recorded that selected names such as WebAssembly, Atomics, and SharedArrayBuffer were unavailable in that session, while Worker and MessageChannel were present. These are narrow observations for that page and applet configuration only. They do not prove the complete absence of a native bridge, do not establish a vulnerability, and do not authenticate the console's SoC. The test server's earlier HTTP HEAD 501 was a bug in the project's own server; the host-side fix was verified separately.

**Result:** ordinary web runtime behavior observed; no exploit or native execution.

### 3.2 USB enumeration and MTP

Passive macOS inspection initially found no device node. After the user reconnected the cable, macOS enumerated a Nintendo Switch (VID 057e, PID 201d) with one MTP interface (class/subclass/protocol 06/01/01) and three endpoints. A separate descriptor reader recorded:
- 0x81: bulk IN, 512-byte max packet;
- 0x01: bulk OUT, 512-byte max packet;
- 0x82: interrupt IN, 24-byte max packet.

The standard UI transition out of “Copy to a Computer via USB” changed the visible USB function to HID (PID 2000, class 03/00/00); returning to the official copy screen restored MTP. No HID report data was read or sent.

With libmtp 1.1.23, standard read-only MTP discovery reported device version 23.0.1, storage description Album, access mode read-only, and a root object count of 3. The storage capacity/free-space values were maximum-value sentinels, not actual capacities. The tool sent only DeviceInfo, GetStorageIDs, GetStorageInfo, and root GetNumObjects requests after checking advertised operations. It did not enumerate object names, retrieve file contents, or perform write/delete operations.

Across nine successful sessions, the root count remained 3 and standard queried responses were successful. Storage IDs changed after user-controlled MTP mode restarts but remained stable within repeated sessions in each mode. The cause is unknown; no security impact was established. A later live capture also recorded endpoint enumeration but did not send protocol data.

**Result:** ordinary, limited MTP/HID function changes and read-only metadata behavior observed; no system storage access or exploit primitive. Do not treat MTP as a demonstrated PC-to-console file-write path.

### 3.3 Hardware identity

None of the USB captures independently identifies V2/Mariko/T210B01. The target revision remains owner-described, not silicon-attested. Do not upgrade that status without new evidence.

## 4. Firmware and browser artifact research

### 4.1 Correct component mapping

Public title/update metadata reviewed in Phase 25/26 supports this mapping for HOS 22.0+:
- Wi-Fi Web Auth applet ID 0x19 maps to **openWeb**, title ID 0100000000001043.
- **BrowserDll** is separate shared SystemData, title ID 0100000000000803.

Do not confuse openWeb with the older WebApplet title 010000000000100A, or treat BrowserDll as the applet executable itself.

### 4.2 Public metadata candidates

Third-party NinUpdates parsed text outputs for title revision v1543505072 / 23.0.0.1200 report:
- openWeb: openweb.nss, 64-bit, FS SDK 23.2.2, 279 symbols, PAC/CFI build indicators marked yes; parsed NPDM identifies an applet and lists declared service/SVC access.
- BrowserDll Data NCA: RomFS paths include webkit_wkc.nro.lz4, oss_wkc.nro.lz4, peer_wkc.nro.lz4, libfont.nro.lz4, and cairo_wkc.nro.lz4 in CFI-related directories, plus buildinfo/buildinfo.dat.

The HOS 23.0.1 public title delta reviewed does not list openWeb or BrowserDll as changed, supporting (but not cryptographically proving) carry-forward of the 23.0.0.1200 candidate components. The component title revision is not the full HOS version. The generated parse reports are third-party text metadata, not executable binaries, signed Nintendo manifests, or independently verified file hashes.

The parsed openWeb NPDM text lists svcMapPhysicalMemoryUnsafe and svcUnmapPhysicalMemoryUnsafe among allowed SVCs. This is only an access-control metadata observation. It does not show that the applet invokes those SVCs, can map arbitrary physical memory, or has an exploitable kernel primitive.

### 4.3 User-provided candidate NCA containers

The Phase 26 local inventory recorded 238 files (about 326 MB) in the user-provided folder /Users/adamkrisko/Downloads/Firmware.23.0.1/. Four candidate files matched public content-ID filenames and expected sizes:

| Candidate | Size | Local SHA-256 |
|---|---:|---|
| openWeb program NCA c1cad975a7fe0a2eb363410723d967e4.nca | 7,104,000 B | c1cad975a7fe0a2eb363410723d967e4c08be3467791248bd26e315e4b2c130b |
| openWeb Meta/CNMT 05b2410a157592b00710eba92a083f6f.cnmt.nca | 3,584 B | 05b2410a157592b00710eba92a083f6ff65a60dce43ac87e5a5b1a6238607fd1 |
| BrowserDll Data NCA 6c9e6a19c7d6a8410c477e303fbc97ba.nca | 42,174,464 B | 6c9e6a19c7d6a8410c477e303fbc97bad67e7576776e7f38c82919ec88db09a0 |
| BrowserDll Meta/CNMT 7f186be8a6315af1b6259a891a84c3f9.cnmt.nca | 3,584 B | 7f186be8a6315af1b6259a891a84c3f94031b9d8b4d383041d79c35e939d76d1 |

These hashes identify the supplied encrypted containers only. Their filenames and sizes do not independently prove provenance, authenticity, exact HOS version, or Mariko applicability. The containers were not committed to this repository.

NSTool v1.9.2 was run in a read-only identification attempt with an empty keyset. It failed to load an NCA Header Key and reported the input type undetermined. This does **not** mean the files are invalid. No NCA internals were parsed, no decryption or extraction was performed, and no NSO/NRO/NPDM executable bytes were recovered. Thus the artifact gate for actual binary analysis remains closed.

## 5. Parser, reverse-engineering and lab tooling

### 5.1 ARM64 disassembler (Phase 18)

The project repaired scripts/inspect_arm64_binary.py and tested it against a local PROJECT ZERO homebrew ELF (SHA-256 9798cc4c8c2089c859f372f2bc3edfbc23a0d3d32512ed086f2aea12f6aea3bd), not Nintendo firmware. It now uses ELF function symbols and bounded control-flow traversal, avoids decoding embedded data as instructions, marks inferred/heuristic ranges, and reports undecoded regions. Its output was compared with Apple objdump and Ghidra's direct disassembly on the same host ELF. Ghidra's full auto-analysis timed out during DWARF processing; the direct import/disassembly comparison succeeded.

Seven focused tests and the then-current project suites passed. This validates host ELF behavior only, not NSO/HOS/Mariko compatibility.

### 5.2 Switch artifact metadata inspector (Phases 19 and 23)

scripts/inspect_switch_artifact.py implements a bounded, read-only subset for NSO, NRO, KIP1, NPDM and ELF:
- NSO: header, segments, module ID/name, rodata metadata, hash flags and LZ4/ZBIC flag interpretation;
- NRO: header, segment geometry, compression metadata, NRA0/ASET bounds;
- KIP1: segment and supported kernel-capability descriptor metadata;
- NPDM: META, ACI/ACID bounds, SAC service entries and supported kernel-capability descriptors;
- ELF: program-header metadata, with AArch64 disassembly delegated to the separate ELF tool.

Phase 23 corrected the ACID body offset to +0x200, added descriptor parsing and corrected ZBIC selector interpretation. The project compared output against NSTool v1.9.2 on the local homebrew NRO and constructed synthetic fixtures. Agreement applies only to those tested inputs.

**Important limitations:** no LZ4/ZBIC NSO decompression, NRO compression decompression, KIP BLZ decompression, ACID signature verification, full segment hash verification, FAC rights validation, Horizon loader emulation, or proof of console acceptance. A valid-subset result is not proof of authenticity or loadability.

### 5.3 Test results

Recorded results across the phases include:
- Phase 18 focused disassembler tests: 7 passed.
- Phase 19: 25 workspace + 11 lab + 6 Phase 14 validator tests = 42 passed.
- Phase 23: 20 focused format-inspector tests; 33 full workspace + 11 lab + 6 Phase 14 validator tests = 50 passed across those suites.

These are phase-specific historical counts and test sets overlap. Do not add them together as unique tests or imply they test Nintendo firmware. They validate code, synthetic fixtures, and local homebrew inputs.

### 5.4 Synthetic differential lab

The lab intentionally inserted faults into toy reference/candidate models and demonstrated that the engine could find and minimize:
- handle reuse after open → close(0) → open;
- pending state after prepare → cancel;
- missing idempotency after send → lose_ack → retry.

Independent model/oracle checks were used within the documented synthetic scope. These defects were deliberately planted. **No Horizon OS anomaly was verified.** The model catalog contains many unexecuted hypotheses; an unexecuted or unrefuted model hypothesis is not a platform result.

## 6. Public vulnerability and exploit-claim review

- The original Fusée Gelée route is associated with older unpatched Erista hardware; public Mariko BootROM differences mean it cannot be assumed to work on patched V2.
- Historical Switch WebKit, Wi-Fi, kernel and service vulnerabilities must be checked against exact component version, hardware, firmware and exploit-chain prerequisites. A CVE affecting a different Switch revision or a browser-only crash is not proof of Mariko native execution.
- The reviewed public WebKit tables did not establish a successful Switch code-execution result applicable to this target.
- Public ns2jb / SmileBASIC material reviewed was released as a Switch 2-scoped research/demo path. An author statement about some Switch 1 testing did not specify a reproducible Switch 1 model, SoC, firmware range or complete chain. It therefore does not establish Mariko/T210B01 + HOS 23.0.1 compatibility.
- Claims such as nvhax or nspwn describe capabilities under their own prerequisites; they do not by themselves establish a stock Mariko entry point or a complete chain for this target.
- Nintendo's HOS 23.0.1 user-facing update notes are not a full security changelog and do not publish browser binaries or hashes. Do not infer that no security changes occurred merely because the public note is brief.

**Review conclusion:** no reviewed public source supplies a reproducible software-only jailbreak chain for the exact Mariko / HOS 23.0.1 target.

## 7. Closed or deprioritized leads

1. **Phase 7 libnx callback capacity:** closed within the public callback contract and host test; library-side, not a stock HOS entry point.
2. **Phase 12 benign Web Auth probe:** ordinary runtime behavior only; no exploit or native bridge established.
3. **Phases 13–14 USB/MTP:** read-only metadata behavior consistent across sessions; Storage ID changes correlate with user-controlled mode restarts and have no demonstrated security impact.
4. **Synthetic lab anomalies:** intentionally injected into models; not platform vulnerabilities.
5. **Generic/local ELF analysis:** validates host tooling only.
6. **ns2jb Switch 1 extrapolation:** insufficient platform/version/chain evidence for Mariko.

Reopen a closed lead only when new evidence changes its technical basis.

## 8. Current blockers

1. No independently verified exact silicon identity for the target console.
2. No decrypted/inspectable openWeb executable and matching NPDM with verified build identity.
3. No same-build BrowserDll/SystemData NRO payloads available for actual code analysis.
4. No trusted manifest/read-back tying candidate files to the target console's installed content.
5. Parser pipeline still lacks several decompression, signature and loader-semantic capabilities.
6. No confirmed vulnerability or exploit primitive from any stock Mariko-reachable component.
7. No demonstrated route from a userland foothold through required privilege boundaries to unsigned native code.

## 9. Research priorities

Prioritize evidence, not report volume:

1. Establish exact target hardware identity and firmware using reliable, non-invasive evidence.
2. Resolve the lawful artifact/provenance gate for openWeb and BrowserDll; preserve hashes and source chain.
3. Once inspectable binaries exist, validate decompression and parsing against an independent implementation before disassembly.
4. Map real openWeb ↔ BrowserDll ↔ IPC/service interactions from actual matching-build code and metadata.
5. Test narrowly scoped parser/service hypotheses with host-side fuzzing or authorized safe experiments; distinguish crashes from controlled code execution.
6. For any candidate issue, establish reachability from stock state, exact affected versions, exploit primitive, privilege boundary crossed, and independent reproduction.
7. Update this single summary only when new evidence changes a finding, status, or priority.

## 10. Evidence labels and contribution rules

Every new claim must use one of these labels:
- **CONFIRMED:** directly reproduced with a documented method and suitable evidence.
- **OBSERVED:** directly seen in a bounded physical or host measurement; no broader inference.
- **INFERRED:** follows from cited evidence but was not directly measured.
- **HYPOTHESIS:** technically plausible but unverified.
- **NOT TESTED:** no experiment or evidence.
- **REFUTED (SCOPE-LIMITED):** contradicted only under the stated test conditions.

Every contribution should record target scope, source URLs and revisions, tool versions, hashes, method, sanitized output, limitations, exploit relevance, and a reproduction path. AI-generated output is a lead until independently checked. Do not present model output, synthetic fixtures, third-party metadata, or a local homebrew binary as Nintendo HOS evidence.

## 11. Supporting material retained in the repository

The narrative record is this file. Supporting non-narrative materials remain:
- scripts/, tools/, lab/, tests/: source code, diagnostics, parsers, experiments and test suites.
- reports/raw/ and reports/project-zero-local/raw/: sanitized raw USB/MTP captures and machine-readable measurements.
- reports/vulnerabilities.json: machine-readable public vulnerability research database.
- manifests/: machine-readable test/input manifests.
- research/agents/: scoped agent task briefs and work products where retained outside the consolidated reports.
- references/: third-party source excerpts and notices.

Raw evidence and executable research tooling are not redundant narrative reports and should not be deleted merely to reduce documentation clutter.

## 12. Primary public references

- Nintendo Switch System Update Information: https://www.nintendo.com/en-gb/Support/Troubleshooting/Nintendo-Switch-System-Update-Information-1445507.html
- Switchbrew Internet Browser: https://switchbrew.org/wiki/Internet_Browser
- Switchbrew 23.0.0: https://switchbrew.org/wiki/23.0.0
- Switchbrew 23.0.1: https://switchbrew.org/wiki/23.0.1
- Switchbrew Title list: https://switchbrew.org/wiki/Title_list
- Switchbrew NSO: https://switchbrew.org/wiki/NSO
- Switchbrew NRO: https://switchbrew.org/wiki/NRO
- Switchbrew KIP1: https://switchbrew.org/wiki/KIP1
- Switchbrew NPDM: https://switchbrew.org/wiki/NPDM
- NSTool (MIT): https://github.com/jakcron/nstool
- NinUpdates reports: https://yls8.mtheall.com/ninupdates/reports.php
- Atmosphère issue 2872: https://github.com/Atmosphere-NX/Atmosphere/issues/2872

Community-maintained metadata and format documentation are secondary technical references, not Nintendo-authenticated binary manifests. Recheck current pages before making time-sensitive compatibility claims.

## 13. New reverse-engineering hypotheses (2026-10-31)

The following leads were proposed by an external AI-generated research plan. They have **not** been independently verified against the target's matching HOS 23.0.1 binaries. They are recorded to guide falsifiable investigation, not as findings or evidence of an available exploit chain.

| Lead | Status | What must be established before upgrading its status |
|---|---|---|
| `svcMapProcessMemory` could expose memory belonging to the `openWeb` process | **HYPOTHESIS — NOT TESTED** | Identify the exact caller, target process handle acquisition, required handle rights, kernel checks, mapping direction and permissions. Do not infer cross-process read access from the SVC name alone. |
| `fsp-ldr` could provide access to decrypted executable content | **HYPOTHESIS — NOT TESTED** | Identify the relevant service interface and caller authorization in matching-build code; establish what content is returned and under which process/loader conditions. No stock-console access path is currently demonstrated. |
| BrowserDll `Path::Normalize` call sites could expose a path-handling flaw | **HYPOTHESIS — NOT TESTED** | Locate the actual implementation and call sites in the correct BrowserDll/WebKit build; trace attacker-controlled input, normalization semantics, bounds checks and downstream filesystem use. No overflow or filesystem-service bridge is currently demonstrated. |
| `svcMapPhysicalMemoryUnsafe` / `svcUnmapPhysicalMemoryUnsafe` in openWeb NPDM may be security-relevant | **OBSERVED METADATA; SECURITY IMPACT NOT TESTED** | Confirm the SVC descriptors in the exact matching NPDM, then determine whether the executable invokes them and what kernel-enforced constraints apply. An NPDM allowlist entry is not proof of arbitrary physical-memory access. |
| Transfer-memory handling or TLV `0x44` (`TransferMemoryEnabled`) may affect the Web Auth applet path | **HYPOTHESIS — NOT TESTED** | Find the relevant structure/handler in the matching executable, establish the TLV definition and data flow from a reachable input, and test the actual privilege and memory boundaries. Do not infer behavior from names or unrelated source references. |
| A privileged `fs` path could make keyless executable inspection possible | **HYPOTHESIS — NOT TESTED** | First identify a reproducible, authorized stock-state entry point and prove the exact permissions and data path. No `fs` privilege escalation, `FullPermission` path, or decrypted-code dump capability is currently established. |

### 13.1 Required investigation order

1. **Artifact identity and provenance:** identify each candidate NCA by hash, content ID, NCA type, title ID, title version and parsed key-generation field where available. Record the source and confidence. Do not infer every NCA's key generation solely from the HOS release label.
2. **Parser and extraction validation:** document exact tool versions and supported command-line syntax. Validate extraction against a known-good, lawfully available test artifact and an independent implementation. A magic-byte check (`NSO0` or `NPDM`) is only a format sanity check, not proof of correct decryption, provenance, signature validity or target compatibility.
3. **NPDM access-control inventory:** parse SVC, service and filesystem access-control metadata from the matching openWeb NPDM. Label these as declared permissions; separately track actual call sites and kernel-enforced conditions.
4. **openWeb call/data-flow map:** identify actual SVC calls, IPC/service sessions, transferred-memory use and relevant input handlers. Record cross-references and reachable call paths rather than relying on symbol names or AI-generated guesses.
5. **BrowserDll/WebKit map:** identify the exact NRO build and map filesystem-related call sites, path normalization, IPC and service boundaries. Do not assume a `Path::Normalize` vulnerability exists.
6. **Falsifiable tests:** create narrowly scoped host-side tests or authorized non-destructive experiments for a specific parser or input-validation hypothesis. Distinguish a parse error, crash, controlled memory corruption, code execution and privilege escalation; they are different outcomes.
7. **Exploit-chain accounting:** for any candidate issue, document stock-state reachability, affected build, primitive, process context, privilege boundary crossed, mitigations, reproducibility and independent confirmation. Browser code execution alone is not a jailbreak.
8. **Update this report only when evidence changes:** preserve the single-report policy. Add no duplicate narrative report. Keep all unverified leads explicitly marked HYPOTHESIS or NOT TESTED.

### 13.2 Explicit non-claims

This section does **not** establish that:
- keygen 16 is present in every NCA associated with HOS 23.0.x;
- a particular key set is available, valid or sufficient for every candidate NCA;
- an NPDM SVC permission bypasses kernel policy;
- `svcMapProcessMemory` permits arbitrary cross-process reads;
- `fsp-ldr` exposes decrypted code to an unprivileged stock process;
- a `Path::Normalize` overflow exists or is reachable;
- an `fs` exploit or keyless dump route exists on Mariko / HOS 23.0.1.

No console secrets, key files, decrypted Nintendo binaries or proprietary executable artifacts should be committed to this repository.
