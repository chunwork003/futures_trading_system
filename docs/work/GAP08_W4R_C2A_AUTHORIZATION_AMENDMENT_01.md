# GAP-08 W4R-C2A Authorization Amendment 01

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_C2A_RF01_ONLY`

Correction base:

`cdd979d6fe46b161b9376f6c58c14ed1aa90e749`

Parent authorization:

`docs/work/GAP08_W4R_C2A_AUTHORIZATION.md`

Independent review:

`docs/work/GAP08_W4R_C2A_REVIEW_RF01.md`

## Goal

Seal C2A exact-read identity closure only.

No C2B or W4R-D implementation is authorized.

## Exact writable files

Production:

- `persistence/recovery.py`

Tests:

- `tests/unit/test_c15_account_recovery_readiness.py`

Exactly these two files. No new files.

## Required corrections

1. After `OrderRepository.get(head.order_id)`, require result exists and `order.order_id == head.order_id`.
2. After expected snapshot re-read, require exact snapshot ID and exact BrokerAccount.
3. After source-event read, require exact event ID and `entity_type == "ORDER"`.
4. Preserve all accepted C2A root-source, report ambiguity, reconstruction binding and fingerprint semantics.

## Required counterexamples first

1. mismatched embedded Order ID fails closed;
2. mismatched expected snapshot ID fails closed;
3. mismatched expected snapshot BrokerAccount fails closed;
4. mismatched source event ID fails closed;
5. matching identities keep deterministic output unchanged;
6. output still exposes no READY/finalize/handoff authority.

## Test gate

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c15_account_recovery_readiness.py -q --basetemp .\.tmp\pytest-w4r-c2a-rf01-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c06_broker_action_safety.py tests/unit/test_c10_broker_reconstruction.py tests/unit/test_c12_recovery_cut.py tests/unit/test_c13_reconciliation_case_scope.py -q --basetemp .\.tmp\pytest-w4r-c2a-rf01-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-c2a-rf01-full
```

If production code changes after the full regression, rerun the final full regression and report it transparently.

## Tooling mode

`CONTROLLED_STAGING_ROOT_FIRST`

Use the known-working controlled staging path before first edit. Do not try the known-failing workspace patch route.

## Efficiency report

Report changed files, approximate additions/deletions, semantic correction cycles, tooling retries and 5HR consumption. Pytest count is verification, not workload.

## Git

Exactly one correction commit:

`fix(recovery): seal W4R-C2A exact root reads`

Push once after origin divergence guard, then STOP reviewer.

## Protected / denied

Everything outside the exact two writable files is read-only.

Denied:

- W4R-C2B/D;
- global Order/history scan;
- migration changes/execution;
- actual PostgreSQL/V07;
- A08;
- broker/paper/Shioaji I/O;
- production;
- P7;
- W4 closure/credit.
