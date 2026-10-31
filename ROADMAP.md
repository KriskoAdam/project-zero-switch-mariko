# Roadmap

This roadmap is about improving evidence quality and shared research. It does not promise an exploit or a release date.

## Now

- Reproduce the Phase 19 read-only Switch-format parser tests; use only legally sourced, integrity-verifiable target artifacts if any become available.
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

- Phase 19 parser pipeline: bounded subset validation and synthetic tests exist for NSO/NRO/KIP1/NPDM; ELF metadata and Phase 18 AArch64 analysis are wired into one JSON CLI. No HOS 23.0.1 executable was available, compressed Switch sections and full loader/signature semantics remain unsupported, and this is not a firmware analysis result (`reports/PHASE19_HOS_ARTIFACT_READINESS.md`).
- Phase 18 ARM64 disassembler repair validated on the local homebrew ELF only; no HOS compatibility claim (`reports/PHASE18_DISASSEMBLER_VALIDATION.md`).
- Phase 7 libnx filename-buffer ABI hypothesis: closed as safe under the documented callback capacity.
- Phase 12 benign web-applet capability probe: no vulnerability demonstrated.
- Phase 13–14 standard read-only MTP observations: no reproducible security anomaly demonstrated; branch closed absent new evidence.
- SDK/Homebrew library findings requiring already-running unsigned code are not first-entry-point candidates.
