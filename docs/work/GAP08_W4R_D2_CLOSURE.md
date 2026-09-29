# GAP-08 W4R-D2 Closure

Final accepted runtime:

`6aa0b51b6c550a4eef46b680de70b7f326c216f8`

Disposition:

`W4R-D2 ACCEPTED / FROZEN / READ_ONLY`

Parent W4R-D:

`PARTIAL / D3 NEXT`

Internal W4R accepted weight remains:

`13 / 18`

Official correction-core acceptance remains:

`75 / 113`

W4 weight remains:

`18 / NOT_CREDITED`

## Accepted D2 authority

D2 establishes an immutable resolver-produced:

`TrustedReadinessEvidenceBundle`

that binds one BrokerAccount recovery world across:

- active recovery generation;
- recovery-cut revision;
- ingress version;
- readiness revision;
- canonical RecoveryCut fingerprint;
- AccountStateHead/checkpoint/authority receipt;
- exact expected snapshot and authority-commit identity;
- current continuity head;
- head-selected continuity epoch;
- exact continuity transition receipt;
- deterministic durable SequenceGap material;
- generation-scoped broker-report disposition witness;
- BrokerAction semantic state;
- C13 blocker evidence;
- B1/B2 discovery/reconstruction/observation/capability evidence;
- exact C14 boundary/outcome;
- C2 recovery root set and exact closure.

The bundle fingerprint is derived from canonical material and cannot be caller-overridden.

## Same-world rules accepted

D2 fails closed on identity/material mismatch including:

- BrokerAccount mismatch;
- recovery generation mismatch;
- recovery-cut mismatch;
- authority closure mismatch;
- expected snapshot / authority receipt mismatch;
- continuity head/epoch/transition mismatch;
- transition recovery-cut/account/snapshot/authority mismatch;
- durable gap set vs transition `gap_set_fingerprint` mismatch;
- C13 blocker account mismatch;
- C14 formal-run world mismatch;
- C2 root/closure mismatch;
- BrokerAction account mismatch;
- missing exact trusted B2 evidence.

Historical continuity epochs never substitute for the head-selected epoch.

Caller booleans/fingerprints do not grant trusted authority.

## RF01 accepted corrections

Final RF01 runtime:

`2e87d00f9cf546911dc48f7dc784a8bb1d14ff84`

Accepted:

1. transaction composability:
   - standalone `PostgresExecutionStateLoader.load()` retains `REPEATABLE READ READ ONLY`;
   - D2 resolver uses current-transaction pure read helper;
   - D2 resolver does not reset transaction characteristics and is composable after a D3 control lock.

2. continuity-gap linkage:
   - durable exact SequenceGap material is deterministically fingerprinted;
   - derived fingerprint must equal transition receipt `gap_set_fingerprint`;
   - stale transition gap world fails closed.

RF01 verification:

- targeted: `75 passed`
- compatibility: `105 passed`
- full regression: `1360 passed / 4 skipped`
- user-observed 5HR: `17%`

## RF02 accepted correction

Final accepted runtime:

`6aa0b51b6c550a4eef46b680de70b7f326c216f8`

RF02 corrected D2 broker-report witness scope.

Accepted behavior:

- D2 report disposition is scoped by:
  - broker;
  - account_ref;
  - selected active recovery generation;
- latest application remains selected by `application_sequence`, never wall-clock time;
- application join binds exact ingress + generation;
- deterministic ordering remains;
- existing C12 `_read_report_witness(cursor, account)` remains unchanged and BrokerAccount-wide;
- D2 alone uses the new generation-scoped helper.

RF02 verification:

- targeted: `38 passed`
- compatibility: `123 passed`
- full regression: `1361 passed / 4 skipped`
- exact two-file scope: PASS
- semantic correction cycles: `0`
- tooling retries: `0`
- user-observed 5HR: `10%`
- migration / actual PostgreSQL / broker I/O: NO

Mechanical intake:

`MECHANICAL_INTAKE_PASS / SEMANTIC_REVIEW_REQUIRED`

Independent semantic review:

`PASS`

## Tooling learning retained

The accepted execution envelope is:

`CONTROLLED_ROUTE_SET`

Known reparse-point edit restrictions may route directly to controlled staging with exact-scope copy-back.

Pytest remains repository-local.

A tooling-route switch inside the authorized set is not a semantic reauthorization event.

## Freeze

D2 bundle and resolver semantics are now frozen/read-only.

D3 may consume/re-run the accepted D2 resolver under its final locked transaction, but may not weaken or duplicate D2 authority.

Any later D2 semantic change requires explicit reauthorization.
