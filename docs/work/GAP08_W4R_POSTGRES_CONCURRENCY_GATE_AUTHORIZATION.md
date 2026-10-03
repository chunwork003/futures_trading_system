# GAP-08 W4R PostgreSQL Integration / Concurrency Gate Authorization

Status:

`BOUNDED_AUTHORIZED_FOR_W4R_POSTGRES_CONCURRENCY_GATE_ONLY`

Execution baseline:

`38198142b5d57141c38582508a31d292e4bf246c`

Dependencies:

- W4R-A ACCEPTED / FROZEN
- W4R-B ACCEPTED / FROZEN
- W4R-C ACCEPTED / FROZEN
- W4R-D ACCEPTED INTERNALLY / 18 OF 18
- W4 official weight remains NOT_CREDITED

## Purpose

Produce real PostgreSQL evidence for the shared recovery-readiness fence and atomic final-handoff claim.

This is an integration/concurrency verification gate. It is not a production-code package, not V07 production-environment conformance, and does not authorize broker I/O.

## Exact writable file

One new test file only:

`tests/integration/test_w4r_recovery_concurrency.py`

No other file may be modified by the executor.

No production source changes. No migration changes.

Need any source correction => STOP / REAUTHORIZATION.

## Authorized PostgreSQL environment

Only these explicit existing test variables may be used:

- `POSTGRES17_TEST_DSN`
- `POSTGRES18_TEST_DSN`

Rules:

- no fallback DSN;
- no production DSN;
- do not print/log DSN values;
- connect through existing `connect_postgres(...)`;
- validate `SHOW server_version_num` matches the declared major before test material is written;
- if a variable is absent, that exact major is SKIP / PENDING;
- if both are configured, both must pass;
- at least one configured test DSN must actually execute the concurrency tests before this gate can be declared VERIFIED.

If neither variable is configured:

`ENV_BLOCKED / HARNESS_READY`

The test harness may still be committed and pushed, but PostgreSQL concurrency verification remains NOT_VERIFIED and W4 closure remains blocked.

A configured DSN with missing Psycopg, wrong server major, SQL failure, lock failure, or cleanup failure is a real FAIL, not a skip.

## Migration setup

Reuse existing `discover_migrations(...)` and `run_migrations(...)`.

Apply the repository migration chain through current `0009` to the configured TEST database before concurrency scenarios.

Migration setup may commit in the TEST database so separate connections can observe the schema.

This authorization permits migration execution on the named TEST_DSN targets only.

It does NOT authorize production migration, V07 production/actual-environment conformance claim, or schema edits.

## Isolation / cleanup

Every scenario must use a unique test identity.

Suggested:

- broker: stable explicit test broker string;
- account_ref: prefix + PostgreSQL major + `uuid4`;
- ingress IDs: unique per scenario.

Tests must not depend on existing business/account data.

All connections must close in `finally`.

After scenario transactions are finished, cleanup using a separate TEST connection.

Cleanup must delete only rows owned by the exact unique test identity and must commit.

Cleanup failure fails the test.

Do not truncate shared tables or drop schema/database.

## Verification A — handoff lock vs broker ingress

Prove with two independent PostgreSQL connections.

### Setup

Create one active `AccountRecoveryControl` with known generation, ingress_version, readiness_revision, and `active=TRUE`.

Commit setup so both connections see it.

### Transaction A

Connection A must lock the exact active recovery control using the same row-lock semantics as D3:

`SELECT ... FROM trading.account_recovery_controls ... FOR UPDATE`

Prefer reuse of the existing D3 lock helper rather than a second test-only lock algorithm.

Do not commit yet.

### Transaction B

Connection B:

- set a bounded local `lock_timeout`;
- attempt real `PostgresBrokerRecoveryRepository.append_inbox(...)` for the same BrokerAccount/generation.

Expected while A holds the lock:

- the statement cannot pass the recovery-control lock;
- PostgreSQL returns lock-timeout / lock-not-available;
- B transaction is rolled back;
- no inbox row is durable;
- ingress_version/readiness_revision are unchanged.

Do not use arbitrary sleeps as authority.

Use PostgreSQL lock behavior plus a bounded timeout.

### Handoff under A

While A still owns the recovery-control lock:

