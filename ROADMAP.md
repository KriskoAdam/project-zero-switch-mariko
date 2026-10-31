# PROJECT ZERO Roadmap — Mariko Software-Only Jailbreak

The destination is a reproducible software-only jailbreak for Nintendo Switch V2 / Mariko: a path from a stock console to unsigned native code execution and homebrew, without a modchip or hardware modification.

The roadmap describes the research path toward that result. Milestones are goals, not claims that the relevant exploit stages already exist.

## Phase 1 — Establish the exact target

- Confirm the console revision and SoC using reliable, non-invasive evidence.
- Record the exact Horizon OS version and relevant system configuration.
- Separate Mariko-specific results from Erista V1, Switch 2, and other firmware research.
- Build a compatibility matrix for every candidate lead.

**Exit condition:** the hardware and firmware target are precisely identified.

## Phase 2 — Find a stock-software entry point

- Map software components reachable during ordinary stock-console use.
- Investigate plausible applet, browser, service, and protocol entry surfaces.
- Review public vulnerability research for exact hardware and firmware compatibility.
- Prioritize leads that can be reached before unsigned homebrew is already running.

**Exit condition:** at least one concrete candidate can be tested from a stock starting state.

## Phase 3 — Validate a vulnerability

- Turn the candidate into a narrowly scoped, repeatable experiment.
- Establish whether the behavior is a real flaw rather than normal interface behavior.
- Determine affected component, firmware range, and security boundary.
- Seek independent reproduction and document limitations.

**Exit condition:** a reproducible vulnerability with a clearly described impact.

## Phase 4 — Investigate an exploit chain

- Determine what capability the validated issue provides.
- Identify what additional stages would be required to reach native unsigned code execution.
- Evaluate whether separate, independently supported weaknesses can be connected.
- Test each stage separately and record where the chain stops.

**Exit condition:** a technically supported route from the initial entry point toward native code execution.

## Phase 5 — Demonstrate homebrew execution

- Validate the complete route on the precisely identified Mariko target.
- Demonstrate a minimal, harmless unsigned native program.
- Repeat the procedure from a documented starting state.
- Record exact firmware compatibility, prerequisites, reliability, and limitations.

**Exit condition:** an independently reproducible software-only homebrew launch on Mariko.

## Current position

The project is still in the discovery and validation stages. The Web Auth Applet and USB/MTP investigations have produced observations but no demonstrated entry point. The libnx callback investigation closed a host-side hypothesis and does not provide a stock-console route. No complete Mariko / HOS 23.0.1 software-only exploit chain has been demonstrated.

## Current research priorities

- Wait for an authorized, integrity-verifiable openWeb executable, matching NPDM, and BrowserDll/SystemData/OSS set. Phase 26 found third-party parsed metadata for 23.0.0.1200: openWeb `0100000000001043` is reported as 64-bit `openweb.nss` (FS SDK 23.2.2, 279 symbols, PAC/CFI noted); its NPDM parse output lists services/SVCs; BrowserDll `0100000000000803` metadata lists NetFront/WebKit-related LZ4 NRO paths and buildinfo. The 23.0.1 title delta does not list either ID, supporting carry-forward of the 23.0.0.1200 files. These are third-party text outputs, not binary hashes or a Nintendo-signed installed-content manifest; no actual binaries/user backups were found (`reports/PHASE26_ARTIFACT_ACQUISITION.md`).
- Use the Phase 23 parser for read-only metadata triage when a legitimate input arrives; preserve its explicit no-decompression/no-signature-verification limits. No real HOS input is currently available (`reports/PHASE23_DIFFERENTIAL_ANALYSIS.md`).
- Invite independent review of evidence labels, privacy scrubbing, and historical conclusions.
- Clarify exact hardware identity and distinguish owner-reported model/firmware from direct silicon evidence.
- Reproduce safe host-side tests from a clean checkout.
- Improve citations and attach source/version/hash information to each technical claim.

## Next, if new evidence supports it

