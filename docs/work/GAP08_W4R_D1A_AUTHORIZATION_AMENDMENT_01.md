# GAP-08 W4R-D1A Authorization Amendment 01

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_D1A_RF01_ONLY`

Correction base:

`34960db79b9d2732d23af260dfeb1131c368d9e1`

Parent authorization:

`docs/work/GAP08_W4R_D1A_AUTHORIZATION.md`

Independent review:

`docs/work/GAP08_W4R_D1A_REVIEW_RF01.md`

## Goal

Make AccountAuthority readiness-fence participation mandatory/fail-closed.

No D1B/D2/D3 work is authorized.

## Exact writable files

Production:

- `persistence/account_authority.py`

Tests:

- `tests/unit/test_c04_account_authority_commit.py`

Exactly these two files.

No new files.

## RF01-1 Mandatory fence protocol

For every new material AccountAuthorityCommit:

- call `repository.lock_active_readiness_fence(BrokerAccount(...))` directly;
- do not use `getattr`, `hasattr`, optional callback detection or fallback;
- absence of the required repository method must fail before:
  - AccountStateHead lock/bootstrap;
  - participant factory material application;
  - participant writes;
  - checkpoint/head/receipt writes.

A returned `None` is allowed and means the repository positively reports no active recovery fence.

## RF01-2 Preserve duplicate ordering

Existing stable receipt resolution remains first.

Therefore:

- exact duplicate receipt => no fence lock/advance;
- conflicting receipt => no fence lock/advance.

Do not change historical duplicate semantics.

## RF01-3 Advance failure rolls back

Add explicit test evidence:

- active fence locks successfully;
- authority material writes occur;
- `advance_locked_readiness_fence` fails;
- UoW does not commit;
- context exit rolls back.

Do not add manual rollback calls to repositories.

## Required counterexamples first

1. legacy/missing-fence repository fails before head/material writes;
2. implemented fence returning `None` permits non-recovery commit;
3. active fence still orders `lock_fence -> lock_head -> material -> authority -> advance`;
4. advance failure rolls back/no commit;
5. duplicate/conflict still bypass fence completely.

## Test gate

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c04_account_authority_commit.py -q --basetemp .\.tmp\pytest-w4r-d1a-rf01-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c06_broker_action_safety.py tests/unit/test_operational_execution.py tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_operational_postgres.py -q --basetemp .\.tmp\pytest-w4r-d1a-rf01-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-d1a-rf01-full
```

If production changes after the full regression, rerun final full regression and report transparently.

## Tooling mode

`CONTROLLED_STAGING_ROOT_FIRST`

Use the already-proven direct/repository-local routes immediately.

Do not retry known external staging pytest/common-root or Git-index sandbox failures.

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

`fix(recovery): require W4R-D1A readiness fence contract`

Before push:

- origin/master must equal the RF01 execution baseline;
- no amend/rebase/force push.

Push once then STOP reviewer.

## Protected / denied

Everything outside the exact two writable files is read-only.

Denied:

- D1B/D2/D3;
- C15 READY;
- final handoff;
- migrations;
- actual PostgreSQL/V07;
- A08;
- broker/paper/Shioaji I/O;
- production;
- P7;
- W4 closure/credit.
