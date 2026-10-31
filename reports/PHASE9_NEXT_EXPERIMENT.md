# PROJECT ZERO — Phase 9: another experiment

## The only recommended next step

**First obtain the authorized, unencrypted and hash-identified binary artifact of stock HOS 23.0.1, then perform its offline callability audit.** The specific target should be a single stock system module or stock applet, not another SDK library. Input must contain trusted build metadata and documentation of its user/IPC permissions; acquisition may not require console keys or console intervention.

### Tested question

Can a stock HOS 23.0.1 application reach a selected parser/service path through a normally allocated interface, and in what context is that path executed? Static analysis should map imports/entrypoints, IPC boundaries and security assumptions. Without a reproducible bug and proof of permissions, the finding will not be marked as a vulnerability.

### Continue/terminate criteria

Continue only if:

1. the origin of the artifact and its HOS 23.0.1 build can be verified without secret keys;
2. the artifact belongs to a stock component that is executed before Homebrew or is callable by a stock application;
3. it is possible to determine its trust boundary and entry path from the artifact itself or trusted documentation.

Exit without experiment if a legal and verifiable binary is not available or if the only available input requires Homebrew already running. **In its current state, these assumptions are not met**, so further analysis of the target code now has no meaningful input. The specific next step is an artifact-acquisition gate, not further modeling or continuing in Phase 7/8 library tracks.

## Why this step has the highest informational value

Removes a major lack of evidence: so far we've only analyzed the public SDK and host models, not the stock HOS 23.0.1 component. A single hash-identified stock binary target would make it possible to see what the code actually contains and which inputs lead to it; however, it still would not by itself prove runtime impact on Mariko or the existence of a homebrew entrypoint. Without the artifact, any further fuzz experiment would only test our approximation.

## Current decision

It is now impossible to perform meaningful pre-homebrew experimentation on Nintendo code in the local tree. No new, reproducible security entry has yet been found for Mariko/T210B01 + HOS 23.0.1. Phase 7/8 library results remain archived but do not advance the reachability of the stock system.
