# PROJECT ZERO — Software-Only Nintendo Switch Mariko Jailbreak Research

**Independent AI-assisted research project** investigating whether a stock Nintendo Switch V2 / Mariko can reach unsigned native code and homebrew without a modchip or hardware modification.

> **Status (2026-10-31): no software-only jailbreak has been demonstrated by this project.** The target console is owner-reported as HOS 23.0.1; its exact Mariko/T210B01 silicon identity has not been independently verified. No vulnerability or complete exploit chain has been confirmed.

## Research status

The project has investigated the Wi-Fi Web Auth applet, public browser/runtime metadata, USB/MTP behavior, public exploit claims, binary-inspection tooling, and synthetic differential models. The physical applet and MTP tests produced bounded observations, not an exploit. The parser and disassembler have been tested on synthetic fixtures and local homebrew—not Nintendo firmware.

The highest-priority current lead is the relationship between **openWeb** (0100000000001043) and shared **BrowserDll** SystemData (0100000000000803). Public third-party metadata identifies candidate component revisions and WebKit-related paths, but actual executable analysis remains blocked: candidate NCA containers are encrypted and no executable contents were parsed.

## One source of truth

All current findings, evidence boundaries, artifact status, closed leads, blockers, and next priorities are maintained in **[RESEARCH_SUMMARY.md](RESEARCH_SUMMARY.md)**. Keep this as the single narrative research report. Preserve source code, tests, raw sanitized captures, and machine-readable datasets as supporting material; do not create another phase report for every task.

## Contributing

Reverse engineers, Switch homebrew developers, embedded developers, security researchers, and AI-agent builders are welcome. Read [AI_AGENTS.md](AI_AGENTS.md), [CONTRIBUTING.md](CONTRIBUTING.md), and [SECURITY.md](SECURITY.md). Contributions should add reproducible evidence, not speculative report volume.

## Repository map

- RESEARCH_SUMMARY.md — sole consolidated narrative research report.
- lab/, scripts/, tools/, tests/ — code, experiments, parsers, diagnostics and tests.
- reports/raw/ and reports/project-zero-local/raw/ — sanitized raw evidence.
- reports/vulnerabilities.json — machine-readable vulnerability research dataset.
- research/agents/ — research task briefs and agent work products.
- references/ — third-party source excerpts and notices.

## Reproduce host-side checks

Create a virtual environment, install requirements.txt, then run:

```sh
python3 -m unittest discover -s lab/tests -v
python3 -m unittest discover -s tests/workspace-tests -v
(cd tools/phase14-mtp && python3 -m unittest -v test_validate_phase14.py)
```

These checks validate host-side tooling and models. They do not test or jailbreak a Nintendo Switch.

## License

Project-authored code and scripts are MIT licensed; project-authored documentation is CC BY 4.0. Third-party excerpts retain their own license and notices. See [LICENSE](LICENSE).
