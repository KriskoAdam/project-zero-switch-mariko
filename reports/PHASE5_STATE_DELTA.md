# Phase 5 — project status differences

**Check:** 30/10/2026. Older reports were not overwritten.

## Check of required documents

All content inputs listed in the entry are present: four Phase 4 messages, `reports/UNRESOLVED_QUESTIONS.md`, `reports/vulnerabilities.json`, `reports/ENVIRONMENT.md`, `reports/BINARY_ANALYSIS_READINESS.md`, `PROJECT_ZERO/README.md`, and all seven messages in `PROJECT_ZERO/reports/`.

**Name deviation:** the entry text refers to `PHASE4_GE​​ZINE_INVESTIGATION.md` where there is an invisible character U+200B between "GE" and "ZINE". There is no such name on the disk. The actual file is `reports/PHASE4_GEZINE_INVESTIGATION.md`, its content corresponds to the handoff. It is not a missing report.

Desktop AI handoff `Switch_Mariko_Project_AI_Handoff.txt` exists and summarizes phases 1–4 and the first iteration of PROJECT_ZERO. Phase 5 expanded PROJECT_ZERO; older reports were left as historical records. Therefore, the figure of "8/8 tests" in the original phase is historical; after expanding phase 5 the result is 11/11.

## Additions to Phase 5

- Campaign now fully enumerates depth 3: 40 distinct sequences; the original stop-at-first-find run stopped after 20. Added 20 sequences after the first find.
- Minimizer now shrinks numeric arguments towards zero and removes steps. Handle trace remained `open → close(0) → open`.
- The cancellation model received a separately coded oracle and met the criteria at the E2 synthetic level.
- Added full synthetic lost-ack/retry experiment with idempotency key.
- `.venv` tests after expansion: 11/11 passed.
- Public status as of 10/30/2026: Nintendo lists HOS 23.0.1 as the latest original Switch firmware. Gez's new posts from October do not change Mariko's verdict; primary X links return 403 and secondary records do not provide Mariko model/FW or reproduction.

## Integration failure log

The first full run of the extended campaign stopped because BFS returns a tuple and the new minimizer needed a leaf. The unit tests passed in that run, but the campaign did not complete. Fixed the typecast and relaunched the campaign in the existing `.venv`. Final results are in `PROJECT_ZERO/results/campaign_summary.json`, `cancel_recovery.json`, `lost_ack_retry.json` and `test_output_phase5.txt`.

## What doesn't change

- No HOS artifact or dump was delivered/analyzed; the console was not used.
- `reports/vulnerabilities.json` was not changed because delta-check did not yield a new documented vulnerability to add. No new CVE or Mariko finding is expected.
- The verdict on Mariko 23.0.1 does not change.
