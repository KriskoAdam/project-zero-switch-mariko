# PROJECT ZERO — experimental mission summary

**Date:** October 30, 2026
**Goal:** create a falsifiable workflow for safe Mariko research without manipulating the console.

## Result

A runnable synthetic discovery framework was created: a 50-hypothesis catalog, heuristic ranking, bounded state-space exploration, explicit invariant checks, differential comparisons, trace minimization, a second oracle, seeded generated cases, and SQLite/JSON run records.

Three independent research roles contributed ideas (Inventor), experiment architecture (Engineer), and adversarial review (Skeptic). The skeptic's specific objection to differential comparison led to a fix, after which the runs were repeated.

The framework demonstrated that it can detect an **intentionally injected** defect in a toy candidate: identifier reuse after `open → close → open`. A third cycle and independent oracle reproduced this counterexample; disabling the injected defect removed the difference. A separate cancellation model found another injected defect after `prepare → cancel`. Both are results about synthetic models, not Horizon OS.

## What was learned

The strongest verifiable contribution is methodological: a declared contract, separately implemented models, bounded generation, minimization, an independent oracle, and a negative control. The skeptic found inadequate state comparison; the fix was included before the final runs. This increases confidence in the experimental framework itself.

## What this does not prove

No Horizon binaries, public code artifacts, or legally provided firmware were analyzed; the physical console remained untouched. No result confirms a flaw, entry point, or compatibility for Mariko/T210B01/HOS 23.0.1. Hypotheses are test proposals, not findings about Nintendo's implementation.

## Outputs

- [Original hypotheses and challenge plan](ORIGINAL_HYPOTHESES.md)
- [Experimental results](EXPERIMENTAL_RESULTS.md)
- [Verified synthetic anomalies](VERIFIED_ANOMALIES.md)
- [Rejected or unsupported hypotheses](FAILED_HYPOTHESES.md)
- [Independent skeptical review](INDEPENDENT_SKEPTIC_REVIEW.md)
- [Next research direction](NEXT_BREAKTHROUGH_DIRECTION.md)
- [Code and reproduction](../../README.md)
