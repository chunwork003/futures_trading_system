# GAP-08 W4R-C2B Authorization Amendment 01

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_C2B_RF01_ONLY`

Correction base:

`515bbcca04b7afa69737b713f71f8267bc182ffb`

Parent authorization:

`docs/work/GAP08_W4R_C2B_AUTHORIZATION.md`

Independent review:

`docs/work/GAP08_W4R_C2B_REVIEW_RF01.md`

## Goal

Seal only C2B canonical Event identity/linkage.

No W4R-D implementation is authorized.

## Exact writable files

Production:

- `persistence/recovery.py`

Tests:

- `tests/unit/test_c15_account_recovery_readiness.py`

Exactly these two files.

No new files.

## RF01-1 Event idempotency identity

For the exact root Event sequence:

- canonical identity is `(idempotency_scope, idempotency_key)`;
- require identities unique across the sequence;
- duplicate identity => `RecoveryClosureIntegrityError`.

Existing exact scope requirement remains:

`idempotency_scope == ORDER_EVENT:<order_id>`

Do not weaken it.

## RF01-2 Event causation linkage

Restore the already-frozen execution persistence invariant during recovery validation:

- sequence 0:
  `event.causation_id == Order.intent_id`;
- sequence >0:
  `event.causation_id == previous_event.event_id`.

Mismatch => `RecoveryClosureIntegrityError`.

Do not alter lifecycle transition semantics.

## RF01-3 Preserve accepted C2B closure

Do not change:

- root membership;
- Order exact read;
- bounded Event read;
- Fill set membership;
- Fill provenance checks;
- economic closure;
- fingerprint composition;
- ambiguous report carry-forward.

## Required counterexamples first

1. duplicate Event idempotency identity fails closed;
2. sequence-0 wrong causation fails closed;
3. later Event wrong causation fails closed;
4. exact valid closure remains deterministic;
5. output still has no READY/finalize/handoff authority.

## Test gate

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c15_account_recovery_readiness.py -q --basetemp .\.tmp\pytest-w4r-c2b-rf01-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_operational_execution.py tests/unit/test_event_ledger.py tests/unit/test_c10_broker_reconstruction.py tests/unit/test_c12_recovery_cut.py tests/unit/test_c13_reconciliation_case_scope.py -q --basetemp .\.tmp\pytest-w4r-c2b-rf01-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-c2b-rf01-full
```

If production changes after the full regression, rerun final full regression and report transparently.

## Tooling mode

`CONTROLLED_STAGING_ROOT_FIRST`

Known failures are already classified:

- external staging pytest common-root permission;
- Git index sandbox permission.

Use the known-working direct import/test route and repository-local Git/index route immediately.

Do not retry the known-failing paths.

## Efficiency report

Report:

- changed files;
- additions/deletions;
- semantic correction cycles;
- tooling retries;
- 5HR consumption.

Pytest count is verification, not workload.

## Git

Exactly one correction commit:

`fix(recovery): seal W4R-C2B event identity linkage`

Before push:

- origin/master must equal RF01 execution baseline;
- no amend/rebase/force push.

Push once then STOP reviewer.

## Protected / denied

Everything except the exact two writable files is read-only.

Denied:

- W4R-D;
- C15 READY;
- final handoff;
- migrations;
- actual PostgreSQL/V07;
- A08;
- broker/paper/Shioaji I/O;
- production;
- P7;
- W4 closure/credit.