- call existing C09 `finalize_handoff(...)` with exact generation/ingress/readiness fence;
- commit A.

Expected: control becomes inactive and no pending active-capture report existed inside the serialized window.

### Retry B after handoff

Retry the same-generation inbox append in a fresh B transaction.

Expected:

- append may be durably captured according to accepted C09 inactive-control semantics;
- `recovery_active_at_capture == FALSE`;
- it does not advance recovery ingress_version;
- it does not advance readiness_revision;
- finalized control remains inactive.

This proves post-handoff evidence cannot retroactively enter the active recovery frontier.

## Verification B — readiness CAS rejects stale handoff

Use a fresh unique BrokerAccount.

Setup active recovery control with known generation/cut/ingress/readiness and commit.

Use existing `PostgresRecoveryReadinessFenceRepository` to lock the active control, advance `readiness_revision` exactly once, and commit.

Then call existing C09 `finalize_handoff(...)` with the prior captured readiness revision.

Expected:

- `RecoveryFenceConflictError`;
- no durable inactive control;
- control remains active.

Using the newly durable readiness revision, call the same final handoff and commit.

Expected:

- control becomes inactive;
- generation/cut/ingress remain exact;
- only readiness changed before finalization.

## Required PostgreSQL assertions

For each configured major:

- exact server major verified;
- migrations through 0009 applied/available;
- autocommit is false;
- lock timeout proves concurrent writer exclusion;
- failed B transaction is rolled back before reuse;
- stale handoff CAS fails;
- fresh handoff succeeds;
- post-handoff ingress is inactive-capture and does not advance active frontier;
- cleanup removes only the unique test material.

## No fake concurrency

The integration file may use Python coordination only to manage two real DB connections.

Do not substitute fake connection objects, source inspection, mocked cursor locking, or queue fakes for the required PostgreSQL proof.

Threads are allowed if needed, but a deterministic two-connection lock-timeout sequence is preferred.

## Test gate

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/integration/test_w4r_recovery_concurrency.py -q --basetemp .\.tmp\pytest-w4r-pg-concurrency
```

Existing PostgreSQL integration compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/integration/test_postgres_foundation.py tests/integration/test_operational_persistence.py -q --basetemp .\.tmp\pytest-w4r-pg-compat
```

Full regression exactly once after the integration file is final:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-pg-full
```

The completion report must distinguish passed tests, skipped tests, and which PostgreSQL majors actually executed.

A green pytest result consisting only of skips is NOT gate acceptance.

## Gate disposition

### VERIFIED

Only when at least one of PG17/PG18 actually executed both concurrency scenarios, every configured target passed, cleanup passed, targeted/compatibility/full regression passed, and exact one-file scope passed.

Then STOP for independent W4 final review.

### ENV_BLOCKED / HARNESS_READY

Use when neither TEST_DSN is configured.

Harness may be committed/pushed, but W4 closure remains blocked.

### FAIL

Use when any configured target has wrong major, driver unavailable, migration failure, concurrency expectation failure, stale CAS unexpectedly succeeds, fresh handoff fails, or cleanup fails.

STOP reviewer. Do not patch production in this package.

## Tooling

`CONTROLLED_ROUTE_SET`

Known repository reparse restrictions remain.

Controlled staging is authorized for editing the one test file.

Pytest must run from repository checkout.

## Git

Exactly one test-harness commit:

`test(recovery): verify W4R PostgreSQL concurrency gate`

The commit is expected even if environment is `ENV_BLOCKED / HARNESS_READY`.

Before push:

- origin/master must still equal the gate governance execution baseline;
- exact changed source scope must be the one authorized integration file;
- `git diff --check`;
- no amend/rebase/force push.

Push once, then STOP.

## Completion report

Report initial/final HEAD, origin synchronization, exact changed files/diff, configured/actually executed PostgreSQL majors, targeted/compat/full results, lock-timeout evidence, stale/fresh CAS evidence, cleanup evidence, semantic correction cycles, tooling retries, user-observed 5HR, TEST_DSN migration execution, broker I/O = NO, and final disposition.

## Denied

- production source changes;
- migration source changes;
- production/unknown DB connection;
- arbitrary DSN discovery;
- V07 conformance claim;
- broker/paper/Shioaji I/O;
- W4 closure;
- W4 official credit;
- P7;
- production activation.
