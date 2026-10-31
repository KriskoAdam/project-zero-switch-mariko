# Phase 3 — executive summary

**Target:** Nintendo Switch V2 Mariko T210B01, HOS 23.0.1. Status: 30 October 2026.

## Result

Public sources have not shown reproducible software input for the exact Switch V2/Mariko + HOS 23.0.1 target without the modchip. This is not proof that a non-public or undiscovered error does not exist.

## Measurable outputs

- 12 items in the database including historical boot, kernel, WebKit, service, NVIDIA and Wi-Fi records.
- Markdown and machine-readable JSON database.
- 4 research utilities and 6 unit tests.
- All utilities run on synthetic Mach-O ARM64 fixture or project manifests; the tests passed.
- Ghidra 12.1.4, JDK 25 and macOS ARM64 native components verified. REA 6.8.0 Codex registration aligned; the live provider requires Codex to be restarted after changing the configuration.
- No firmware, key or dump was obtained or analyzed.

## Critical resolution

CVE-2026-82079 is described in the official advisory as a possible information leak during a proximity attack; Switchbrew attributes the ldn fix to a change in version 23.0.0. Nintendo describes 23.0.1 as a fix for a functional issue, and Switchbrew leaves the security field of this version blank. Therefore, we do not attribute a new security patch to 23.0.1 without proof. [Nintendo advisory](https://www.nintendo.com/security-advisories/assets/pdf/20260910e.pdf), [23.0.0](https://switchbrew.org/wiki/23.0.0), [23.0.1](https://switchbrew.org/wiki/23.0.1), [Nintendo 23.0.1](https://www.nintendo.com/en-gb/Support/Troubleshooting/Nintendo-Switch-System-Update-Information-1445507.html)

See [final report](PHASE3_FINAL_REPORT.md), [database](VULNERABILITY_DATABASE.md), [open questions](UNRESOLVED_QUESTIONS.md) and [readiness of analysis](BINARY_ANALYSIS_READINESS.md).

