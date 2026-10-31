# Contributing to PROJECT ZERO

PROJECT ZERO is working toward a software-only jailbreak for Nintendo Switch V2 / Mariko. The goal is to find a reproducible route from a stock console to unsigned native code execution and homebrew, without a modchip or hardware modification.

Contributions should help answer one practical question: **does this work move us closer to a real Mariko software-only entry point or validate an important stage of a possible jailbreak chain?**

## Contributions we are looking for

- New software-only entry-point ideas that are relevant to Mariko.
- Reverse engineering of publicly documented Switch components and interfaces.
- Reproduction or careful evaluation of known Switch vulnerabilities against the exact target.
- Experiments that establish whether a candidate behavior is exploitable or ordinary system behavior.
- Analysis of applets, Horizon services, IPC, WebKit, USB, and other plausible starting surfaces.
- Evidence-backed exploit-chain diagrams and compatibility research.
- AI-assisted analysis, automation, test harnesses, and independent technical reviews.
- Clear reports of failed approaches that prevent duplicated work.

## What to include

For each proposed finding or experiment, include:

1. **Goal:** what part of the software-only jailbreak path are you investigating?
2. **Target:** exact console revision, SoC evidence, Horizon OS version, and prerequisites. Mark unknown details as unknown.
3. **Hypothesis:** the specific behavior or vulnerability you expect to test.
4. **Method:** sources, tools and versions, commands or steps, and test environment.
5. **Result:** observed output and what it does—and does not—prove.
6. **Reproduction:** enough detail for another researcher to independently check the result.
7. **Impact:** whether it provides an entry point, code execution, privilege transition, or only a limited observation.

## Before opening a pull request

- Check the roadmap and open questions to avoid repeating closed work.
- Link sources and identify their dates, versions, and hardware scope.
- Distinguish physical-device results, public-source analysis, host tests, simulations, and inference.
- Keep generated files small and sanitized.
- Do not include console secrets, personal identifiers, proprietary firmware dumps, keys, or private raw captures.
- Do not claim a jailbreak or exploit works unless the complete relevant behavior is reproducible.

## Pull request checklist

- [ ] The contribution relates to the Mariko software-only jailbreak goal.
- [ ] Hardware and firmware scope are explicit.
- [ ] The hypothesis and expected outcome are clear.
- [ ] Sources, tools, versions, and reproduction steps are included.
- [ ] Results are separated from assumptions and simulations.
- [ ] The technical impact on a possible jailbreak path is explained.
- [ ] Privacy and redistribution rights were checked.
