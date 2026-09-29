# GAP-08 W4R-D2 Authorization Amendment 03 — RF02

Status:

`BOUNDED_AUTHORIZED_FOR_GAP08_W4R_D2_RF02_ONLY`

RF02 baseline:

`2e87d00f9cf546911dc48f7dc784a8bb1d14ff84`

Parents:

- `docs/work/GAP08_W4R_D2_AUTHORIZATION.md`
- `docs/work/GAP08_W4R_D2_AUTHORIZATION_AMENDMENT_01.md`
- `docs/work/GAP08_W4R_D2_AUTHORIZATION_AMENDMENT_02.md`

Independent review:

`docs/work/GAP08_W4R_D2_REVIEW_RF02.md`

## Goal

Correct exactly one D2 same-world defect:

`broker_report_witness` must be scoped to the selected active recovery generation.

Retain all RF01 runtime material.

No D3 behavior is authorized.

## Exact writable files

Production:

- `persistence/postgres/recovery.py`

Tests:

- `tests/unit/test_operational_postgres.py`

Exactly these two files.

No new files.

## Production correction

Keep existing:

`_read_report_witness(cursor, account)`

unchanged for existing C12 / legacy final-revalidation behavior.

Add one private generation-scoped helper for D2.

Suggested contract:

```text
_read_generation_report_witness(
    cursor,
    account,
    recovery_generation,
) -> tuple[tuple[str, ...], int, int]
```

Exact implementation name may differ.

It must:

- use latest application by `(ingress_id, generation, application_sequence)`;
- filter inbox rows by exact:
  - `broker`;
  - `account_ref`;
  - `generation`;
- join application rows on exact ingress + generation;
- retain deterministic ordering;
- return deterministic canonical anchors;
- not use timestamp as current authority;
- not write/lock/commit/rollback.

`PostgresTrustedReadinessEvidenceResolver.resolve()` must use this generation-scoped helper when populating:

`TrustedReadinessEvidenceBundle.broker_report_witness`

Do not change the already generation-scoped `reports` query used by root resolution except for bounded refactor if mechanically necessary.

## Required tests

At minimum:

1. generation-scoped helper SQL contains:
   - `i.broker=%s`
   - `i.account_ref=%s`
   - `i.generation=%s`
2. parameters include the selected generation;
3. deterministic latest application remains based on `application_sequence DESC`;
4. same-account historical generation is excluded by the D2 helper;
5. legacy `_read_report_witness` remains BrokerAccount-wide and unchanged;
6. D2 resolver source uses the generation-scoped helper;
7. D2 resolver retains no:
   - `SET TRANSACTION`;
   - `FOR UPDATE`;
   - UPDATE/INSERT/DELETE;
   - `.commit()`;
   - `.rollback()`;
8. no D3 evaluator/finalize/handoff is added.

## Test gates

Targeted:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_operational_postgres.py -q --basetemp .\.tmp\pytest-w4r-d2-rf02-targeted
```

Compatibility:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_c15_account_recovery_readiness.py tests/unit/test_c09_broker_recovery_fence.py tests/unit/test_c13_reconciliation_case_scope.py tests/unit/test_c14_reconciliation_run.py -q --basetemp .\.tmp\pytest-w4r-d2-rf02-compat
```

Full regression exactly once after targeted/compatibility pass:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .\.tmp\pytest-w4r-d2-rf02-full
```

If production changes after full regression, rerun and report transparently.

## Tooling

`CONTROLLED_ROUTE_SET`

The same route envelope from Amendment 01 remains authorized.

Because repository-local patch is already known to be rejected by the same reparse guard, Codex may go directly to controlled staging.

Do not repeat equivalent failed patch routes.

Pytest runs only in repository checkout with repository-local basetemp.

## Semantic correction corridor

Only the generation-scoped D2 report witness correction is authorized.

No change to:

- D2 bundle model;
- RF01 transaction helper;
- gap linkage;
- C12 legacy helper semantics;
- C13/C14;
- C09 handoff;
- D3 evaluator/finalizer;
- migrations.

Need anything beyond this => STOP / REAUTHORIZATION.

## Git

Exactly one RF02 runtime commit:

`fix(recovery): scope W4R-D2 report witness generation`

Before push:

- origin/master must still equal the RF02 governance execution baseline;
- no amend/rebase/force push.

Push once, then STOP reviewer.

## Completion report

Report:

- initial HEAD;
- final HEAD/origin;
- exact changed files;
- diff size;
- generation-scoped witness evidence;
- proof legacy helper remains unchanged;
- targeted/compat/full results;
- semantic correction cycles;
- tooling route switches/retries;
- 5HR consumption when available;
- migration/PostgreSQL/broker I/O = NO;
- STOP.

## Side effects denied

- D3;
- READY integration;
- final handoff;
- migration;
- actual PostgreSQL/V07;
- broker/paper/Shioaji I/O;
- production;
- P7;
- W4 closure/credit.
