# PROJECT ZERO Phase 20 — GitHub Recovery and Research Audit

Date: 2026-10-31

## Git and publication state

- Repository: `main`, remote `origin` = `https://github.com/KriskoAdam/project-zero-switch-mariko.git`.
- Verified local HEAD: `638cb473a2e3412eb3fc32cdfe11fa16383734cc` (`Add bounded Switch artifact inspection pipeline`).
- Parent/remote-tracking commit before this phase: `6abc5e7` (`Publish English-language PROJECT ZERO research`). Local branch was one commit ahead. The specified Phase 18/19 commit contains the ARM64 repair and tests, artifact inspector and tests, both phase reports, evidence register, roadmap and script documentation.
- `git ls-remote origin HEAD` failed: `Could not resolve host: github.com`. `dscacheutil -q host -a name github.com` returned no address. `dig` could not bind its socket (`Operation not permitted`) in the managed execution environment; `networksetup` could not read the network service configuration (`AuthorizationCreate() failed: -60008`). Therefore the observed failure is name resolution from Git, while the active resolver configuration could not be independently inspected here.
- `gh auth status` reports that the configured account token is invalid. No token value was requested, displayed, or written. Neither an authentication workaround nor a push was attempted. Even if DNS recovers, the credential must be renewed through the normal GitHub sign-in flow before push can work.
- No GitHub synchronization occurred. Phase 20 changes are committed locally; Phase 17 report files already present as untracked files were preserved and excluded from this commit.

## Research state checked

Read `README.md`, `ROADMAP.md`, `AI_AGENTS.md`, `reports/EVIDENCE_REGISTER.md`, `reports/PHASE17_ARTIFACT_AUDIT.md`, `reports/PHASE17_TOOL_VALIDATION.md`, `reports/PHASE17_NEXT_EXPERIMENT.md`, and `reports/PHASE18_DISASSEMBLER_VALIDATION.md` / `reports/PHASE19_HOS_ARTIFACT_READINESS.md`.

### Actually tested

- Physical-console observations recorded previously: benign local WifiWebAuthApplet page checks and standard USB/MTP observation. They establish only those observed session behaviors, not code execution, vulnerability, or independently verified Mariko silicon.
- Phase 18: symbol-aware/CFG-bounded AArch64 analysis on a local PROJECT ZERO homebrew ELF, compared with Apple `objdump` and Ghidra direct disassembly. Full Ghidra DWARF analysis timed out; it was not counted as complete.
- Phase 19: JSON and SHA-256 inspection of a locally built NRO and ELF, plus self-authored synthetic NSO/NRO/KIP1/NPDM parser tests. Latest run: 25 workspace tests, 11 lab tests, 6 Phase 14 validator tests all pass. None consumed HOS code.
- Phase 17: Ghidra can import a host AArch64 ELF; Capstone, LIEF, pyelftools, Construct were exercised against host-built material. SwitchBlade was reviewed as public source but not checked out or independently run. Unicorn was absent. REA was not demonstrated on an HOS artifact or a Switch format in this evidence set.

### What is ready, and what is not

- Ready for a permitted input: SHA-256 and bounded metadata checks for NSO0/NRO0/KIP1/NPDM and ELF; pyelftools ELF segment metadata; Phase 18 ELF/AArch64 symbol-range/entrypoint-CFG analysis; Ghidra import/disassembly workflow for ELF.
- Not ready for full HOS module reverse engineering: NSO LZ4/Zbic and KIP BLZ decompression; compressed NRO support; NPDM signature validation and full FAC/SAC/KC/capability semantics; NSO/KIP-to-Ghidra loading and relocation semantics; independent Switch-format parser comparison. The current “valid-subset” label is not proof that Horizon's loader accepts an artifact.
- The repository inventory has no target-identified HOS 23.0.1 NSO/KIP/ELF, matching NPDM, build manifest, or verifiable component hash. Available ELF/NRO are project homebrew outputs. No stock-system vulnerability, reachable bug, or software-only entry point has been demonstrated.

### Open research questions

1. Does any stock-reachable HOS 23.0.1 component contain a vulnerability reachable from an ordinary user-facing parser or service?
2. What exact process/service capability and applet configuration applies to the measured WifiWebAuthApplet runtime on this target build?
3. Are any public Switch 1 findings reproducible on Mariko/T210B01 and exactly HOS 23.0.1?
4. Can an authorized target-identifiable executable and its matching NPDM/build identity be obtained without extracting or decrypting proprietary firmware?

## Highest-value next experiment — blocked on a real input

**Hypothesis:** the compiled `webapplet` metadata and executable for HOS 23.0.1 either corroborate the public API/configuration explanation for the already observed WifiWebAuthApplet behavior, or expose a concrete difference that merits focused review. This would add binary evidence to the existing runtime observation without treating API availability as a vulnerability.

**Required input gate:** a legitimately published or otherwise authorized, integrity-verifiable HOS 23.0.1 `webapplet` executable in a form this toolchain can actually inspect (ELF, or uncompressed NSO) **and its matching NPDM plus component/build identity**. A compressed/encrypted NSO/container alone is not a usable input for the current Phase 19 pipeline. Do not extract/decrypt firmware, access keys, or modify the console to obtain it.

**Measurement if the gate is met:** record provenance and SHA-256; parse executable mapping and NPDM flags/capability sections; import the actual executable into Ghidra; identify only call sites and configuration relevant to the observed web APIs; compare with public documentation and the prior page results. Stop if provenance/build matching is uncertain, if only a compressed/encrypted container is supplied, or if no new mismatch/call-path evidence appears. Any API/configuration mismatch would be a lead, not an exploit finding.

**Current result:** blocked; the required target artifact and matching metadata are absent. No synthetic stand-in or substitute experiment was created. The next project action is to wait for a legitimate, target-identified artifact or a reproducible public research result.

## Verification commands and results

From repository root:

```sh
git status --short --branch
git show --stat 638cb473a2e3412eb3fc32cdfe11fa16383734cc
git remote -v
git log -5 --oneline --decorate
gh auth status
git ls-remote origin HEAD
../.venv/bin/python -m unittest discover -s tests/workspace-tests -v
../.venv/bin/python -m unittest discover -s lab/tests -v
../.venv/bin/python tools/phase14-mtp/test_validate_phase14.py
git diff --check
```

Results: specified commit and included Phase 18/19 files verified; Git remote lookup failed on hostname resolution; GitHub credential invalid; tests passed 25 + 11 + 6 = 42; `git diff --check` passed. The commit/push state and resolver diagnostic limits above are recorded without secret material.
