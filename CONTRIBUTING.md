# Contributing

Thanks for helping make the findings more accurate. Start with `AI_AGENTS.md`, `SECURITY.md`, and `docs/RESEARCH_METHOD.md`.

## Good contributions

- Correct a source citation or compatibility statement with a verifiable reference.
- Reproduce a host-side test from a clean checkout and report exact versions/output.
- Add an independent skeptical review or document a competing interpretation.
- Propose a narrowly scoped, safe experiment that can be performed with existing lawful inputs.
- Improve privacy scrubbing, test instructions, and evidence labels.

## Before opening a pull request

- Search the existing reports and issues to avoid repeating a closed branch.
- Never include console secrets, firmware images, personal identifiers, or the excluded Phase 15/16 application.
- Keep generated results small and sanitized. Do not commit caches, virtual environments, tool distributions, binaries, or private raw captures.
- Distinguish what is documented, observed, inferred, simulated, and unverified.
- Include exact reproduction steps and a stop condition.

## Pull request checklist

- [ ] Scope and target are explicit.
- [ ] Sources are linked and dated.
- [ ] Commands, versions, and hashes are included where relevant.
- [ ] Tests are host-only unless physical-console observation is clearly stated.
- [ ] Privacy and redistribution rights were checked.
- [ ] No exploit payload, secrets, or console modifications are included.
