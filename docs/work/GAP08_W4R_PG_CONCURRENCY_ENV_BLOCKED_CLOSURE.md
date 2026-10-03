# GAP-08 W4R PostgreSQL Concurrency Gate — Harness Closure / Environment Block

Harness commit: `fb61f9af96a2c7e507545e07e9ed04e44b270d7c`

Disposition: `HARNESS_ACCEPTED / ENV_BLOCKED / CONCURRENCY_NOT_VERIFIED`

W4R-D: `INTERNALLY COMPLETE / 18 OF 18`

Official W4 weight: `18 / NOT_CREDITED`

W4 closure: `BLOCKED_ON_REAL_POSTGRESQL_CONCURRENCY_EVIDENCE`

## Accepted harness

Accepted file: `tests/integration/test_w4r_recovery_concurrency.py`

Scope:
- one new integration file;
- `+311 / -0`;
- no production source changes;
- no migration source changes.

The harness uses real PostgreSQL connections and existing production repository owners.

### Scenario A

Two independent connections verify:
- active recovery-control row lock;
- concurrent broker ingress is excluded by PostgreSQL row locking;
- SQLSTATE `55P03` lock timeout;
- failed concurrent ingress rollback leaves no durable inbox row;
- handoff completes under the held recovery-control fence;
- post-handoff same-generation ingress is `recovery_active_at_capture = FALSE`;
- post-handoff ingress does not advance `ingress_version` or `readiness_revision`.

### Scenario B

Real PostgreSQL verifies:
- shared readiness fence advances `readiness_revision`;
- stale C09 handoff is rejected and control stays active;
- fresh readiness CAS permits handoff;
- generation / cut / ingress remain exact.

### Cleanup

Every scenario uses a unique BrokerAccount and cleanup deletes only exact test-owned rows.

## Review evidence

- configured PostgreSQL targets: none;
- actually executed PostgreSQL targets: none;
- targeted: `4 skipped`;
- PostgreSQL compatibility: `4 skipped`;
- full regression: `1383 passed / 8 skipped`;
- semantic corrections: `0`;
- tooling retries: `0`;
- user-observed 5HR: `14%`;
- TEST_DSN migration execution: NO;
- production/V07 DB access: NO;
- broker I/O: NO.

Mechanical intake: `MECHANICAL_INTAKE_PASS / SEMANTIC_REVIEW_REQUIRED`

Independent harness semantic review: `PASS`

## Environment block

At review time both `POSTGRES17_TEST_DSN` and `POSTGRES18_TEST_DSN` were not configured.

Therefore no real PostgreSQL concurrency evidence exists yet. Skipped tests do not establish gate verification.

## Current governance

- harness: ACCEPTED / READ_ONLY;
- PostgreSQL concurrency gate: NOT_VERIFIED;
- W4: HOLD;
- official W4 weight: NOT_CREDITED;
- P7: NOT_AUTHORIZED;
- V07 actual-environment conformance: NOT_ASSERTED;
- production activation: NOT_AUTHORIZED;
- runtime source modification: NOT_AUTHORIZED.

## Resume condition

After at least one explicit TEST_DSN is configured, run the accepted harness directly. No Codex/source-modification package is required merely to execute the environment verification.

If one target is set, it must run both concurrency scenarios and pass. If both are set, both must pass.

After real execution evidence is available, STOP for independent W4 final review.
