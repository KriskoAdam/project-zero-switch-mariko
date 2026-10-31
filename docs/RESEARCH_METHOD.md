# Research Method — From Stock Mariko to Homebrew

PROJECT ZERO's goal is a reproducible software-only jailbreak for Nintendo Switch V2 / Mariko. This method is designed to help distinguish a promising entry point from ordinary system behavior and to show exactly how far a result moves toward unsigned native code execution.

## Research stages

For each candidate lead, identify its place in the possible path:

1. **Reachability:** can the component or input be reached from ordinary stock-console use?
2. **Vulnerability:** is there a reproducible flaw, rather than an expected response or harmless crash?
3. **Capability:** what does the flaw actually provide?
4. **Privilege transition:** does the result cross a relevant process or privilege boundary?
5. **Chain relevance:** could it contribute to a route to native unsigned code execution?
6. **Homebrew demonstration:** has the complete route been reproduced on the target Mariko hardware and firmware?

Do not skip stages when describing a result. A finding at one stage does not establish the next.

## Evidence labels

- **Physical:** directly observed on the owner-operated console; state exactly what was observed and any user-reported context.
- **Public source:** source code, official advisory, technical paper, or public documentation; state revision/date and whether primary.
- **Host test:** experiment on the Mac or another host; no target-system implication unless the same behavior is established.
- **Model/synthetic:** output of a model or synthetic input; supports only the model/tested parser.
- **Inference:** reasoned interpretation with premises and alternatives stated.
- **Unknown:** evidence is absent or insufficient.

## Minimum experiment record

Every experiment should state its jailbreak-stage question, hypothesis, stop condition, target/environment version, tools and versions, exact steps, sanitized inputs/outputs, hashes where useful, interpretation, limitations, and independent review.

## Compatibility

Always distinguish Erista V1, Mariko V2, and Switch 2. Record exact firmware and hardware evidence. A known exploit on another revision is a research lead, not proof of Mariko compatibility.

## When to close a lead

Close or deprioritize a branch when repeated tests produce no new evidence relevant to a stock-to-homebrew path, when the required starting conditions are unavailable, or when the result only applies after unsigned homebrew is already running. Record why it was closed so future work can focus on better candidates.

## Experiment boundaries

Use lawful, non-destructive research methods. Do not modify the physical console, access secrets, acquire proprietary firmware through circumvention, or send malformed/destructive traffic. These boundaries preserve the test device and the reliability of the research; they do not change the project's jailbreak objective.
