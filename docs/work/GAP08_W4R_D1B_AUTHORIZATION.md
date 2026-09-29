# GAP-08 W4R-D1B Authorization

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_D1B_ONLY`

Execution baseline:

`af794f5895c41925cfe007da7e1f522fcd189920`

Dependencies:

- W4R-A ACCEPTED / FROZEN
- W4R-B ACCEPTED / FROZEN
- W4R-C ACCEPTED / FROZEN
- W4R-D1A ACCEPTED / FROZEN

Parent plan:

`docs/work/GAP08_W4R_D_EXECUTION_PLAN.md`

## Goal

Wire the remaining C13/C14 reconciliation writers into the accepted D1A neutral readiness fence.

D1B does not build the TrustedReadinessEvidenceBundle and does not perform C15/final handoff.

## Shared primitive

Reuse only:

- `RecoveryReadinessFenceToken`
- `PostgresRecoveryReadinessFenceRepository`

Do not duplicate `account_recovery_controls` fence SQL.

Do not alter the D1A primitive.

No repository may commit or rollback.

## D1B-1 C13 reconciliation-case history

Owner:

`PostgresReconciliationCaseRepository.append(...)`

The repository must lock the active BrokerAccount readiness fence before any case-history material write.

### Currentness semantics

Readiness is based on C13 unresolved/blocking semantics, not audit wrapper metadata.

Reuse the existing C13 semantic owner:

`reconciliation_blocker_semantic_fingerprint(...)`

Do not create a second blocker algorithm.

For the exact case being appended, classify its readiness contribution as:

- `None` when the latest version is absent or `RESOLVED`;
- the existing C13 semantic fingerprint for a non-resolved version.

Compare prior contribution vs new contribution.

Advance `readiness_revision` exactly once only when those contributions differ.

Examples:

- new HALT / REVIEW_REQUIRED case -> advance;
- HALT <-> REVIEW_REQUIRED material transition -> advance;
- result/policy/state material change -> advance;
- unresolved -> RESOLVED -> advance;
- audit-only version/recorded_at/actor/evidence change with identical underlying C13 blocker material -> no advance.

The existing case scope-drift fail-closed behavior remains unchanged.

No C13 blocking semantics change is authorized.

### Ordering

For append:

1. lock active readiness fence using `version.reconciliation_case.account`;
2. read/lock latest exact case row;
3. validate account scope;
4. derive prior C13 readiness contribution;
5. insert the new append-only version;
6. derive new contribution from the supplied version;
7. advance once only if contribution changed and active token exists;
8. caller controls commit.

Insert/scope failure must not produce a committed readiness advance.

## D1B-2 C14 formal-run boundary establish

Owner:

`PostgresReconciliationRunRepository.establish(...)`

For a new boundary:

1. lock active readiness fence using `boundary.account`;
2. attempt the existing append-only boundary insert;
3. if newly inserted, advance exactly once when active;
4. if exact duplicate, do not advance;
5. if conflicting duplicate, fail closed and do not advance.

The existing C14 boundary identity/equality semantics remain unchanged.

## D1B-3 C14 terminal finalize

Owner:

`PostgresReconciliationRunRepository.finalize(...)`

`ReconciliationRunOutcome` does not contain BrokerAccount, so the repository must resolve account scope without reversing the shared lock order.

Required order:

1. read the exact boundary without material mutation to obtain its canonical BrokerAccount;
2. if missing/invalid, fail closed;
3. lock active readiness fence for that account;
4. lock/re-read the exact boundary row `FOR UPDATE`;
5. revalidate that the locked boundary is exactly the same canonical boundary/account resolved before the fence lock;
6. attempt the existing terminal-outcome insert;
7. newly inserted outcome -> advance exactly once when active;
8. exact duplicate outcome -> no advance;
9. conflicting duplicate -> fail closed / no advance;
10. caller controls commit.

This preserves the global writer order:

`recovery-control fence -> readiness-relevant row lock/write`

while allowing account resolution from the C14 boundary.

## Required counterexamples first

C13:

1. active C13 append locks recovery fence before reconciliation case material write;
2. new unresolved blocker advances exactly once;
3. unresolved -> RESOLVED advances exactly once;
4. blocker result/policy/state material change advances;
5. audit-wrapper-only version does not advance;
6. missing/inactive recovery control performs no readiness UPDATE;
7. account scope conflict fails before case INSERT/advance;
8. repository never commits.

C14 establish:

9. new boundary locks fence before INSERT and advances once;
10. exact duplicate boundary does not advance;
11. conflicting duplicate boundary fails closed and does not advance;
12. inactive/missing control does not advance.

C14 finalize:

13. account is resolved from exact boundary before fence lock without material write;
14. fence lock occurs before locked boundary revalidation and outcome INSERT;
15. boundary missing fails closed;
16. boundary changes between pre-read and locked re-read fail closed;
17. new terminal outcome advances once;
18. exact duplicate outcome does not advance;
19. conflicting duplicate outcome fails closed/no advance;
20. repository never commits.

Global:

21. `ingress_version` is never changed;
22. no C13 blocking algorithm is duplicated;
23. no C14 formal-run semantics are changed;
24. no C15 READY / C09 final handoff / D2 trusted bundle surface appears.

## Exact writable files

Production:

- `persistence/postgres/reconciliation.py`

Tests:

- `tests/unit/test_c13_reconciliation_case_scope.py`
- `tests/unit/test_c14_reconciliation_run.py`
- `tests/unit/test_operational_postgres.py`

Exactly these four files.

No new files.

## Protected / read only

Including:

- `persistence/reconciliation.py`
- `persistence/readiness_fence.py`
- `persistence/postgres/readiness_fence.py`
- `persistence/account_authority.py`
- `persistence/postgres/account_authority.py`
- `persistence/postgres/account.py`
- `persistence/recovery.py`
- `persistence/postgres/recovery.py`
- `persistence/broker_recovery.py`
- `persistence/postgres/broker_recovery.py`
- all migrations
- all W4R-A/B/C/D1A frozen source
- docs
- broker network code
- `data/`

Need protected scope => STOP / REAUTHORIZATION.

## Test gate

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c13_reconciliation_case_scope.py tests/unit/test_c14_reconciliation_run.py -q --basetemp .\.tmp\pytest-w4r-d1b-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_operational_postgres.py tests/unit/test_c15_account_recovery_readiness.py -q --basetemp .\.tmp\pytest-w4r-d1b-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-d1b-full
```

If production code changes after the full regression, rerun the final full regression and report it transparently.

## Tooling mode

`CONTROLLED_STAGING_ROOT_FIRST`

Use the repository-local/direct routes already proven reliable.

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

Exactly one runtime commit:

`feat(recovery): fence W4R-D1B reconciliation writers`

Before push:

- origin/master must still equal the D1B execution baseline produced by governance materialization;
- no amend/rebase/force push.

Push once then STOP reviewer.

## Side effects

ALLOW:

- exact four-file source/test work;
- local tests;
- one commit/push.

DENY:

- D2/D3;
- C15 READY;
- C09 final handoff changes;
- migrations;
- actual PostgreSQL/V07;
- A08;
- broker/paper/Shioaji I/O;
- production;
- P7;
- W4 closure/credit.
