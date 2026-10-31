# Roadmap

This roadmap is about improving evidence quality and shared research. It does not promise an exploit or a release date.

## Now

- Wait for an authorized, integrity-verifiable openWeb executable + matching NPDM + BrowserDll/SystemData/OSS set. Phase 26 found NinUpdates generated reports for 23.0.0.1200: openWeb `0100000000001043` is 64-bit `openweb.nss` (FS SDK 23.2.2, 279 symbols, PAC/CFI noted); its NPDM parse output lists services/SVCs; BrowserDll `0100000000000803` metadata lists NetFront/WebKit-related LZ4 NRO paths and buildinfo. The 23.0.1 title delta does not list either ID, supporting carry-forward of the 23.0.0.1200 files. These are third-party text outputs, not binary hashes or a Nintendo-signed installed-content manifest; no actual binaries/user backups were found (`reports/PHASE26_ARTIFACT_ACQUISITION.md`).
- Use the Phase 23 parser for read-only metadata triage when a legitimate input arrives; preserve its explicit no-decompression/no-signature-verification limits. No real HOS input is currently available (`reports/PHASE23_DIFFERENTIAL_ANALYSIS.md`).
- Invite independent review of evidence labels, privacy scrubbing, and historical conclusions.
- Clarify exact hardware identity and distinguish owner-reported model/firmware from direct silicon evidence.
- Reproduce safe host-side tests from a clean checkout.
- Improve citations and attach source/version/hash information to each technical claim.

## Next, if new evidence supports it

- Review new public security advisories, conference material, and research repositories for exact Switch 1 hardware/firmware scope.
- If a legally obtained, unencrypted candidate set is provided, hash and identify openWeb `0100000000001043` + its paired `main.npdm` and BrowserDll `0100000000000803` SystemData. Compare title/build metadata with the Phase 26 reports, then run NSTool and the project parser read-only. Do not source firmware or keys through this project.
- Design safe experiments around publicly documented stock interfaces, with explicit stop criteria and no malformed console traffic.

## Later

- Maintain a versioned compatibility matrix for Erista, Mariko, and Switch 2.
- Add an evidence-backed corpus of public claims and independent reproductions.
- Decide whether a specific technical lead merits deeper work based on pre-homebrew reachability.

## Done / closed branches

- Phase 26 obtained no binary, but found third-party parsed update metadata for openWeb and BrowserDll at component revision `23.0.0.1200`, including openWeb build/NPDM fields and BrowserDll `buildinfo` and NetFront NRO paths. The 23.0.1 title delta omits both target IDs, supporting carry-forward; no HOS bytes were hashed or disassembled (`reports/PHASE26_ARTIFACT_ACQUISITION.md`).

- Phase 25 corrected the stock WifiWebAuth target mapping: applet ID `0x19` maps to openWeb `0100000000001043` on 22.0.0+; BrowserDll and openWeb are listed as 23.0.0.1200, with BrowserDll NetFront/buildinfo content changed in 23.0.0. The relevant files and a user backup were not present, so no target binary analysis occurred (`reports/PHASE25_BROWSERDLL_TARGET_RESEARCH.md`).

- Phase 23 added bounded NSO/NRO/KIP/NPDM metadata decoders and differential regression coverage. NSTool agreed on tested synthetic access-control/capability structures and the local homebrew NRO. A source-level ACID `+0x200` correction and ThreadInfo documentation discrepancy are recorded; no HOS executable or exploit evidence was obtained (`reports/PHASE23_DIFFERENTIAL_ANALYSIS.md`).
- Phase 22 built and compared MIT-licensed NSTool v1.9.2 against the local homebrew NRO and synthetic format fixtures. It exposed version-support gaps but acquired no HOS artifact; WebApplet reverse engineering remains gated on an authorized target set (`reports/PHASE22_ARTIFACT_ACQUISITION.md`).
- Phase 21 public-source architecture review confirms the WebApplet main NSO/NPDM alone would not capture the shared BrowserDll/SystemData engine; no target 23.0.1 binary set was found or acquired, so code/permission analysis remains blocked (`reports/PHASE21_WEBAPPLET_ANALYSIS.md`).
- Phase 20 confirmed the local Phase 18/19 commit is present and complete; GitHub remains unsynchronized because local hostname resolution failed and the configured `gh` credential is invalid. No authentication workaround was attempted (`reports/PHASE20_GITHUB_AND_RESEARCH_AUDIT.md`).
- Phase 19 parser pipeline: bounded subset validation and synthetic tests exist for NSO/NRO/KIP1/NPDM; ELF metadata and Phase 18 AArch64 analysis are wired into one JSON CLI. No HOS 23.0.1 executable was available, compressed Switch sections and full loader/signature semantics remain unsupported, and this is not a firmware analysis result (`reports/PHASE19_HOS_ARTIFACT_READINESS.md`).
- Phase 18 ARM64 disassembler repair validated on the local homebrew ELF only; no HOS compatibility claim (`reports/PHASE18_DISASSEMBLER_VALIDATION.md`).
- Phase 7 libnx filename-buffer ABI hypothesis: closed as safe under the documented callback capacity.
- Phase 12 benign web-applet capability probe: no vulnerability demonstrated.
- Phase 13–14 standard read-only MTP observations: no reproducible security anomaly demonstrated; branch closed absent new evidence.
- SDK/Homebrew library findings requiring already-running unsigned code are not first-entry-point candidates.
