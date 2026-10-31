# Open questions

1. Can the intended physical target's SoC/revision be verified through a lawful, non-invasive source that does not require homebrew or opening the device?
2. Is there new, public, independently reproducible research for Switch 1 Mariko on HOS 20.x–23.0.1 that is reachable before unsigned user code?
3. Which specific public claims about web applets/services identify a privilege boundary and an exact firmware scope, rather than merely an exposed API?
4. Can an authorized, integrity-verifiable HOS executable/metadata artifact be obtained for analysis without circumventing access controls or redistributing proprietary material? If not, which public symbols/specifications can narrow the question without pretending to represent the binary?
5. Can Phase 14's standard MTP experiment be repeated after restoring ordinary USB enumeration, and does any new, non-invasive observation change the conclusion? Stop if only IDs or sentinel values vary without impact.
6. What independent review would falsify the project's current no-demonstrated-entrypoint conclusion?

A new experiment should answer one question, name a stop condition, and have a plausible path to new evidence. Do not extend closed MTP or SDK branches solely to generate activity.
