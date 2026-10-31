# Experimental results

## Method and limits

All runs are on Mac over artificial models. The input events, required invariants, and candidate errors are synthetic. The candidate contains intentional errors to verify the sensitivity of the detector. It is not a Horizon OS emulation.

## Cycle A — generation and order

The catalog created **50** distinct hypotheses in 10 areas. The ranking uses transparent testability, security and interdisciplinarity scores; it is not about the probability of vulnerability. The outputs are `hypotheses/catalog.json` and `results/ranked_hypotheses.json`.

## Cycle B — implementation of top experiments

1. **Handle lifetime:** the reference automaton assigns monotonically unique identifiers. The candidate reuses them after the error inserted by close.
2. **Cancellation of pending work:** the reference automaton cancels the pending status; the candidate leaves it in the negative branch.

These contracts were chosen for simplicity and total falsifiability. They are not an assertion that a particular Horizon IPC interface has the same contract.

## Cycle C — runs actually performed

- Bounded BFS checked all sequences above `{open, use(0), close(0)}` up to depth 2: **13 sequences, no difference**.
- At depth 3, the difference was found in the sequence `open, close(0), open`; the search stopped at the first hit after 20 sequences checked, so it is not full coverage for this depth.
- A run with a depth of 5 repeated the same minimum difference; stopped at the first find.
- Seeded control is a deterministic generator from the Python standard library, i.e. property-based style without external Hypothesis dependency; each seed is reproducible.
- Seeded negative control: **200 routes × 32 operations** with embedded error disabled; 200/200 matched, 0 differences.
- Metamorphic test: two independent closes in opposite order had the same resulting reference state.
- Cancellation: enumeration finds `prepare, cancel` as the first difference after 6 checked sequences. The model contract requires the pending status to disappear after cancel.

## Cycle D — reduce and repeat

Handle counterexample shrunk to `open → close(0) → open`. Deleting any one step will remove the difference; it is a 1-minimum trace according to delete operations. Parameter values ​​are not reduced.

Validator ran the trace again, confirmed the match of the reference model with the second oracle and the difference of the candidate with the oracle in the same step. When the defect is switched off, the difference does not appear. Cancellation reduced to `prepare → cancel`; here the candidate immediately leaves the pending status.

## Cycle E — new hypotheses from the results

`hypotheses/followups.json` includes an automatically generated follow-up: remove each step and mutate parameters after finding a difference; when passing a negative control, expand the depth and seed. It is not proof; it is a plan derived from observation.

## Cycle F — skeptical review

The skeptic found that the early differential engine overlooked state deviations when the answer still matched. The engine has been fixed to compare both events and the normalized state after each step. The validator has been enhanced with the same-step oracle comparison. Limitations that remain: oracle shares the monotonic ID specification; coverage is small; the minimizer does not change the values; the candidate's mistakes are inserted on purpose.

## Cycle G — direction by result

Since the handle error is isolated to identity allocation, the next experiment was chosen from a different class of properties: cancellation and rollback. This model was run and its embedded error was found. Another unfulfilled direction is the loss of confirmation and retries of an idempotent operation, or a delayed response after a session reset.

## Reproduction and artifacts

```sh
cd PROJECT_ZERO
python3 -m engine.run_campaign
python3 -m unittest discover -s tests -v
```

Key files: `results/campaign_summary.json`, `results/cancel_recovery.json`, `results/execution.jsonl`, `results/test_output.txt`, `results/discoveries.sqlite3`. Model SHA-256 hashes are in the relevant entries. The full campaign shell outputs are in `results/campaign_stdout.json`.
