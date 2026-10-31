# Unsuccessful and not yet substantiated hypotheses

"Failed to refute in a given model" does not mean that the hypothesis holds on the platform.

| Hypothesis/Model Assertion | Result | Exact Range |
|---|---|---|
| Monotone candidate without embedded error differs from reference | Unconfirmed; indiscriminate | BFS sequences to depth 4 (3^0…3^4) and 200 seeded routes after 32 operations; only model input alphabet |
| The order of two independent closes changes the resulting state | In this case refuted | One metamorphic pair, two live sources, bug disabled; without errors, timeouts or competition |
| Handle-reuse difference arises in sequence shorter than 3 operations | Disproved in model | Full BFS check to depth 2: 13 sequences without difference; first difference of length 3 |
| Handle reuse is a property of Horizon/Mariko | Untested | No source code, legal artifact, trace or device test |
| Canceling pending work leaves status in Horizon | Untested | Only artificial candidate/reference pair |
| Another 48 of 50 hypotheses | E0 — unexecuted | Catalog contains designs; we do not pretend experiments for all areas of |

No failed synthetic path translates to "all real paths are safe". Each conclusion is limited by the model and scope of the enumeration.

## Phase 5 Addendum

- Handle model without embedded error: 13/13 sequences to depth 2 without difference and 200 seeded routes after 32 operations without difference. These results are limited to only the toy alphabet and implementations.
- Full depth-3 traversal: 40 unique sequences, 1 embedded anomalous path; the first stop-at-first run found the same route after 20 and fell incomplete.
- Argument shrinking does not change the counterexample handle core; `close(0)` is already a minimal non-negative argument.
- Lost-ack retry: declared toy contract and bug-off/reference oracle match; only a deliberately faulty candidate without deduplication idempotency will cause an error. It cannot be transferred to any real service.
- Public delta-check until 30/10/2026: no new public proof bound to Mariko/T210B01 + HOS 23.0.1. X 403 is unverified, not disproved. The public Nintendo update still lists 23.0.1 and a functional patch; a new security fix is ​​not expected.
