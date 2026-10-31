# Phase 3 — consolidated findings of five agents

## Coordinator

All five separate research reports were compared. Consensus: sources do not show reproducible software homebrew chain for Switch V2 Mariko/T210B01 + HOS 23.0.1. This is a circumscribed negative public search result, not proof that the error does not exist.

The list of specific historical items and the exact fields are in [database](VULNERABILITY_DATABASE.md) and [JSON](vulnerabilities.json). Unknown fields remained unknown. Special: Switchbrew's WebKit table has empty successful exploit results for the listed CVEs; therefore, a confirmed Switch RCE is not attributed. nvhax source describes code execution in the context of nvservices after primitive combining; this alone does not confirm Mariko applicability or the full kernel chain. nspwn source says arbitrary code execution with full system privileges after access to lr, but target hardware/firmware specific compatibility unconfirmed.

## Agent A — Mariko hardware and boot

- Mariko uses new Boot ROM and documented IROM mitigations. Fusée Gelée/CVE-2018-6242 is hardware fixed; RCM mode itself is not an exploit.
- NH Guide lists patched/Mariko Caffeine only for 4.1.0, then modchip.
- T210B01/HOS 23.0.1 chain not found; individual fuse state was not detected.
- Certainty: medium to high for a documented difference; community technical documentation, not a test of a specific Switch V2 unit.
- Details: [phase3_A_boot.md](../research/agents/phase3_A_boot.md).

## Agent B — Horizon OS and kernel

- Historical kernel/sysmodule errors have old patch versions listed. Some entries expressly speculative or not tested on hardware; the database maintains these restrictions.
- HOS 23.0.0 bundles ldn update with CVE-2026-82079 fix; The Nintendo advisory uses the general wording of a possible information leak.
- 23.0.1 changelog describes a functional fix, sdb update; The Switchbrew security flaws field remains empty. We do not claim another security fix.
- Details: [phase3_B_horizon.md](../research/agents/phase3_B_horizon.md).

## Agent C — WebKit and network interfaces

- Historical WebKit CVEs: 2.1.0, 3.0.1, 6.1.0, 7.0.0 fixes by Switchbrew. The successful exploitation result in the table is empty, therefore the successful Switch RCE remains unknown.
- ns2jb WebKit path is Switch 2-only research that did not reach sysmodule code execution; the successful path issued is different. The author's Switch 1 mention has no revision/FW or public package.
- Broadpwn is only listed as a relevant Wi-Fi class; Switchbrew itself says that controller code execution is untested on Switch.
- Details: [phase3_C_attack_surface.md](../research/agents/phase3_C_attack_surface.md).

## Agent D — REA and Ghidra

- Ghidra 12.1.4, JDK25 and ARM64 native component checks successful after setting env; the analyzer and the ARM64 fixture were non-invasively started.
- Agent D noted the Ghidra provider as available. However, the subsequent coordinator binary_session returned the old server environment and Ghidra unavailable, while the live identity server shows the process running before the Codex config change. CLI doctor with explicit paths passed. Conservative result: REA MCP connection works, but provider activation in live session is not unequivocally verified without Codex restart. REA firmware parser unsupported_host on macOS.
- Target binary analysis failed without artifact firmware.
- Details: [phase3_D_tooling.md](../research/agents/phase3_D_tooling.md).

## Agent E — independent auditor

- Fixed exaggerated claims about WebKit: source table has no confirmed Switch code-execution results.
- Confirmed nvhax code execution in sysmodule context and nspwn full system privileges with existing lr access; neither proves the target Mariko 23.0.1 chain.
- Confirmed the ns2jb boundary and the difference between the CVE-2026-82079 fix in 23.0.0 and the 23.0.1 working fix.
- Details: [phase3_E_audit.md](../research/agents/phase3_E_audit.md).

## Decisions of the coordinator

1. No agent has brought accurate reproducible PoC for Mariko + 23.0.1.
2. Switch 2 and original Erista proofs do not transfer to Mariko without explicit compatibility.
3. Every NULL field in vulnerability JSON means unknown/undocumented range, not "no".
4. HOS 23.0.1 safety claim is limited: there is no documented chain in reviewed public sources; proprietary binary diff failed.

## Coordinated continuation — 2026-10-30

### Workstreams

