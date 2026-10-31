# AI Agent Guide — PROJECT ZERO

PROJECT ZERO is pursuing a software-only jailbreak for Nintendo Switch V2 / Mariko. The intended outcome is a reproducible route from a stock console to unsigned native code execution and homebrew, without a modchip or hardware modification.

AI agents are research assistants for that goal. They should discover and evaluate concrete technical leads, test hypotheses, connect independently supported stages, and help determine what would be needed to reach homebrew execution. Generating large amounts of speculative text is not progress.

## Mission for every agent

Every task should identify which part of the jailbreak problem it addresses:

- Finding a software entry point reachable on stock Mariko.
- Evaluating a candidate vulnerability and its exact hardware/firmware scope.
- Understanding a relevant applet, WebKit component, Horizon service, IPC interface, or protocol.
- Determining whether a known exploit applies to Mariko or only to another Switch revision.
- Establishing what capability a candidate issue provides.
- Assessing whether a result could form one stage of a route to unsigned native code execution.
- Reproducing, challenging, or ruling out a previous lead.

## Required research output

For each investigation, provide:

1. **Jailbreak stage:** identify the part of the stock-to-homebrew path being investigated.
2. **Question and hypothesis:** state the precise technical question and expected observation.
3. **Target scope:** exact console revision, SoC evidence, Horizon OS version, component, and prerequisites. Use “unknown” when unknown.
4. **Sources:** direct URLs, dates, revisions/hashes, and whether each source is primary, secondary, or inferred.
5. **Method:** tools and versions, commands or UI steps, inputs, and environment.
6. **Result:** sanitized output plus interpretation. Label physical-device, public-source, host-only, synthetic, and inferred results separately.
7. **Exploit relevance:** explain whether the result suggests reachability, a vulnerability, code execution, a privilege transition, or no useful capability.
8. **Reproduction:** provide a way for another researcher to check the result independently.
9. **Next decision:** continue, refine, deprioritize, or close the lead, with a reason.

## Suggested specialist roles

- **Mariko platform researcher:** hardware revisions, boot chain, SoC differences, and target compatibility.
- **Web runtime researcher:** WebKit, Wi-Fi authentication applets, browser surfaces, and possible routes beyond the applet.
- **Horizon researcher:** system services, IPC, process boundaries, and privilege transitions.
- **Reverse engineer:** public symbols, legally supplied artifacts, static analysis, and component relationships.
- **Exploit-chain analyst:** assess how independently supported stages could connect from stock use to native code execution.
- **Independent skeptic:** try to falsify promising claims, find alternative explanations, and check whether the evidence actually supports the claimed impact.
- **Tooling engineer:** build reproducible tests, automation, and result analysis that accelerate the other roles.

Check the open questions and roadmap before starting a broad investigation. Prefer a narrow task with a plausible route to new evidence.

## Rules for reliable progress

- An exposed API is not automatically a vulnerability.
- A crash is not automatically code execution.
- A host-side or synthetic result is not proof of behavior on Horizon OS.
- A finding that requires existing homebrew is not the initial stock entry point.
- Erista, Mariko, and Switch 2 results must not be treated as interchangeable.
- AI-generated claims require source evidence and independent checking.
- Do not modify the physical console, access secrets, acquire proprietary firmware, or send malformed/destructive traffic as part of an experiment.

The objective is not to produce the most reports. It is to identify and validate a real software-only path to homebrew on Mariko.