- Review new public security advisories, conference material, and research repositories for exact Switch 1 hardware/firmware scope.
- If a legally obtained, unencrypted candidate set is provided, hash and identify openWeb `0100000000001043` plus its paired `main.npdm` and BrowserDll `0100000000000803` SystemData. Compare title/build metadata with the Phase 26 reports, then run NSTool and the project parser read-only. Do not source firmware or keys through this project.
- Design safe experiments around publicly documented stock interfaces, with explicit stop criteria and no malformed console traffic.

## Closed or deprioritized leads

- **Phase 7 libnx callback hypothesis:** closed against the documented callback capacity; not a stock-system entry point.
- **Phase 12 Web Auth Applet probe:** ordinary web APIs were observed; no vulnerability was demonstrated.
- **Phases 13–14 MTP observations:** no reproducible security-relevant primitive was established. Revisit only if new evidence changes the technical question.
- **SDK or Homebrew library issues:** not first-entry candidates when they require unsigned code to be running already.

## Completed research phases

- **Phase 26:** obtained no binary, but found third-party parsed update metadata for openWeb and BrowserDll at component revision `23.0.0.1200`, including openWeb build/NPDM fields and BrowserDll `buildinfo` and NetFront NRO paths. The 23.0.1 title delta omits both target IDs, supporting carry-forward; no HOS bytes were hashed or disassembled (`reports/PHASE26_ARTIFACT_ACQUISITION.md`).
- **Phase 25:** corrected the stock WifiWebAuth target mapping: applet ID `0x19` maps to openWeb `0100000000001043` on 22.0.0+; BrowserDll and openWeb are listed as 23.0.0.1200. The relevant files and a user backup were not present, so no target binary analysis occurred (`reports/PHASE25_BROWSERDLL_TARGET_RESEARCH.md`).
- **Phase 24:** reviewed public title/version metadata and firmware artifact availability; no authorized, integrity-verifiable target binary set was acquired (`reports/PHASE24_HOS_ARTIFACT_ACQUISITION.md`).
- **Phase 23:** added bounded NSO/NRO/KIP/NPDM metadata decoders and differential regression coverage. NSTool agreed on tested synthetic access-control/capability structures and the local homebrew NRO. No HOS executable or exploit evidence was obtained (`reports/PHASE23_DIFFERENTIAL_ANALYSIS.md`).
- **Phase 22:** built and compared MIT-licensed NSTool v1.9.2 against the local homebrew NRO and synthetic format fixtures. It exposed version-support gaps but acquired no HOS artifact (`reports/PHASE22_ARTIFACT_ACQUISITION.md`).
- **Phase 21:** public-source architecture review confirmed the WebApplet main NSO/NPDM alone would not capture the shared BrowserDll/SystemData engine; no target 23.0.1 binary set was found or acquired (`reports/PHASE21_WEBAPPLET_ANALYSIS.md`).
- **Phase 20:** confirmed the local Phase 18/19 commit was present and complete; the historical local GitHub synchronization attempt failed due DNS and invalid configured credentials. No authentication workaround was attempted (`reports/PHASE20_GITHUB_AND_RESEARCH_AUDIT.md`).
- **Phase 19:** added bounded subset validation and synthetic tests for NSO/NRO/KIP1/NPDM; ELF metadata and Phase 18 AArch64 analysis were wired into one JSON CLI. No HOS 23.0.1 executable was available; compressed Switch sections and full loader/signature semantics remain unsupported (`reports/PHASE19_HOS_ARTIFACT_READINESS.md`).
- **Phase 18:** ARM64 disassembler repair was validated on the local homebrew ELF only; no HOS compatibility claim (`reports/PHASE18_DISASSEMBLER_VALIDATION.md`).

## How priorities are chosen

Prefer work that can move the project closer to a stock-to-homebrew path. A useful lead must have a plausible route to the target, a testable technical claim, and a way to tell success from failure. Do not keep a direction alive merely because it produces more reports.