| Role | State | Independent Output |
|---|---|---|
| System Architecture | Finished | Switchbrew describes the system web applets and general service ACL differences, but the exact config/ACL for WifiWebAuthApplet HOS 23.0.1 was not documented. Erista/Mariko BootROM differences are a family fact, not a specific console measurement. |
| RE specialist | Completed | The project is missing HOS system executable and image artifacts. The only ELF object identified is the AArch64 devkitPro/newlib object `references/vendor/devkita64-newlib-4.6.0.20260123-4/libsysbase_dirent.o`, SHA-256 `4b3b4fdb38ef370402120d9964d39f2b487e9c34ce1bf250c39eb3eb767fd7de`; it's not a Nintendo code. Ghidra 12.1.4 available; REA 6.8.0 works for supported actions, firmware extraction unsupported_host. The Capstone 5.0.7 and LIEF `1.0.0-d05b3499b` runtimes differ from the manifest given by Capstone 5.0.9 and LIEF 1.0.0. |
| Public Vulnerabilities | Completed | Nintendo advisory CVE-2026-82079 lists fix in HOS 23.0.0; does not mention Mariko/T210B01. The 23.0.1 page lists a functional fix and is not a full security changelog. |
| Runtime and Interfaces | Completed | New physical WifiWebAuthApplet log captures passive probe, runtime API and peer network tests. The corrected HTTP HEAD server is currently verified on the host, not on the Switch. |
| Independent Skeptic | Completed | Confirmed that bridge inventory reads descriptors/prototype chain to depth 8, accessor does not read values ​​and does not call methods. The other page intentionally does DOM/Fetch/XHR/WebSocket tests. Negative `present:false` only applies to selected names and context; log/UA is not a cryptographic identity. Found resource HEAD 501: missing `do_HEAD` on our server. |
| Engineer/artifact audit | Partially completed | Read-only audit completed; the subsequent architecture task ended at the Codex usage limit. He confirmed the absence of the HOS artifact and pointed out the outdated number of lines and the bad report link, which the coordinator corrected. |

### Coordinator's summary

- Observed user run is classified as physical applet run by user confirmation and correlated UA/HTTP log; client UA/JSON are not cryptographically authenticated. Mariko/T210B01 remains unverified.
- The passive bridge test did not find 8 named globals. It is not proof of the complete absence of native bridge or vulnerability.
- `HEAD 501` was a bug in our harness/server, not a target find. The repair was reproduced by the host; a physical rerun is an optional additional protocol check.
- PZ registration register is in `reports/EVIDENCE_REGISTER.md`; this registry is the primary list of classes and IDs. Not to be confused with the E0–E3 scale in `PROJECT_ZERO/README.md`; the registry lists A–F separately for this phase.
- Agent findings and exact limits are summarized here; full new phases/duplicate reports were not created.

## Red team review — 2026-10-31: SmileBASIC / ns2jb

Five independent roles were actually launched: Horizon Architecture, Application Desktop/SmileBASIC, Mariko Platform, Reverse Engineering and Independent Skeptic. They all submitted their results. GitHub was not used, no exploit was downloaded or run, and Nintendo data was not modified.

- The official Nintendo listing identifies SmileBASIC 4 as a Switch title and states supported compatibility with Switch 2. This is app availability, not proof of a vulnerability.
- The author's article from 10/18/2026 defines the released ns2jb as a tethered software-only jailbreak for Switch 2 on 23.0.1. In conclusion, the author claims that he also tested "the exploit" on Switch 1, but did not package this version. It does not define the model/SoC, firmware, test scope or reproducible result of Switch 1.
- The public GitLab README is labeled "Switch 2 FS demo" and explicitly mentions Switch 2 only and system 23.0.1. It does not confirm the published Switch 1 variant.
- The skeptic pointed out the ambiguity of the scope of the author's Switch 1 sentence: the article describes Switch 1 SmileBASIC research in one part and the sysmodule/FS chain mostly in the context of Switch 2; the final sentence doesn't say if this entire chain worked on Switch 1.
- No independent public evidence in reviewed sources identifies Erista vs Mariko, T210B01/Tegra214 or HOS 23.0.1 for Switch 1. The previous Phase 3 report already noted a similar authorship claim, so this is not a new technical finding or a change to the Mariko feasibility verdict.
- A targeted audit of other stock app/parser findings did not discover a new public item beyond the already registered CVE-2026-82079 and the historical database; this is a bounded search, not a proof of the absence of non-public errors. Without HOS executable/NPDM, parsers of a specific build cannot be audited.

Agent D revalidated local artifact gate: HOS executable/NPDM/system image not present; the only relevant ELF is the devkitPro/newlib object. Ghidra 12.1.4 and REA 6.8.0 are available, but target binary analysis is not possible. The exact metadata/limits are in [register evidence](EVIDENCE_REGISTER.md), entry `PZ14-SMILE-01`.
