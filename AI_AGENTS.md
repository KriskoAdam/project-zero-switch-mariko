# AI agent participation guide

AI-assisted research is welcome. Every contribution must be reviewable by a human and reproducible without trusting a model's summary.

## Required contribution record

For each claim or experiment, provide:

1. **Question and stop condition.** State the narrow question and what result ends the experiment.
2. **Target scope.** Exact console revision, SoC evidence, OS version, applet/service context, and prerequisites. Use “unknown” when unknown.
3. **Sources.** Direct URLs, publication dates, source revision/hash, and whether each source is primary, secondary, or an inference.
4. **Method.** Exact commands or UI steps, tools and versions, inputs, and environment. Remove personal paths, serial numbers, network identifiers, and secrets.
5. **Result.** Raw sanitized output plus interpretation. Label physical-device, public-source, host-only, synthetic, and inferred results separately.
6. **Independent check.** A second reviewer or a separate reproduction. Explain differences and unresolved questions.
7. **Safety.** Confirm the work did not modify the console, run unknown payloads, access secrets, or send malformed/destructive traffic.

## Agent boundaries

- Do not infer a vulnerability from an API existing, an operation being declared, or a model finding.
- Do not make changes to a physical console. Experiments that require user interaction must give one clear, reversible step and wait for the result.
- Do not fetch proprietary firmware, keys, dumps, or private artifacts.
- Do not submit generated exploit payloads, bypass instructions, or code that targets the console with malformed input.
- Do not claim AI independently verified a fact unless the evidence and method are included.

## Suggested agent roles

A researcher may independently review boot-chain literature, stock applet/service reachability, public vulnerability scope, tool/artifact legality, or the skeptical interpretation of another result. Avoid duplicating a broad survey. Check `docs/OPEN_QUESTIONS.md` first and claim a narrowly scoped issue before doing parallel work.

## Review standard

The skeptical reviewer should try to falsify the claim, audit assumptions and identify the strongest alternative explanation. A disagreement is recorded, not averaged away. An AI-generated result without source evidence is a lead, not a finding.
