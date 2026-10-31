# PROJECT ZERO — Phase 5 experiments

**Results date:** October 30, 2026.
**Environment:** existing `switch-research/.venv`, Python 3.14.7. No packages were installed. All cases are synthetic; no Switch artifact or console was used.

## P0 — reproduction and integrity

Command: `.venv/bin/python -m unittest discover -s PROJECT_ZERO/tests -v`
Result: **11/11 tests passed**, recorded in `PROJECT_ZERO/results/test_output_phase5.txt`.

`campaign_summary.json` and `discoveries.sqlite3` record for handle cycles:
- seed, depth, number of sequences checked, and whether the limit was fully exhausted;
- `reference_matches_oracle`, `candidate_oracle_mismatch_indices`, and `same_step_divergence_confirmed`;
- `bug_disabled_control_diverges`.

| Run | Seed | Depth | Sequences checked | Complete? | Result |
|---|---:|---:|---:|---|---|
| `local-10-2` | 10 | 2 | 13 | yes | no difference |
| `local-20261030-3` | 20261030 | 3 | 20 | no; stop at first finding | finding |
| `local-77-5` | 77 | 5 | 20 | no; stop at first finding | finding |

A complete BFS at depth 3 checked all **40 distinct sequences** and found one anomalous sequence. The original run stopped after 20 at the first finding; the complete search added **20 sequences** after that first finding. BFS does not use state pruning/canonicalization.

## P1.4 — independent cancellation oracle

Model `synthetic_deferred_cancel_v1`; seed 0; maximum depth 4. Enumeration stopped at the first difference after 6 sequences, so this was not a complete depth-4 traversal.

- Input: `prepare → cancel`.
- Minimized trace: the same `prepare → cancel`.
- Correct reference matches the separately implemented oracle: yes.
- Candidate differs at the same index 1: yes; the intentionally faulty candidate retained a pending state.
- Bug-disabled control: clean.
- Model SHA-256: `8a827a6b9577db9f93439ea4f9fe7a459fe1098b091996afeb67274e47e0b5af`.
- Experiment SHA-256: `9f8f0cb0197275ccdf736145dd3b4aa3f051c610d1c61b3c710779a257c20ed6`.
- Rating: **E2 synthetic second implementation** under the Phase 5 criteria.

## P1.5 — complete depth-3 enumeration

`explore(max_depth=3, stop_at_first=False)` exhaustively traversed 40 sequences from the alphabet `open`, `use(0)`, `close(0)`. The original stop-at-first run checked 20 sequences and stopped at one error. The full traversal checked 40 unique sequences and found one differing sequence. This is a property of a small toy automaton, not a platform.

## P1.6 — argument minimization

The minimizer now reduces numeric handles toward zero and then removes operations. For the reduction input `open → close(0) → open → use(99)`, it recorded `use(99) → use(0)` and then removed the redundant `use` operation. The result remained `open → close(0) → open` and is 1-minimal under deletion of individual operations.

The argument to `close(0)` has no lower nonnegative value. It therefore remains minimal under argument reduction in the declared handle domain `handle ≥ 0`. This is a shrinker test on an injected model difference, not a claim about real handles.

## P1.7 — idempotent operation, lost acknowledgment, and retry

The new hypothesis `P5-RETRY-001` is in `PROJECT_ZERO/hypotheses/phase5_followups.json`, with an explicit falsification criterion.

- Model: `synthetic_idempotent_retry_v1`; seed 0; depth 4.
- All 121 sequences were enumerated; 10 generated trace variants reached a difference in the bugged candidate. These are not 10 independent bug classes.
- Input/minimum: `send → lose_ack → retry`.
- The reference matches the independent ledger oracle; the candidate differs at the same step; bug-off is clean.
- The candidate contains an intentional failure to deduplicate the idempotency key.
- Model SHA-256: `6aab62e802ec31569c785a290591c149532d587241ae99ec1be4cec416c92fe4`.
- Experiment SHA-256: `f260a53c4ad00921543262942798f41f66add7ed1ad8b20eaf5f06ad4e7bdc01`.
- Rating: **E2 synthetic second implementation**. This is not a finding about HOS IPC, networking, or a service.

## Findings and limits

A. **Handle reuse:** seed 20261030/depth 3; trace `open → close(0) → open`; bug-off is clean; the oracle agrees with the reference and differs from the candidate at index 2; E2 in the synthetic model. Model hash and engine bundle hash are in the run JSON/manifest.

B. **Pending state after cancel:** seed 0/depth 4; trace `prepare → cancel`; bug-off is clean; the oracle agrees with the reference and differs from the candidate at index 1; E2 in the synthetic model.

C. **Lost-ack retry:** seed 0/depth 4; trace `send → lose_ack → retry`; bug-off is clean; oracle/reference agree, and the candidate differs at the final step; E2 in the synthetic model.

**All A/B/C defects were intentionally injected. They say nothing about Horizon OS, Switch, HOS 23.0.1, or Mariko/T210B01.** No E3+ result exists.

## Hash manifest and logs

SHA-256 values for sources and models: `manifests/phase5_manifest.json`.
Runs: `results/local-*.json`, `results/campaign_summary.json`, `results/cancel_recovery.json`, `results/lost_ack_retry.json`, `results/execution.jsonl`, and `results/discoveries.sqlite3`.
Test output: `results/test_output_phase5.txt`.
