# GAP-08 W4R-D3 Authorization Amendment 01 — RF01

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_D3_RF01_ONLY`

RF01 baseline:

`f0116524fb7254f912255023d2b80bf702a40f11`

Parent authorization:

`docs/work/GAP08_W4R_D3_AUTHORIZATION.md`

Independent review:

`docs/work/GAP08_W4R_D3_REVIEW_RF01.md`

## Goal

Correct exactly two D3 final-authority defects:

1. bind C14 formal boundary discovery/observation identity to the D2 trusted core;
2. canonically validate final handoff `recorded_at` through `AccountRecoveryControl`.

Retain the existing D3 evaluator/finalizer candidate otherwise.

No D2, C09 repository, UoW, migration or broker semantics change is authorized.

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

## RF01-A — C14 ↔ B2 exact identity linkage

In `evaluate_trusted_readiness(...)`:

before readiness classification, require exact linkage:

```text
boundary.discovery_run_id == trusted_core.discovery_receipt_id
boundary.observation_id == trusted_core.broker_observation_id
```

Both boundary values must be non-null exact stable identities.

Mismatch/missing:

`TrustedRecoveryEvidenceError`

This is a D3 final-authority guard only.

Do not:

- modify `TrustedReadinessEvidenceBundle`;
- modify D2 resolver;
- modify C14 repository/model;
- add fallback inference.

## RF01-B — canonical final-control construction

In `PostgresTrustedReadinessFinalizer.finalize(...)`:

replace final inactive-control `model_copy(update=...)` construction with normal `AccountRecoveryControl` validation/reconstruction.

Requirements:

- `recorded_at` must pass the existing model's aware-UTC validator;
- aware offset timestamps normalize canonically;
- naive timestamp fails before `finalize_handoff`;
- invalid time material fails before `finalize_handoff`;
- failure causes no commit;
- UoW exception path remains rollback authority.

Do not duplicate the datetime normalization algorithm in the finalizer.

Reuse the canonical model validator.

## Mandatory counterexamples first

Pure evaluator:

1. cross-discovery C14 boundary fails closed;
2. cross-observation C14 boundary fails closed;
3. missing boundary discovery identity fails closed;
4. missing boundary observation identity fails closed;
5. exact matching C14/B2 identities retain current READY behavior.

Finalizer:

6. naive `recorded_at` fails before C09 handoff;
7. invalid `recorded_at` fails before C09 handoff;
8. aware non-UTC timestamp is canonically normalized before repository handoff;
9. successful READY still calls C09 once and commits once;
10. non-READY still rollback/no-handoff;
11. control drift/finalize conflict still no commit.

## Test gates

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c15_account_recovery_readiness.py -q --basetemp .\.tmp\pytest-w4r-d3-rf01-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_operational_postgres.py tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_c13_reconciliation_case_scope.py tests/unit/test_c14_reconciliation_run.py tests/unit/test_c10_broker_reconstruction.py -q --basetemp .\.tmp\pytest-w4r-d3-rf01-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-d3-rf01-full
```

If production code changes after the final full regression, rerun and report transparently.

## Tooling

`CONTROLLED_ROUTE_SET`

Known repository reparse-point edit restriction is already established.

Codex may go directly to controlled staging.

Requirements:

- materialize/edit only exact authorized files;
- exact-scope copy-back only;
- immediate repository-local `git diff --check` and scope validation;
- pytest only from repository checkout;
- repository-local basetemp;
- do not retry known equivalent reparse routes.

Route switching inside the set is not semantic reauthorization.

## Compatibility corridor

Within the two authorized test files, bounded fixture/test-double changes needed only for RF01-A/B are allowed.

No other test file write is authorized.

No production scope expansion is authorized.

## Git

Exactly one RF01 runtime commit:

`fix(recovery): seal W4R-D3 final authority guards`

Before push:

- origin/master must still equal the RF01 governance execution baseline;
- no amend/rebase/force push.

Push once, then STOP reviewer.

## Completion report

Report:

- initial/final HEAD + origin;
- exact changed files/diff size;
- C14/B2 identity-linkage evidence;
- canonical recorded_at evidence;
- targeted/compat/full results;
- semantic correction cycles;
- tooling route switches/retries;
- 5HR consumption when available;
- migration/actual PostgreSQL/broker I/O = NO;
- STOP.

## Denied

- D2 semantic changes;
- C09 repository changes;
- UoW changes;
- migration;
- isolated PostgreSQL integration/concurrency execution;
- W4 closure;
- P7;
- broker/paper/Shioaji I/O;
- production activation.
