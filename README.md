# PROJECT ZERO — AI-Powered Nintendo Switch Mariko Security Research

**An independent, evidence-first research project investigating whether a software-only homebrew entry point exists for Nintendo Switch V2 (Mariko / T210B01) on Horizon OS 23.0.1.**

> **Current result:** no reproducible software-only entry point for Mariko on HOS 23.0.1 has been demonstrated by this project. The physical console was not independently authenticated as Mariko/T210B01. This repository does not contain an exploit or a claim that one exists.

## The project

PROJECT ZERO began as one independent researcher working with a Nintendo Switch V2, a MacBook, and AI coding and research tools. The work combines careful source review, small host-side experiments, evidence audits, and limited observations from the owner-operated stock console. AI helped organize and review research; it did not magically discover or validate an exploit. We are opening the work so researchers can check the evidence, correct mistakes, and propose better experiments.

## LET'S USE THE POWER OF AI TO BREAK NINTENDO'S SOFTWARE SECURITY BARRIER

**AI researchers, reverse engineers, embedded developers, and skeptical reviewers: help us investigate the question with evidence.** Bring a reproducible result, a public source, a well-scoped experiment, or a careful counterexample. Clearly state the exact hardware, firmware, prerequisites, and what your evidence does *not* establish. We welcome AI-assisted work when its sources, generated steps, and results can be independently checked.

Start with [AI_AGENTS.md](AI_AGENTS.md), then see [Contributing](CONTRIBUTING.md), the [open questions](docs/OPEN_QUESTIONS.md), and [the roadmap](ROADMAP.md). Please do not submit payloads, keys, console dumps, private serials, or instructions to bypass protections.

## Scope and terminology

- **Primary target:** Nintendo Switch V2, commonly associated with Mariko; target silicon is T210B01/Tegra214, but the particular console's SoC has not been directly verified in our evidence.
- **Firmware target:** HOS 23.0.1, reported by the console owner and recorded in the device report.
- **“Switch V1 Mariko” is not used as a target label here.** V1 and Mariko are not interchangeable labels; submissions must identify the exact revision and evidence.
- The goal is feasibility research, not a promise to produce a jailbreak. This repository excludes the locally built Phase 15/16 native Homebrew application and all its source/build products.

## What has been observed

- The stock system's Wi-Fi web-auth applet loaded a benign local test page. DOM, Fetch/XHR and WebSocket checks ran in that applet session; this is not evidence of a vulnerability or native code execution.
- USB exposed a Nintendo device (`057e:201d`) with an MTP interface in the user-operated “copy to computer over USB” mode.
- Standard read-only MTP requests were exercised across nine sessions. The reported storage identifier changed after a user-controlled MTP mode restart; the observed responses remained consistent and no security anomaly was demonstrated.
- Host-side tests found and closed an off-by-one hypothesis in a public libnx callback contract. That SDK finding is not a stock-system entry point.
- Public research reviewed here, including ns2jb claims, does not establish a reproducible Switch V1/V2 Mariko entry point on HOS 23.0.1.

See [evidence register](reports/EVIDENCE_REGISTER.md), [USB/MTP notes](docs/USB_MTP.md), [web runtime notes](docs/WEB_RUNTIME.md), and the original phase records under `reports/`.

## Repository map

- `docs/` — concise project history, target definitions, methods, and open questions.
- `reports/` — preserved, privacy-scrubbed historical reports and evidence registers.
- `research/agents/` — prior agent work products; treat them as leads, not proof.
- `lab/` — host-side models, experiments, and results. Synthetic/model results are not target-device evidence.
- `tools/` — safe host-side inspection, local web test, and read-only MTP diagnostics.
- `references/libnx/` — small libnx source excerpts with their original license notice.
- `tests/` — host-only validation tests.

The local Switch Homebrew app project and all NRO/ELF/NACP/icon/release products are intentionally excluded. This repo contains no proprietary Nintendo firmware, console dump, keys, or extracted secrets.

## Responsible research

Read [SECURITY.md](SECURITY.md) and [Research method](docs/RESEARCH_METHOD.md). Never send unknown, malformed, destructive, or unbounded traffic to a console. Do not alter firmware, boot configuration, storage partitions, or security settings for this project. Report uncertainty rather than converting it into a claim.

## License

Project-authored code and scripts are MIT licensed; project-authored documentation is CC BY 4.0. Third-party excerpts retain their own license and notices. See [LICENSE](LICENSE) and `references/libnx/LIBNX_LICENSE.md`.

## Reproduce safe host checks

Create a virtual environment with `python3 -m venv .venv`, activate it, and install `requirements.txt`. From the repository root, run `python3 -m unittest discover -s lab/tests -v`, `python3 -m unittest discover -s tests/workspace-tests -v`, and `(cd tools/phase14-mtp && python3 -m unittest -v test_validate_phase14.py)`. These are host-only checks; they do not communicate with a console. See each tool README for dependencies and limitations.
