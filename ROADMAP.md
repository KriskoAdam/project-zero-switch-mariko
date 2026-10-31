# PROJECT ZERO — Research Roadmap

The goal is a reproducible software-only path from a stock Nintendo Switch V2 / Mariko to unsigned native code/homebrew, without a modchip.

## Current position

The project has not demonstrated a software-only jailbreak, a stock entry point, or a vulnerability on Mariko / HOS 23.0.1. The exact silicon identity of the test console remains unverified. The highest-priority lead is static/runtime research around openWeb and shared BrowserDll, but actual executable analysis is blocked by encrypted candidate NCA containers and the absence of parsed executable contents.

See **[RESEARCH_SUMMARY.md](RESEARCH_SUMMARY.md)** for the single consolidated record of all findings, evidence, limitations, closed leads, and priorities.

## Milestones

1. **Verify target:** establish exact hardware revision/SoC and firmware using reliable non-invasive evidence.
2. **Acquire analyzable evidence:** obtain authorized, integrity-verifiable, inspectable openWeb executable + matching NPDM + same-build BrowserDll/SystemData.
3. **Map reachable surfaces:** identify real entry points, parser paths, IPC, services, and security boundaries from actual target code/configuration.
4. **Validate a vulnerability:** demonstrate a reproducible defect on a relevant component and establish exact hardware/firmware scope.
5. **Establish exploit impact:** determine the primitive and any required sandbox/privilege transitions; test stages separately.
6. **Demonstrate homebrew:** reproduce a harmless unsigned native program from a stock starting state on the verified target.

Milestones are goals, not claims that any exploit stage exists.

## Research discipline

- Maintain one narrative report: RESEARCH_SUMMARY.md. Update it in place; do not create a new phase report for every experiment.
- Preserve raw captures, source code, test fixtures, manifests, and machine-readable data when they are useful for reproduction.
- Do not commit console secrets, private identifiers, proprietary firmware binaries, or unredacted personal data.
- Separate physical observations, public-source facts, host-only tests, synthetic models, inferences, and hypotheses.
- Do not treat Erista, Mariko, and Switch 2 results as interchangeable.
- Close or deprioritize leads that do not provide a plausible route from stock state to native code execution.
