# PROJECT ZERO — Software-Only Mariko Jailbreak Research

**Can Nintendo Switch V2 (Mariko) be jailbroken through software alone, without installing a modchip? PROJECT ZERO is working to find out.**

PROJECT ZERO is an independent, AI-assisted research project with a concrete goal: discover and validate a reproducible software-only entry point that can lead from a stock Nintendo Switch V2 / Mariko to unsigned native code execution and homebrew.

The main target is Horizon OS 23.0.1. The challenge is that older Switch exploits do not automatically work on Mariko, and a homebrew environment is not useful unless there is a way to reach it from a stock console.

## What we are investigating

The project is exploring possible starting points in WebKit and system applets, Horizon OS services and IPC, USB/MTP behavior, and other software components reachable on stock firmware. We are also comparing public Switch exploit research against the exact Mariko hardware and firmware target.

So far, no working software-only jailbreak or complete Mariko 23.0.1 exploit chain has been demonstrated by this project. The Web Auth Applet and USB/MTP work has produced useful observations, but not an exploit. We publish that status plainly so contributors can see what remains unsolved.

## Help us find the missing entry point

We welcome Switch homebrew developers, reverse engineers, embedded developers, exploit researchers, and AI-agent builders.

We are especially interested in:
- Credible software-only entry-point ideas for Mariko.
- Reproducible findings on the exact hardware and firmware.
- Reverse engineering and analysis of relevant system components.
- Tests that validate or rule out stages of a possible exploit chain.
- Independent reproduction and technical criticism.

The goal is a working jailbreak, not a collection of speculative claims. Every useful contribution should help move the project closer to a reproducible stock-to-homebrew path.

Start with the README, AI agent guide, contribution guide, and open questions.
