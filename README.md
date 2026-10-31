# PROJECT ZERO — Software-Only Nintendo Switch Mariko Jailbreak Research

**An independent, AI-assisted project working toward a software-only jailbreak for Nintendo Switch V2 (Mariko), with the goal of running unsigned homebrew without a modchip or hardware modification.**

> **Current status:** A working software-only jailbreak for Mariko on Horizon OS 23.0.1 has not yet been demonstrated by this project. The exact SoC identity of the test console has not been independently verified. This is the challenge PROJECT ZERO is trying to solve—not a claim that the jailbreak already exists.

## The mission

PROJECT ZERO is pursuing one concrete outcome: find and validate a practical software-only entry point for Nintendo Switch V2 / Mariko that can lead to native unsigned code execution and homebrew.

The intended result is a route that does not require:
- Installing a modchip.
- Soldering or physically modifying the console.
- Replacing or modifying hardware.
- Relying on an exploit that only works on the older unpatched Erista V1 hardware.

The primary research target is Switch V2 / Mariko (commonly associated with T210B01 / Tegra214) running Horizon OS 23.0.1. The target console's exact silicon identity remains unverified in the current evidence.

## What we are trying to achieve

The long-term objective is a reproducible chain from an ordinary stock-console starting point to unsigned native code execution, followed by a practical homebrew launch path.

Research areas include:

- Finding a reachable software entry point on stock Mariko.
- Investigating WebKit and system applets as possible starting surfaces.
- Understanding Horizon OS services, IPC boundaries, and privilege transitions.
- Studying USB and MTP behavior for useful, reproducible leads.
- Comparing known Switch exploits against the exact Mariko hardware and firmware target.
- Evaluating whether separate weaknesses could form a viable exploit chain.
- Building repeatable tests and tooling that help distinguish real leads from dead ends.

These are research directions, not claims that any listed component is vulnerable.

## Why this project exists

Mariko consoles are widely considered difficult to jailbreak without a modchip. Older Switch exploits do not automatically work on Mariko, and a working homebrew environment is not the same thing as having a way to enter the system from stock firmware.

PROJECT ZERO focuses on that missing first step: a software-only route into unsigned code execution.

The project began with one researcher, a Switch V2, a MacBook, and AI coding and research tools. It combines public-source analysis, host-side experiments, observations from a stock console, and AI-assisted investigation. The goal is to turn promising ideas into testable results and, ultimately, a working jailbreak.

## Current progress

The work has explored several possible starting points:

- **Wi-Fi Web Auth Applet:** a benign local test page loaded and ordinary browser APIs were exercised. No exploit or native execution was demonstrated.
- **USB / MTP:** the stock console exposed an MTP interface in its normal copy-to-computer mode. Read-only behavior was measured across multiple sessions; no useful exploit primitive has been established.
- **libnx:** a host-side investigation closed an off-by-one hypothesis in a public callback contract. This is not a stock-console entry point.
- **Public exploit research:** known projects and claims, including ns2jb, have been checked against the exact hardware and firmware target. No reproducible Mariko 23.0.1 jailbreak chain has been confirmed.

These results narrow the search and help decide where further effort is worthwhile. They do not mean the overall goal has been abandoned.

See the [evidence register](reports/EVIDENCE_REGISTER.md), [research findings](docs/RESEARCH_FINDINGS.md), [open questions](docs/OPEN_QUESTIONS.md), and [project roadmap](ROADMAP.md).

## Help move the jailbreak forward

Reverse engineers, Switch homebrew developers, embedded developers, exploit researchers, and AI-agent builders are welcome to contribute.

Useful contributions include:
- A new, technically credible software-only entry-point hypothesis for Mariko.
- A reproducible result on the exact hardware and firmware.
- Analysis showing how a known vulnerability could—or could not—apply to Mariko.
- A test that confirms or rules out a possible stage in an exploit chain.
- Better tooling, automation, reverse-engineering notes, or independent reproduction.

Start with [AI_AGENTS.md](AI_AGENTS.md), [CONTRIBUTING.md](CONTRIBUTING.md), and the [open research questions](docs/OPEN_QUESTIONS.md).

## Research principles

The target is ambitious, so evidence matters. Separate confirmed observations from hypotheses, simulations, and unverified claims. A crash, exposed API, or interesting behavior is a lead—not automatically an exploit. Record exact hardware and firmware scope, preserve reproducible results, and document failed approaches so the project does not repeat them.

Do not submit console secrets, private serials, proprietary firmware dumps, or destructive test payloads. See [SECURITY.md](SECURITY.md) for reporting and handling guidance.

## Repository map

- docs/ — target definitions, project history, research findings, and open questions.
- reports/ — phase reports, evidence registers, and recorded experiment results.
- research/agents/ — AI-assisted research work products; leads must be independently checked.
- lab/ — host-side models, experiments, and results.
- tools/ — local inspection, web-runtime, and read-only MTP diagnostics.
- references/libnx/ — small libnx source excerpts with their original license notice.
- tests/ — host-only validation tests.

The local Phase 15/16 Homebrew application and its source/build products are not included in this public repository.

## License

Project-authored code and scripts are MIT licensed; project-authored documentation is CC BY 4.0. Third-party excerpts retain their own license and notices. See [LICENSE](LICENSE).

## Reproduce host-side checks

Create a virtual environment with python3 -m venv .venv, activate it, and install requirements.txt. From the repository root, run:

    python3 -m unittest discover -s lab/tests -v
    python3 -m unittest discover -s tests/workspace-tests -v
    (cd tools/phase14-mtp && python3 -m unittest -v test_validate_phase14.py)

These checks validate local tooling and models; they do not test or jailbreak a Nintendo Switch.
