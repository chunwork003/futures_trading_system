# GAP-08 W4R-D1A Authorization Amendment 02 — RF01 Resume

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_D1A_RF01_RESUME_ONLY`

Resume base:

`a9f8f6763f0619a9440a4f1e0a48a0f703412b35`

Parent authorization:

`docs/work/GAP08_W4R_D1A_AUTHORIZATION_AMENDMENT_01.md`

Blocker note:

`docs/work/GAP08_W4R_D1A_RF01_BLOCKER_01.md`

## Goal

Resume the already-started D1A RF01 correction without weakening the mandatory readiness-fence contract.

The only scope expansion is the C06 compatibility fake.

No D1B/D2/D3 work is authorized.

## Preserve and reuse the blocked patch

The materialization script saves the already completed unstaged RF01 delta to:

`.tmp/GAP08_W4R_D1A_RF01_BLOCKED.patch`

At resumed execution:

1. inspect that patch first;
2. reapply/reuse it if present;
3. do not rediscover or rewrite equivalent production logic from scratch;
4. if the patch cannot apply cleanly, STOP and report rather than broadening scope.

The patch is expected to contain only:

- `persistence/account_authority.py`
- `tests/unit/test_c04_account_authority_commit.py`

## Exact writable files

Production:

- `persistence/account_authority.py`

Tests:

- `tests/unit/test_c04_account_authority_commit.py`
- `tests/unit/test_c06_broker_action_safety.py`

Exactly these three files.

No new runtime/test files.

## Required production semantics — unchanged from RF01

For every new material AccountAuthorityCommit:

- call `repository.lock_active_readiness_fence(BrokerAccount(...))` directly;
- no `getattr`, `hasattr`, optional callback detection or fallback;
- missing required operation fails before AccountStateHead lock and before material participants;
- explicit return `None` means the repository positively reports no active recovery;
- active token advances exactly once after authority closure validation;
- exact duplicate/conflicting stable receipt remains before fence lock;
- readiness advance failure prevents commit and the UoW rolls back.

Do not restore fail-open compatibility behavior.

## Compatibility fake amendment

In `tests/unit/test_c06_broker_action_safety.py`, update only the existing `AuthorityRepo` fake to satisfy the mandatory AccountAuthority fence protocol used by the test scenario.

Required behavior:

```text
lock_active_readiness_fence(account) -> None
advance_locked_readiness_fence(token) -> must never be called
```

Recommended fail-fast behavior for the second method:

raise `AssertionError` if invoked.

The fake must not:

- create a synthetic active recovery token;
- advance a readiness revision;
- import/use PostgreSQL;
- alter BrokerAction business semantics.

## Required evidence

Counterexample/targeted evidence retained from blocked execution:

- legacy repository without fence operation fails closed;
- explicit no-active-fence repository can commit;
- active fence ordering remains correct;
- advance failure rolls back;
- duplicate/conflict bypass fence.

Resume compatibility evidence must additionally prove:

- existing C06 BrokerAction tests pass with the explicit no-active-recovery fake contract;
- no optional fallback is reintroduced into production.

## Test gates

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c04_account_authority_commit.py -q --basetemp .\.tmp\pytest-w4r-d1a-rf01-resume-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c06_broker_action_safety.py tests/unit/test_operational_execution.py tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_operational_postgres.py -q --basetemp .\.tmp\pytest-w4r-d1a-rf01-resume-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-d1a-rf01-resume-full
```

If production changes after the full regression, rerun final full regression and report transparently.

## Tooling mode

`CONTROLLED_STAGING_ROOT_FIRST`

Known failing routes remain prohibited.

The saved blocked patch is the preferred resume source.

## Git

Exactly one runtime correction commit:

`fix(recovery): require W4R-D1A readiness fence contract`

Before push:

- origin/master must still equal the resumed execution baseline produced by the docs materialization;
- no amend/rebase/force push.

Push once then STOP reviewer.

## Completion report

Report:

- resumed initial HEAD;
- saved patch reused = YES/NO;
- final HEAD/origin;
- exact 3-file or smaller changed scope;
- targeted/compat/full results;
- semantic correction cycles after resume;
- tooling retries after resume;
- 5HR consumption;
- no migration/PostgreSQL/broker I/O;
- STOP.

## Protected / denied

Everything outside the exact three writable files is read-only.

Denied:

- D1B/D2/D3;
- C15 READY;
- final handoff;
- migration changes/execution;
- actual PostgreSQL/V07;
- A08;
- broker/paper/Shioaji I/O;
- production;
- P7;
- W4 closure/credit.
