# Phase 4 — compatibility with Mariko / HOS 23.0.1

## Decision matrix

| Request | Public Proof Status | Rating for Switch V2 / Mariko 23.0.1 |
|---|---|---|
| Original Switch Support | Gezina's announcement mentions "switch 1/2". No public PoC or reproducible record available on Switch 1. | **Claimed, unconfirmed.** |
| Mariko / T210B01 / Tegra214 | The exact chip or model HAC-001(-01), Switch Lite or OLED is not listed in the reviewed sources. | **Unconfirmed.** |
| HOS 23.0.1 on original Switch | "All firmware" is a general claim by the author without a version matrix or test record. | **Unconfirmed; cannot assign exploitability.** |
| Offline / no WebKit / no save transfer | This is the author's declared different solution. The input application/game and required locale are not publicly documented. | **Hardened, not usable for reproduction.** |
| Switch 2 20.0.0+ | The secondary mirror credits the author with explaining that 20.0.0+ is required for Switch 1 compatibility on Switch 2. | **Switch 2 platform assumption; not boundary proof on Switch 1.** |
| Kernel or system permissions | Not reported or proven. | **No evidence.** |
| Public source/PoC | No exploit code or technical write-up was found in the searched author's public channels, GitHub/GitLab and articles. | **Unreleased/not available as a reproducible instrument.** |

## Conclusion for a specific goal

For Nintendo Switch V2 Mariko, T210B01/Tegra214, HOS 23.0.1 **there is no publicly verified Gezine exploit compatibility in this collection**. The notification is a relevant new signal about a possible path in the userland, but does not allow a responsible claim that the target device is vulnerable or that an exploit is working on it.

That is not to say that Mariko is certainly not vulnerable. Evidence to decide this question is missing: a test with a specific Mariko SKU/SoC and HOS 23.0.1, a public implementation or technical explanation, a record of success and independent reproduction. Without them, it is not possible to infer Mariko support from the "Switch 1/2" claim or from "all firmware".

## Safe technical verification without console dump

Without own legally acquired system artifacts, only the publication trail can be verified: dates/statuses, repositories, article content, and whether the code is released. These materials cannot be used to reconstruct a bug, run Ghidra analysis of a target binary, or confirm hardware compatibility. No payload or proprietary image was downloaded or run during this phase.

## Sources and degree of credibility

- [Gezine — notice dated 07/08/2026](https://x.com/gezine_dev/status/2074894225460822503) — primary author status, 403 on load; **medium** certainty for the content of the public claim due to contemporary citations, **low** for technical veracity.
- [Gezine — patch from 07/10/2026](https://x.com/gezine_dev/status/2075682718155956275) — primary author status, 403 on load; mirror [TwStalker](https://w.twstalker.com/gezine_dev) cites needing HOS 20.0.0+ on Switch 2 for Switch 1 game compatibility; **low to medium**.
- [Hackintendo, 2026-07-08](https://hackintendo.com/une-faille-userland-switch1-2/) — period secondary article and status citation; **medium** for notification context, **low** for technical mechanisms.
- [Nintendo Security Advisories](https://www.nintendo.com/security-advisories/en/index.html) — official registry checked 10/30/2026; **high** for published advisories; does not contain Gezine research identification.
