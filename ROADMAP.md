# Roadmap

This roadmap is about improving evidence quality and shared research. It does not promise an exploit or a release date.

## Now

- Wait for an authorized, integrity-verifiable HOS 23.0.1 WebApplet artifact set: inspectable main executable + matching NPDM/build identity + same-build BrowserDll/SystemData (shared NetFront/OSS modules and relevant browser data). Phase 22 found no licensed public binary set; NSTool v1.9.2 parses a bounded subset but does not cover NSO ZBIC, KIP decompression, NRO 23+ compression, or newer NPDM fields (`reports/PHASE22_ARTIFACT_ACQUISITION.md`).
- Use the Phase 23 parser for read-only metadata triage when a legitimate input arrives; preserve its explicit no-decompression/no-signature-verification limits. No real HOS input is currently available (`reports/PHASE23_DIFFERENTIAL_ANALYSIS.md`).
- Invite independent review of evidence labels, privacy scrubbing, and historical conclusions.
- Clarify exact hardware identity and distinguish owner-reported model/firmware from direct silicon evidence.
- Reproduce safe host-side tests from a clean checkout.
- Improve citations and attach source/version/hash information to each technical claim.

## Next, if new evidence supports it

- Review new public security advisories, conference material, and research repositories for exact Switch 1 hardware/firmware scope.
- Analyze only legally obtained, integrity-verifiable artifacts; do not source firmware or keys through this project.
- Design safe experiments around publicly documented stock interfaces, with explicit stop criteria and no malformed console traffic.

## Later

- Maintain a versioned compatibility matrix for Erista, Mariko, and Switch 2.
- Add an evidence-backed corpus of public claims and independent reproductions.
- Decide whether a specific technical lead merits deeper work based on pre-homebrew reachability.

## Done / closed branches

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
