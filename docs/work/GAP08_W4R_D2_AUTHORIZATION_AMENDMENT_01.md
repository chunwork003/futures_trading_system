# GAP-08 W4R-D2 Authorization Amendment 01 — Controlled Route Set

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_D2_RESUME_ONLY`

Blocked governance/runtime HEAD:

`9cdcf9ba432104330dfd89355f541df3af148641`

Parent authorization:

`docs/work/GAP08_W4R_D2_AUTHORIZATION.md`

Blocker:

`docs/work/GAP08_W4R_D2_TOOLING_BLOCKER_01.md`

## Semantic authority

All semantic requirements, invariants, counterexamples, test gates, Git policy, side-effect restrictions, protected files, and the exact four-file write scope from the parent D2 authorization remain unchanged.

This amendment changes tooling execution mechanics only.

No D2 architecture re-planning is authorized or required.

## Exact writable files — unchanged

Production:

- `persistence/recovery.py`
- `persistence/postgres/recovery.py`

Tests:

- `tests/unit/test_c15_account_recovery_readiness.py`
- `tests/unit/test_operational_postgres.py`

Exactly these four files.

No new runtime/test files.

## TOOLING_MODE

`CONTROLLED_ROUTE_SET`

### Route A — repository-local direct

Use repository-local direct editing/patching when the workspace permits it.

If a reparse-point/workspace guard rejects this route, record one tooling route failure and immediately switch to Route B.

Do not retry equivalent absolute/relative forms after the same guard class has been positively identified.

### Route B — controlled staging root

Authorized fallback.

Requirements:

1. create/use one controlled non-reparse staging root;
2. materialize only the exact four authorized files plus minimum read-only dependencies needed by the edit tool;
3. edit only the exact four authorized files;
4. staging diff must contain only the exact authorized file paths;
5. copy back only the exact changed authorized files;
6. immediately verify repository-local `git diff --name-only`, `git diff --check`, and protected scope;
7. all pytest execution occurs in the repository checkout, not in external staging;
8. use repository-local `.tmp\pytest-*` basetemp paths.

The staging root is a tooling workspace only. It is not an alternate Git authority, test environment, or commit location.

### Route switching

Route A -> Route B is pre-authorized.

It:

- does not require STOP;
- does not require governance amendment;
- does not count as semantic correction;
- should be reported as one tooling route switch/retry.

STOP only if:

- Route B also cannot safely materialize/copy back;
- write scope must expand;
- a protected production owner must change;
- architecture/authority semantics must change;
- a migration/schema change becomes necessary.

## Compatibility corridor

Within the already-authorized two D2 test files, Codex may make bounded fixture/test-double adjustments needed solely to express the frozen D2 contracts.

This corridor may not:

- change production semantics;
- add another production file;
- weaken fail-closed assertions;
- change D1/B/C accepted semantics;
- make tests accept caller authority shortcuts.

A compatibility need in any other test file remains STOP / reauthorization.

## Known failing routes

Do not use external staging for pytest.

Do not repeatedly try repository-local `apply_patch` after the reparse-point guard has already rejected the route.

Line-ending warnings alone are not semantic failures.

## Execution behavior

Counterexample first.

Search before read.

Minimum sufficient context.

Then complete the same D2 package through:

`edit -> targeted -> compatibility -> full regression -> exact scope -> one commit -> push -> STOP reviewer`

Do not split D2 again merely because the edit transport changes.

## Tests — unchanged

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c15_account_recovery_readiness.py -q --basetemp .\.tmp\pytest-w4r-d2-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_operational_postgres.py tests/unit/test_c13_reconciliation_case_scope.py tests/unit/test_c14_reconciliation_run.py tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_c10_broker_reconstruction.py -q --basetemp .\.tmp\pytest-w4r-d2-compat
```

Full:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-d2-full
```

## Git — unchanged

Exactly one runtime commit:

`feat(recovery): add W4R-D2 trusted readiness bundle`

No amend/rebase/force push.

Push once, then STOP for independent review.

## Completion report

In addition to the parent D2 report, explicitly report:

- initial route;
- whether Route A was rejected;
- whether Route B was used;
- copy-back exact-scope result;
- tooling route switches/retries;
- semantic correction cycles;
- user-observed 5HR when available.
