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

## Closed or deprioritized leads

- **Phase 7 libnx callback hypothesis:** closed against the documented callback capacity; not a stock-system entry point.
- **Phase 12 Web Auth Applet probe:** ordinary web APIs were observed; no vulnerability was demonstrated.
- **Phases 13–14 MTP observations:** no reproducible security-relevant primitive was established. Revisit only if new evidence changes the technical question.
- **SDK or Homebrew library issues:** not first-entry candidates when they require unsigned code to be running already.

## How priorities are chosen

Prefer work that can move the project closer to a stock-to-homebrew path. A useful lead must have a plausible route to the target, a testable technical claim, and a way to tell success from failure. Do not keep a direction alive merely because it produces more reports.
