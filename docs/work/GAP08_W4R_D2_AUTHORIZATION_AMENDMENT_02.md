# GAP-08 W4R-D2 Authorization Amendment 02 — RF01

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_D2_RF01_ONLY`

RF01 baseline:

`26c1d7028c1c3451e46da3fe1f346d966feb42b5`

Parent authorization:

- `docs/work/GAP08_W4R_D2_AUTHORIZATION.md`
- `docs/work/GAP08_W4R_D2_AUTHORIZATION_AMENDMENT_01.md`

Independent review:

`docs/work/GAP08_W4R_D2_REVIEW_RF01.md`

## Goal

Correct exactly two D2 authority seams:

1. make the accepted D2 resolver transaction-composable for later D3 same-UoW use;
2. bind canonical durable gap material to the continuity transition receipt `gap_set_fingerprint`.

Retain the existing D2 runtime candidate otherwise.

No D3 behavior is authorized.

## Exact writable files

Production:

- `persistence/recovery.py`
- `persistence/postgres/recovery.py`

Tests:

- `tests/unit/test_c15_account_recovery_readiness.py`
- `tests/unit/test_operational_postgres.py`

Exactly these four files remain authorized.

A legitimate smaller subset is allowed.

No new files.

## RF01-A — transaction-composable recovery-cut read

In `persistence/postgres/recovery.py`:

### Preserve standalone loader contract

`PostgresExecutionStateLoader.load(account)` must continue to establish:

`REPEATABLE READ READ ONLY`

for its standalone coherent-cut use.

It must still return exactly the existing:

- `VALID`;
- `BASELINE_NOT_ESTABLISHED`;
- `RESTORE_FAILURE`

semantics.

### Extract current-transaction helper

Factor the read/validation body into one private helper that:

- consumes the existing connection/current transaction;
- performs the same exact durable reads and validations;
- issues no `SET TRANSACTION`;
- performs no commit/rollback;
- performs no write / `FOR UPDATE`.

Name is implementation-local; do not create a new public architecture surface unless required.

### D2 resolver

`PostgresTrustedReadinessEvidenceResolver.resolve(...)` must use the pure current-transaction helper.

It must not call public `PostgresExecutionStateLoader.load()`.

It must not issue:

- `SET TRANSACTION`;
- COMMIT;
- ROLLBACK;
- `FOR UPDATE`;
- any UPDATE/INSERT/DELETE.

This is required so D3 can later call the accepted D2 resolver after D3 has already locked the active control in a caller-owned writable transaction.

RF01 does not implement that D3 lock.

## RF01-B — transition gap-set binding

In `persistence/recovery.py`:

- canonicalize/sort exact `SequenceGap` evidence deterministically;
- derive canonical current gap semantic fingerprint;
- require:

`derived_gap_semantic_fingerprint == continuity_transition.gap_set_fingerprint`

- mismatch => `TrustedRecoveryEvidenceError`;
- caller-supplied `gap_semantic_fingerprint` must still be ignored/overwritten.

Do not change `ContinuityTransitionReceipt` schema or W4R-A frozen source.

## Required counterexamples

Add focused evidence for at least:

1. D2 resolver source path does not call public standalone loader;
2. D2 resolver does not issue `SET TRANSACTION`;
3. standalone `PostgresExecutionStateLoader.load()` still establishes `REPEATABLE READ READ ONLY`;
4. D2 resolver performs no commit/rollback;
5. D2 resolver contains no `FOR UPDATE`/write path;
6. canonical exact gaps matching transition `gap_set_fingerprint` construct successfully;
7. transition gap fingerprint stale/mismatched against durable exact gaps fails closed;
8. caller-provided `gap_semantic_fingerprint` cannot bypass the mismatch;
9. gap ordering is deterministic;
10. existing cross-account/generation/cut/root/C14 counterexamples remain green;
11. no READY/finalize/handoff/activate surface appears.

## Test gates

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c15_account_recovery_readiness.py -q --basetemp .\.tmp\pytest-w4r-d2-rf01-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_operational_postgres.py tests/unit/test_c13_reconciliation_case_scope.py tests/unit/test_c14_reconciliation_run.py tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_c10_broker_reconstruction.py -q --basetemp .\.tmp\pytest-w4r-d2-rf01-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-d2-rf01-full
```

If production changes after final full regression, rerun and report transparently.

## Tooling

`CONTROLLED_ROUTE_SET`

Keep Amendment 01 route behavior:

- if repository-local edit route is known blocked by the same reparse guard, go directly to controlled staging;
- exact authorized-file staging only;
- exact-scope copy-back;
- pytest only from repository checkout with repository-local basetemp;
- no repeated equivalent failed route attempts.

Route switching does not require semantic reauthorization.

## Correction corridor

Within the four authorized files:

- bounded test fixture updates required by the two RF01 assertions are allowed;
- no production semantic expansion beyond RF01-A/RF01-B;
- no other test file compatibility expansion.

Any need outside this scope => STOP / REAUTHORIZATION.

## Git

Exactly one RF01 runtime commit:

`fix(recovery): seal W4R-D2 same-world resolver`

Before push:

- origin/master must still equal the RF01 governance execution baseline;
- no amend/rebase/force push.

Push once, then STOP reviewer.

## Completion report

Report:

- initial HEAD;
- final HEAD/origin;
- exact changed files;
- diff size;
- targeted/compat/full results;
- transaction-composability evidence;
- gap linkage evidence;
- semantic correction cycles;
- tooling route switches/retries;
- 5HR consumption when available;
- migration/PostgreSQL/broker I/O = NO;
- STOP.

## Side effects denied

- D3;
- C15 READY integration;
- final handoff;
- recovery-control activation/deactivation;
- new writer semantics;
- migration;
- actual PostgreSQL/V07;
- A08;
- broker/paper/Shioaji I/O;
- production;
- P7;
- W4 closure/credit.
