# Mariko Software-Only Jailbreak Research

## Primary objective

Find and validate a software-only route from a stock Nintendo Switch V2 / Mariko console to unsigned native code execution and homebrew, without a modchip or hardware modification.

The primary firmware target is Horizon OS 23.0.1. The hardware target is Switch V2 / Mariko, commonly associated with T210B01 / Tegra214. The exact SoC identity of the physical test console has not yet been independently verified.

## What counts as progress

A useful research lead should answer one or more of these questions:

- Is the candidate component reachable on a stock Mariko system?
- Does a specific behavior represent a real vulnerability?
- Which exact hardware revisions and firmware versions are affected?
- What capability does the issue provide?
- Does the result cross a meaningful process or privilege boundary?
- Could it contribute to a route to native unsigned code execution?
- Can another researcher reproduce the result?

A complete success requires more than finding an interesting bug. The project ultimately needs a reproducible chain from a stock starting point to native homebrew execution.

## Research areas

Current and potential areas include the Mariko boot chain, WebKit and system applets, Horizon OS services, IPC, USB/MTP, and public exploit research. These are candidate areas to investigate, not assumptions that any particular component is vulnerable.

## Compatibility discipline

Public research on Erista, Switch 2, older firmware, SDK libraries, or already-running homebrew is not automatically applicable. Record the full hardware and firmware scope and identify which stages were actually reproduced on the target.

## Current status

No reproducible software-only entry point or complete jailbreak chain for Mariko / HOS 23.0.1 has been demonstrated by this project. Current observations and closed hypotheses are recorded in the evidence register and phase reports. The lack of a demonstrated chain is the problem PROJECT ZERO is trying to solve.
