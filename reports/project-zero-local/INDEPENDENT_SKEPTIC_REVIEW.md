# Independent skeptical review

## Procedure

Inventor and Engineer independently contributed hypothesis ideas and architecture design; The skeptic was given a separate task to review the models, validation code, and actual outputs without modifying the files. His points were incorporated and the tests were repeated.

## The discovery that changed the implementation

The first version of `run_pair` only matched `accepted` and the ID at `open`. She could overlook a different normalized state. I fixed it so that it also compares the semantic state `next_handle/live` after each step; the record now preserves both sides and distinguishes the event difference from the state difference.

The validator initially only found that the candidate was different from the oracle. It has been modified to same-step indexes: the reference implementation must agree with oracle, and the candidate difference must be at the same index as the reported difference. After adjustments, 8/8 tests passed and all three hand runs were restarted.

## Other reservations and response

- **Inserted defect:** true. The result is a detector test, not the discovery of an unknown error.
- **Common specification of reference and oracle:** possible common-mode risk remains. Oracle uses a different token representation, but both implement the same simple contract.
- **Limited model:** BFS handle uses only `open`, `use(0)`, `close(0)`, without concurrency or resource quota; BFS stops at the first find.
- **Minimization:** deleting operations is 1-minimal; identifier values ​​or event types are not shrunk.
- **Negative check:** 200 seeded routes only check the model with embedded error turned off, not the realistic base.
- **Catalogue:** 50 candidates, but only two families of experiments were performed.
- **Evidence boundary:** everything is run locally on synthetic implementations. Mariko/HOS have not been tested.

## The skeptic's conclusion

The evidence is sufficient to claim that the discovery pipeline caught these two embedded model differences and that the handle difference passed both an independent second implementation and a bug-disabled check. Not enough to make any claim about a Nintendo system. Further investments are to first extend and validate generic protocol models before mapping documented contracts from legal artifacts.
