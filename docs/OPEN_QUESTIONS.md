# Open Questions — The Missing Mariko Entry Point

PROJECT ZERO is trying to find a software-only route from stock Nintendo Switch V2 / Mariko to unsigned native code execution and homebrew. These questions identify the most useful gaps in the current research.

1. Can the test console's exact hardware revision and SoC be confirmed through reliable, non-invasive evidence?
2. Is there a publicly documented or independently reproducible software entry point for Switch 1 Mariko on a firmware range that includes HOS 23.0.1?
3. Which stock applets, browser components, system services, or protocols provide the most plausible reachable starting point before unsigned code is running?
4. Do any known WebKit, Horizon, IPC, or service vulnerabilities apply to the exact Mariko hardware and firmware target?
5. Can a candidate issue be shown to provide a meaningful capability such as controlled code execution or a privilege transition, rather than only a crash or ordinary API behavior?
6. If a useful primitive is found, what additional independently supported stages would be needed to reach native unsigned code execution?
7. Can any new evidence change the current conclusion from “no demonstrated entry point” to a reproducible candidate?

A useful experiment should answer a specific question and have a plausible path to new evidence. Repeating a closed test without a new hypothesis does not move the jailbreak effort forward.
