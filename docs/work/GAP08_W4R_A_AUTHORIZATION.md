# GAP-08 W4R-A Authorization

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_A_ONLY`

Planning baseline:

`150053fcf638e347ffe0067a6f4a71d5baa31b9b`

Package freeze:

`docs/work/GAP08_W4R_PACKAGE_FREEZE.md`

Replan:

`docs/work/GAP08_WAVE4_REPLAN_V2.md`

## Goal

Implement only the W4R-A foundation:

1. `AccountRecoveryControl.readiness_revision`;
2. BrokerAccount-scoped `ExecutionContinuityHead`;
3. append-only `ContinuityTransitionReceipt`;
4. controlled current-head transition/re-anchor persistence;
5. migration 0009 DDL for W4R-A objects;
6. C09-owned readiness-relevant writes advance the shared readiness fence when recovery is active.

This package must not make C15 READY.

## Frozen Semantics

- `AccountStateHead` remains economic authority.
- `AccountRecoveryControl.generation` remains recovery generation authority.
- `ingress_version` remains broker-ingress frontier only.
- `readiness_revision` is recovery-currentness/CAS fence only.
- `ExecutionContinuityEpoch` remains immutable continuity evidence.
- `ExecutionContinuityHead` alone selects the current epoch.
- timestamp, epoch lexical order, and historical `trusted_current=True` do not select current.
- stale old epoch loses current-readiness eligibility after head advance.
- historical SequenceGap is append-only and never erased by re-anchor.

## Required Negative Tests First

1. old trusted epoch + newer current untrusted epoch => old epoch cannot become current.
2. `EPOCH-1` must never match/select `EPOCH-10`.
3. conflicting head revision CAS => fail closed.
4. duplicate transition identity with different material => conflict.
5. migration must not backfill/infer a head from existing epoch rows.
6. advancing readiness revision must not change `ingress_version`.
7. duplicate broker inbox evidence must not advance either frontier twice.
8. inactive recovery must not pretend to advance active readiness authority.
9. SequenceGap survives re-anchor/current-head transition.

## Exact Writable Files

Production:

- `persistence/broker_recovery.py`
- `persistence/postgres/broker_recovery.py`
- `persistence/postgres/migrations/0009_trusted_readiness_authority.sql`

Tests:

- `tests/unit/test_c09_broker_recovery_fence.py`
- `tests/unit/test_operational_postgres.py`

No new files other than migration 0009.

## Protected / Read Only

- `persistence/recovery.py`
- `persistence/postgres/recovery.py`
- `persistence/account_authority.py`
- `persistence/postgres/account_authority.py`
- `persistence/broker_action.py`
- `persistence/postgres/broker_action.py`
- `persistence/reconciliation.py`
- `persistence/postgres/reconciliation.py`
- `trading/broker_recovery.py`
- `trading/reconciliation.py`
- `trading/execution.py`
- `adapters/capabilities.py`
- `adapters/sinopac/capabilities.py`
- migrations 0001-0008
- docs
- `data/`

If a protected file is required:

`STOP / REAUTHORIZATION`

## Test Gate

Counterexamples first.

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_operational_postgres.py -q --basetemp .\.tmp\pytest-w4r-a-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c12_recovery_cut.py tests/unit/test_c15_account_recovery_readiness.py -q --basetemp .\.tmp\pytest-w4r-a-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-a-full
```

Post checks:

- `git diff --check`
- exact writable scope
- migrations 0001-0008 unchanged
- no actual PostgreSQL/V07
- no A08
- no broker/paper/Shioaji I/O
- final tree only known `data/` / `.tmp`

## Git

One runtime commit only.

Commit message:

`feat(recovery): add W4R-A continuity authority fence`

Before push:

- `origin/master` must equal the authorization baseline produced by this docs commit.
- no force push / amend / rebase.

Push once then STOP.

## Side Effects

ALLOW:

- bounded source/test changes in exact writable files
- create migration 0009 source
- local unit/regression tests
- one commit/push

DENY:

- migration execution
- actual PostgreSQL/V07
- A08
- broker/paper/Shioaji I/O
- credentials
- production activation
- P7
- W4R-B/C/D
- W4 closure/credit

## Completion

Runtime candidate remains reviewer-unaccepted after execution.

CODEX must report:

- initial baseline
- final HEAD
- changed files
- negative-test evidence
- targeted / compatibility / full regression
- tooling retries
- semantic corrections
- scope/protected/migration guards
- actual PostgreSQL/V07 = NO
- A08 = NOT_RUN
- broker I/O = NO
- push result
- observed 5HR consumption if available
- STOP
