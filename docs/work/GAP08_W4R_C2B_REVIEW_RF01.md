# GAP-08 W4R-C2B Independent Review — RF01 Required

Reviewed runtime candidate:

`515bbcca04b7afa69737b713f71f8267bc182ffb`

Execution baseline:

`a19ed9df93ff6f2e24e02daec6f0f139e4464be7`

Disposition:

`HOLD / W4R_C2B_RF01_REQUIRED`

Official correction-core acceptance remains:

`75 / 113`

W4 weight remains:

`18 / NOT_CREDITED`

W4R-A / W4R-B / W4R-C1 / W4R-C2A remain:

`ACCEPTED / FROZEN / READ_ONLY`

## Mechanical result

PASS:

- exactly one C2B runtime commit;
- master == runtime candidate;
- exactly two authorized files changed;
- no migration changes;
- no actual PostgreSQL/V07/A08/broker I/O claimed;
- no READY/finalize/handoff authority added.

Executor evidence:

- targeted = 63 passed;
- compatibility = 67 passed;
- full regression = 1329 passed / 4 skipped;
- semantic correction cycles = 1;
- tooling retries = 3;
- diff ~= +257 / -3;
- user-observed 5HR consumption = 17%.

## Accepted C2B work retained

Retain:

- exact root Order read;
- exact embedded Order identity validation;
- bounded OMS/ORDER event read using `Order.version + 2` limit;
- unique event ID and sequence validation;
- exact contiguous sequence `0..Order.version`;
- event envelope type/source/entity/scope checks;
- canonical OrderEvent decode;
- frozen lifecycle transition validation;
- final event version/status/correlation/projection agreement;
- complete Fill set by exact Order ID;
- Fill identity/order/event/correlation/causation validation;
- filled quantity equality;
- exact weighted average-fill-price equality;
- deterministic Fill sorting;
- deterministic Order/Event/Fill material fingerprints;
- C2A ambiguous ingress IDs carried forward unchanged;
- no global history scan;
- no READY/finalize/handoff surface.

## Material blocker — Canonical Event identity/linkage is not fully sealed

Architect AD-04 defines canonical Event identity as:

- immutable `event_id`;
- verified entity identity;
- sequence;
- idempotency identity.

It also requires invalid linkage / identity conflict to fail closed.

Current C2B verifies event ID uniqueness and sequence uniqueness, and checks the expected `ORDER_EVENT:<order_id>` idempotency scope, but does not verify that idempotency identities are unique across the exact Order event sequence.

A sequence can therefore contain:

- distinct event IDs;
- distinct contiguous sequences;
- the same `(idempotency_scope, idempotency_key)` more than once;

and still pass C2B.

That is not a valid canonical Event identity set.

## Material blocker — Event causation chain is not revalidated

The frozen execution write contract requires:

- sequence 0: `causation_id == Order.intent_id`;
- sequence N>0: `causation_id == previous_event.event_id`.

`validate_order_event_transition()` validates sequence/status/correlation but does not validate causation.

C2B currently reuses `validate_order_event_transition()` without restoring this linkage invariant.

A persisted event can therefore keep valid sequence/status while its causation link is corrupted and still pass recovery closure.

AD-04 requires invalid linkage to fail closed.

## Required correction

For each exact root event sequence:

1. derive canonical idempotency identity as:
   `(event.idempotency_scope, event.idempotency_key)`;
2. require all identities unique across the sequence;
3. sequence 0 must have:
   `causation_id == Order.intent_id`;
4. every later event must have:
   `causation_id == previous_event.event_id`;
5. mismatch => `RecoveryClosureIntegrityError`.

Do not change event source/type/scope semantics or lifecycle transition table.

## Required counterexamples first

1. two otherwise valid events with duplicate idempotency identity => fail closed;
2. sequence-0 event causation differs from `Order.intent_id` => fail closed;
3. later event causation differs from previous event ID => fail closed;
4. exact valid sequence continues to pass;
5. changed causation/idempotency material changes closure fingerprint as before;
6. no READY/finalize/handoff authority appears.

## Efficiency finding

C2B used 17% 5HR, but tooling retries returned to 3:

- external staging pytest common-root permission x2;
- Git index sandbox permission x1.

These are tooling, not semantic corrections.

RF01 must use the already-working direct import/test route and repository-local Git/index route immediately; do not retry the known-failing external/common-root route.

## Reviewer state

W4R-C2B remains unaccepted.

W4R-C overall remains partial.

W4R-D remains NOT_AUTHORIZED.

No GPT-6 escalation is required.
