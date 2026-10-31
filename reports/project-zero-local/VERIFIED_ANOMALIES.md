# Verified anomalies

## Status

**No anomaly has been verified in Horizon OS, firmware, or on the console.** The following are anomalies in intentionally faulty synthetic candidates; their verification confirms the discovery test, not a platform bug.

### Synthetic anomaly A — identifier reuse

- Model: `synthetic_handle_lifecycle_v1`
- Model contract: an issued handle is unique and must not be assigned to another object after close.
- Minimized trace: `open → close(0) → open`.
- Result: the reference automaton issues 0 and then 1; the candidate issues 0 and then 0 again.
- Checks: replay passed; the second implementation/oracle agreed with the reference model; the bug-disabled control passed; deleting any one step removed the difference.
- Evidence: E2 only for this synthetic contract; model hash is in `results/campaign_summary.json`.

### Synthetic anomaly B — pending state after cancel

- Model: `synthetic_deferred_cancel_v1`
- Model contract: after terminal `cancel`, no operation may remain pending.
- Minimized trace: `prepare → cancel`.
- Result: the faulty candidate retains a pending state; the correct model clears it.
- Checks: replay passed; the bug-disabled control matches.
- Evidence: E1 synthetic model; `results/cancel_recovery.json`. This second model does not yet have a separately coded oracle, so it is not labeled E2.

## Explicit limitation

These behaviors were intentionally inserted into our models in advance. They are not new vulnerabilities, evidence about system services, or Mariko compatibility results. Their value is that the framework found and minimized two distinct types of artificial difference and showed which independent checks are needed.

## Phase 5 addendum (October 30, 2026)

Phase 5 extended validation with argument shrinking, an independent cancellation oracle, and a third lost-ack/retry toy model.

- **A — handle identity:** E2 in the synthetic model. Seed 20261030, depth 3; the first difference appeared after 20 checked sequences. The complete depth-3 traversal later exhausted all 40 sequences and found 1 difference. Reduction input: `open, close(0), open, use(99)`; argument reduced `99→0`, redundant `use` removed; minimum `open, close(0), open`. Oracle agrees with reference; candidate mismatch at index 2; bug-off is clean. Model SHA-256 `7148712c559b78fa9c27890b13fe84170309c28afa2bb5c1d17fc601dd87433e`; engine bundle SHA-256 `fecf899fe54a401f181616b15ad47fc694e3e32e82a2437e94d7c8127f63ea50`.
- **B — pending after cancel:** raised from E1 to **E2 synthetic second implementation**. Seed 0, depth limit 4, 6 sequences until the first difference; input/minimum `prepare, cancel`; oracle agrees with reference, candidate mismatch at index 1, bug-off clean. Model SHA-256 `8a827a6b9577db9f93439ea4f9fe7a459fe1098b091996afeb67274e47e0b5af`; experiment SHA-256 `9f8f0cb0197275ccdf736145dd3b4aa3f051c610d1c61b3c710779a257c20ed6`.
- **C — retry after lost ACK:** new intentionally faulty toy candidate; E2 only for the model. Seed 0, depth 4, all 121 sequences; input/minimum `send, lose_ack, retry`; oracle agrees with reference, candidate differs at the same step, bug-off clean. Model SHA-256 `6aab62e802ec31569c785a290591c149532d587241ae99ec1be4cec416c92fe4`; experiment SHA-256 `f260a53c4ad00921543262942798f41f66add7ed1ad8b20eaf5f06ad4e7bdc01`.

All three candidate defects were deliberately injected. They are not vulnerabilities or evidence of HOS/Switch/Mariko behavior. Details and exact BFS scope are in `PROJECT_ZERO/reports/PHASE5_EXPERIMENTS.md` and `manifests/phase5_manifest.json`.
