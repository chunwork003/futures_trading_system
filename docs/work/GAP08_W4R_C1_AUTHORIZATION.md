# GAP-08 W4R-C1 Authorization

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_C1_ONLY`

Planning baseline:

`1f5db799360691744a741c461e13eaebedded046`

Dependencies:

- W4R-A ACCEPTED / FROZEN
- W4R-B ACCEPTED / FROZEN

Execution plan:

`docs/work/GAP08_W4R_C_EXECUTION_PLAN.md`

## Goal

Implement only W4R-C1:

- directly reuse C13 `unresolved(account)`;
- directly reuse C13 `blocking_case_state(...)`;
- derive deterministic semantic blocker witness/fingerprint;
- expose resolver-produced C13 trusted evidence for later W4R-D.

No duplicate reconciliation-case SQL.
No C2 recovery closure.
No C15 READY or handoff.

## Frozen semantic owner

C13 remains the owner of:

- account-scoped unresolved-case selection;
- legacy NULL-scope fail-closed behavior;
- HALT > REVIEW_REQUIRED > nonblocking precedence.

C1 must call the repository and `blocking_case_state`; it may not reimplement those semantics.

## Suggested trusted evidence

A resolver-produced immutable model may contain:

- BrokerAccount;
- `blocking_state: ReconciliationCaseState | None`;
- unresolved case IDs in deterministic order;
- semantic blocker fingerprint.

It is not a READY decision.

## Semantic fingerprint contract

For each unresolved case, include canonical readiness-relevant material:

- `case_id`;
- exact `account`;
- canonical `result`;
- `policy`;
- `state`.

Do not include version/audit wrapper material:

- `ReconciliationCaseVersion.version`;
- `recorded_at`;
- `actor_ref`;
- wrapper `evidence`.

Sort by exact case ID before fingerprinting.

Changing only audit metadata => same semantic fingerprint.

Changing case semantic material => different fingerprint.

## Required counterexamples first

1. HALT unresolved case => blocking state HALT;
2. REVIEW_REQUIRED only => REVIEW_REQUIRED;
3. HALT + REVIEW_REQUIRED => HALT;
4. all RESOLVED / no unresolved => no blocker;
5. other-account case is absent from requested account evidence;
6. legacy NULL scope error propagates/fails closed;
7. changing version number only => fingerprint unchanged;
8. changing recorded_at only => fingerprint unchanged;
9. changing actor_ref/version evidence only => fingerprint unchanged;
10. changing result status/material => fingerprint changes;
11. changing policy => fingerprint changes;
12. changing blocking state => fingerprint changes;
13. caller cannot supply arbitrary blocking bool/fingerprint to bypass repository resolution.

## Exact writable files

Production:

- `persistence/reconciliation.py`
- `persistence/recovery.py`

Tests:

- `tests/unit/test_c13_reconciliation_case_scope.py`
- `tests/unit/test_c15_account_recovery_readiness.py`

Exactly these four files.

No new files.

## Protected / read only

- `persistence/postgres/reconciliation.py`
- `persistence/broker_recovery.py`
- `persistence/postgres/broker_recovery.py`
- `persistence/execution.py`
- `persistence/postgres/execution.py`
- `persistence/broker_action.py`
- `persistence/postgres/broker_action.py`
- `persistence/postgres/recovery.py`
- all migrations
- W4R-A/B frozen files outside exact scope
- broker network code
- docs
- `data/`

Need outside scope => `STOP / REAUTHORIZATION`.

## Test gates

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c13_reconciliation_case_scope.py tests/unit/test_c15_account_recovery_readiness.py -q --basetemp .\.tmp\pytest-w4r-c1-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c14_reconciliation_run.py tests/unit/test_operational_postgres.py -q --basetemp .\.tmp\pytest-w4r-c1-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-c1-full
```

## Tooling mode

`CONTROLLED_STAGING_ROOT_FIRST`

Do not attempt the known-failing workspace patch route first.

Use one controlled staging root for exactly four writable files, then one sync-back + hash/diff/scope guard.

## Efficiency report

Report:

- actual changed files;
- approximate diff size;
- semantic correction cycles;
- tooling retries;
- 5HR consumption.

Pytest pass count is verification, not workload.

## Git

Exactly one runtime commit:

`feat(recovery): bind W4R-C1 reconciliation blocker authority`

Push once after remote ancestry guard.

Then STOP reviewer.

## Denied

- W4R-C2/D
- duplicate C13 SQL
- C13 semantic changes
- migrations
- actual PostgreSQL/V07
- A08
- broker/paper/Shioaji I/O
- production
- P7
- W4 closure/credit
- files outside exact writable set
