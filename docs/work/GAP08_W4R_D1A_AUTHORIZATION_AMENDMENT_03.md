# GAP-08 W4R-D1A Authorization Amendment 03 — RF01 Resume 2

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_D1A_RF01_RESUME2_ONLY`

Resume base:

`0c2ae2fffb6de09662aba22cd9f8ee2db25b3eff`

Parent authorization:

`docs/work/GAP08_W4R_D1A_AUTHORIZATION_AMENDMENT_02.md`

Blocker note:

`docs/work/GAP08_W4R_D1A_RF01_BLOCKER_02.md`

## Goal

Resume the already-started D1A RF01 correction after full regression identified the remaining C03/C05 compatibility fakes.

Do not change the mandatory production fence semantics.

No D1B/D2/D3 work is authorized.

## Preserve and reuse current WIP

The materialization script saves the current three-file unstaged WIP to:

`.tmp/GAP08_W4R_D1A_RF01_RESUME_BLOCKED.patch`

Expected patch contents:

- `persistence/account_authority.py`
- `tests/unit/test_c04_account_authority_commit.py`
- `tests/unit/test_c06_broker_action_safety.py`

At resumed execution:

1. inspect the saved patch first;
2. apply/reuse it before editing;
3. do not rediscover/rewrite equivalent production logic;
4. if it does not apply cleanly, STOP.

## Exact writable files

Production:

- `persistence/account_authority.py`

Tests:

- `tests/unit/test_c04_account_authority_commit.py`
- `tests/unit/test_c06_broker_action_safety.py`
- `tests/unit/test_c03_expected_state_initialization.py`
- `tests/unit/test_c05_durable_pending_submission.py`

Exactly these five files.

No new runtime/test files.

## Production semantics — unchanged

For every new material `AccountAuthorityCommit`:

- directly invoke `repository.lock_active_readiness_fence(BrokerAccount(...))`;
- no `getattr`, `hasattr`, feature detection or optional fallback;
- a missing required method must fail before head lock and material writes;
- explicit `None` means the repository positively reports no active recovery;
- active token advances exactly once after authority closure validation;
- exact duplicate/conflicting stable receipt remains before fence lock;
- readiness advance failure prevents commit and rolls back the UoW.

No production semantic change beyond the already completed RF01 delta is expected in Resume 2.

## C03 compatibility fake

In `tests/unit/test_c03_expected_state_initialization.py`, update only the existing `AuthorityRepo` fake:

```text
lock_active_readiness_fence(account) -> None
advance_locked_readiness_fence(token) -> AssertionError if invoked
```

Do not change expected-state initialization semantics.

## C05 compatibility fake

In `tests/unit/test_c05_durable_pending_submission.py`, update only the existing `AuthorityRepo` fake:

```text
lock_active_readiness_fence(account) -> None
advance_locked_readiness_fence(token) -> AssertionError if invoked
```

Do not change durable-pending submission semantics.

## Existing C06 fake

Retain the already completed C06 compatibility fake amendment with the same explicit no-active-recovery contract.

## Required verification

### Focused contract gate

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c03_expected_state_initialization.py tests/unit/test_c04_account_authority_commit.py tests/unit/test_c05_durable_pending_submission.py tests/unit/test_c06_broker_action_safety.py -q --basetemp .\.tmp\pytest-w4r-d1a-rf01-resume2-focused
```

### Compatibility

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_operational_execution.py tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_operational_postgres.py -q --basetemp .\.tmp\pytest-w4r-d1a-rf01-resume2-compat
```

### Full regression

Exactly once after focused + compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-d1a-rf01-resume2-full
```

If production code changes after the full regression, rerun the final full regression and report it transparently.

## Full-regression interpretation

The previous complete run produced exactly:

`1334 passed / 4 skipped / 9 failed`

and all 9 failures were attributed to the C03/C05 old test-double contract.

Therefore Resume 2 should not broaden scope if a different failure appears.

Any new failure outside these five files:

`STOP / REAUTHORIZATION`

## Tooling mode

`CONTROLLED_STAGING_ROOT_FIRST`

Reuse the saved patch.

Known failing external staging/common-root and Git-index sandbox paths remain prohibited.

A tooling retry does not consume semantic correction budget.

## Git

Exactly one runtime correction commit:

`fix(recovery): require W4R-D1A readiness fence contract`

Before push:

- origin/master must still equal the Resume 2 execution baseline;
- no amend/rebase/force push.

Push once then STOP reviewer.

## Completion report

Report:

- initial HEAD;
- saved Resume-2 patch reused = YES/NO;
- final HEAD/origin;
- exact changed files;
- focused/compat/full results;
- semantic correction cycles;
- tooling retries;
- 5HR consumption;
- migration/PostgreSQL/broker I/O = NO;
- STOP.

## Protected / denied

Everything outside the exact five writable files is read-only.

Denied:

- D1B/D2/D3;
- C15 READY/final handoff;
- migration changes/execution;
- actual PostgreSQL/V07;
- A08;
- broker/paper/Shioaji I/O;
- production;
- P7;
- W4 closure/credit.
