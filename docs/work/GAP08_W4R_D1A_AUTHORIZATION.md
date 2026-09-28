# GAP-08 W4R-D1A Authorization

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_D1A_ONLY`

Planning baseline:

`2eebf518cc88401466752e8c4e36a79e8dd47a38`

Dependencies:

- W4R-A ACCEPTED / FROZEN
- W4R-B ACCEPTED / FROZEN
- W4R-C ACCEPTED / FROZEN

Execution plan:

`docs/work/GAP08_W4R_D_EXECUTION_PLAN.md`

## Goal

Implement only D1A:

1. reusable transaction-local shared recovery-readiness fence primitive;
2. AccountAuthorityCommit participation;
3. broker position observation participation.

No D1B/D2/D3 work.

## D1A-1 Neutral fence contract

Add:

- `persistence/readiness_fence.py`
- `persistence/postgres/readiness_fence.py`

The domain contract must be broker-neutral and contain no C15 READY semantics.

A lock token must positively bind at least:

- BrokerAccount;
- recovery generation;
- recovery_cut_revision;
- captured readiness_revision.

The token is a transaction-local currentness witness, not economic authority.

Required repository operations:

### lock active fence

Exact BrokerAccount:

- `SELECT ... account_recovery_controls ... FOR UPDATE`;
- missing control => return no active token;
- inactive control => return no active token;
- active control => return exact token;
- no mutation yet.

### advance locked fence

Given the exact token:

- advance `readiness_revision` by exactly one;
- exact CAS on BrokerAccount / generation / recovery_cut_revision / captured readiness_revision / active=TRUE;
- mismatch => fail closed;
- return/verify the exact new revision;
- never alter `ingress_version`;
- never commit.

## D1A-2 AccountAuthorityCommit integration

Do not change public business semantics of AccountAuthorityCommit.

Extend its repository contract only as needed to delegate the neutral fence.

For a **new material commit**:

1. existing stable receipt lookup/conflict handling remains first;
2. after confirming this is not an exact duplicate, lock the active recovery readiness fence **before AccountStateHead lock and before participants**;
3. execute existing authority transaction unchanged;
4. after all material writes + authority closure validation succeed, advance the locked fence exactly once;
5. then commit.

Required behavior:

- exact historical duplicate receipt => no fence advancement;
- same commit identity / conflicting material => no fence advancement;
- participant failure => UoW rollback; no committed readiness advancement;
- checkpoint/head/receipt failure => rollback;
- successful new material commit under active recovery => exactly one readiness increment;
- no active recovery => ordinary authority commit continues with no readiness increment.

### BrokerAction coverage

Do not modify BrokerAction repository/service in D1A.

BrokerAction attempt/resolution head mutations are already AccountAuthorityCommit participants.

The single outer AccountAuthorityCommit fence covers:

- Order/Fill/Event/snapshot participants;
- BrokerAction reserve/resolve participants.

D1A must not introduce a second BrokerAction-specific readiness increment.

## D1A-3 Broker observation append

`PostgresBrokerPositionObservationRepository.append(...)`:

1. lock active readiness fence before the observation INSERT;
2. append canonical observation and all item rows;
3. advance exactly once after successful material writes if an active token exists;
4. no internal commit.

If observation/item persistence fails, caller transaction rollback must also discard the readiness advancement.

No active control => append remains permitted without readiness increment.

## Required counterexamples first

1. active fence token locks exact BrokerAccount row;
2. inactive/missing control returns no token and performs no readiness UPDATE;
3. fence CAS conflict fails closed;
4. fence advance changes readiness only, never ingress_version;
5. fence repository never commits;
6. new AccountAuthorityCommit locks readiness before AccountStateHead;
7. successful new AccountAuthorityCommit advances exactly once;
8. exact duplicate AccountAuthorityCommit does not advance;
9. conflicting stable receipt does not advance;
10. material participant failure does not reach advance/commit;
11. BrokerAction participant remains inside the one outer authority fence;
12. broker observation locks fence before first observation INSERT;
13. successful observation under active recovery advances once;
14. inactive/missing recovery control observation does not advance;
15. observation persistence failure cannot commit a readiness bump;
16. no READY/finalize/handoff API appears.

## Exact writable files

New:

- `persistence/readiness_fence.py`
- `persistence/postgres/readiness_fence.py`

Existing production:

- `persistence/account_authority.py`
- `persistence/postgres/account_authority.py`
- `persistence/postgres/account.py`

Tests:

- `tests/unit/test_c04_account_authority_commit.py`
- `tests/unit/test_operational_postgres.py`

Exactly these seven files.

## Protected / read only

Including:

- `persistence/broker_action.py`
- `persistence/postgres/broker_action.py`
- `persistence/reconciliation.py`
- `persistence/postgres/reconciliation.py`
- `persistence/recovery.py`
- `persistence/postgres/recovery.py`
- `persistence/broker_recovery.py`
- `persistence/postgres/broker_recovery.py`
- all migrations
- W4R-A/B/C frozen files outside authorized scope
- docs
- broker network code
- `data/`

Need protected scope => STOP / REAUTHORIZATION.

## Test gate

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c04_account_authority_commit.py tests/unit/test_operational_postgres.py -q --basetemp .\.tmp\pytest-w4r-d1a-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c06_broker_action_safety.py tests/unit/test_operational_execution.py tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_c15_account_recovery_readiness.py -q --basetemp .\.tmp\pytest-w4r-d1a-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-d1a-full
```

If production code changes after full regression, rerun final full regression and report transparently.

## Tooling mode

`CONTROLLED_STAGING_ROOT_FIRST`

Use repository-local/direct test and Git/index routes already proven reliable.

Do not retry known external staging pytest common-root or Git-index sandbox failures.

## Efficiency report

Report:

- changed files;
- additions/deletions;
- semantic correction cycles;
- tooling retries;
- 5HR consumption.

Pytest count is verification, not workload.

## Git

Exactly one runtime commit:

`feat(recovery): fence W4R-D1A account authority writers`

Before push:

- origin/master must still equal D1A execution baseline;
- no amend/rebase/force push.

Push once, then STOP reviewer.

## Side effects

ALLOW:

- exact seven-file source/test work;
- local tests;
- one commit/push.

DENY:

- D1B/D2/D3;
- C15 READY;
- final handoff changes;
- migrations;
- actual PostgreSQL/V07;
- A08;
- broker/paper/Shioaji I/O;
- production;
- P7;
- W4 closure/credit.
