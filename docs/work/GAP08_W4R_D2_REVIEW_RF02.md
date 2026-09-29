# GAP-08 W4R-D2 Independent Review RF02

Reviewed runtime:

`2e87d00f9cf546911dc48f7dc784a8bb1d14ff84`

Mechanical intake:

`MECHANICAL_INTAKE_PASS / SEMANTIC_REVIEW_REQUIRED`

Disposition:

`W4R-D2 HOLD / RF02_REQUIRED`

The RF01 runtime is retained. RF01 transaction composability and continuity-gap linkage are accepted candidate material.

## RF01 accepted candidate material

RF01 successfully corrected:

1. current-transaction composability:
   - standalone `PostgresExecutionStateLoader.load()` keeps `REPEATABLE READ READ ONLY`;
   - D2 resolver uses `_load_current_transaction()`;
   - D2 resolver does not reset transaction characteristics.

2. continuity gap linkage:
   - deterministic exact `SequenceGap` fingerprint;
   - exact equality with `ContinuityTransitionReceipt.gap_set_fingerprint`;
   - stale/mismatched gap world fails closed.

Execution evidence:

- targeted: `75 passed`
- compatibility: `105 passed`
- full regression: `1360 passed / 4 skipped`
- user-observed 5HR: `17%`
- semantic correction cycles: `0`
- test assertion correction: `1`
- tooling route switches/retries: `2`

## RF02 blocker — broker report witness is not generation scoped

Frozen D2 contract requires current broker-report disposition/evidence for the selected:

`BrokerAccount + active recovery generation`

Current D2 resolver does this for root material:

```text
SELECT report_json
FROM trading.broker_report_inbox
WHERE broker=%s
  AND account_ref=%s
  AND generation=%s
```

but separately constructs bundle `broker_report_witness` using:

`_read_report_witness(cursor, account)`

The accepted legacy helper filters only by BrokerAccount and therefore includes rows from every historical generation.

That helper is valid as an existing C12 broad currentness witness and must not be changed globally in RF02.

However using it for the D2 bundle can bind historical-generation report/application disposition into the selected current recovery world.

This violates D2 same-world authority and would make D3 pure readiness classification susceptible to historical-generation contamination.

## Required correction

Add a separate generation-scoped report witness helper in:

`persistence/postgres/recovery.py`

Requirements:

- same deterministic latest-application semantics as `_read_report_witness`;
- exact filters:
  - broker;
  - account_ref;
  - generation;
- no timestamp-based latest selection;
- exact `application_sequence` remains authority;
- deterministic ordering;
- caller cannot provide the witness;
- no commit/rollback/write/lock.

Use this generation-scoped helper only for D2 trusted bundle resolution.

Do NOT change existing `_read_report_witness` behavior used by C12 / `PostgresAccountReadinessGate`.

## Counterexamples

RF02 must prove:

1. D2 generation 4 witness excludes generation 3 history for the same BrokerAccount;
2. D2 witness includes exact generation 4 current disposition;
3. latest application uses `application_sequence`, not `recorded_at`;
4. D2 SQL includes broker/account/generation predicates;
5. legacy C12 `_read_report_witness` remains unchanged in behavior/signature;
6. D2 resolver still performs no write/commit/rollback/`FOR UPDATE`;
7. no D3 READY/handoff code appears.

## Governance

- W4R-A/B/C and D1A/D1B remain accepted/frozen.
- W4R-D2 remains HOLD until RF02 independent review.
- W4R-D3 remains NOT_AUTHORIZED.
- internal W4R accepted weight remains `13/18`.
- official correction core remains `75/113`.
- W4 weight remains `18 / NOT_CREDITED`.
