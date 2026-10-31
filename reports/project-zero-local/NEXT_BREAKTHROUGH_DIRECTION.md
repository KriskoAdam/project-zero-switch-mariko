# The following direction to the breakthrough

## Recommended experiment: lost confirmation and retries

Another separate model family is to distinguish:

1. the client sends an operation with a declared idempotency key;
2. the service confirms the status change;
3. the response is lost or delayed;
4. the client repeats the request;
5. both the final status and accounting are examined.

**Falgiable property:** for an operation whose toy contract explicitly declares idempotency by key, all sequences with one to three retries have the same final state as one successful execution.

**Experiment:** independent reference transaction table and candidate with optionally embedded bug; bounded enumeration of response loss point, sequence retry and session reset; reduce every difference; independent oracle and bug-off check. The result should only be considered a confirmation of the framework until the public contract of the real interface is found.

## Why this direction

The first model found the handle identity problem; the second model tested cancellation. Retries after an ambiguous result is a third, distinct property: the interaction of protocol, lifecycle, and network/response errors. Other suitable directions from the inventor are old response after session reset, partial acknowledgment between two synthetic services, and cleanup idempotence.

## Gate before transfer to real artifact

Before any conclusion about HOS, the publicly documented message/API contract and its version must be named. It would then be possible, if the user supplies a legally obtained unprivileged artifact, to just add a static check for the relevant parser/stub. Without the artifact, we remain at E0–E2. No physical test is planned or anticipated.
