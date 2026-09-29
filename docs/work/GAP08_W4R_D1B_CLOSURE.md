# GAP-08 W4R-D1B Closure

Final accepted runtime:

`ef3400a0cbabc52b45cb2e4f5e69bae0711b64ba`

Disposition:

`W4R-D1B ACCEPTED / FROZEN / READ_ONLY`

Parent W4R-D:

`PARTIAL / D2 NEXT`

Internal W4R accepted weight remains:

`13 / 18`

Official correction-core acceptance remains:

`75 / 113`

W4 weight remains:

`18 / NOT_CREDITED`

## Accepted D1B authority

D1B extends the accepted D1A readiness currentness fence to the remaining C13/C14 writers.

### C13 reconciliation-case history

`PostgresReconciliationCaseRepository.append(...)` now:

1. locks the active BrokerAccount recovery-readiness fence;
2. locks the latest exact case version;
3. preserves account-scope fail-closed behavior;
4. derives the prior readiness contribution from the existing C13 semantic blocker owner;
5. appends the new immutable history version;
6. advances readiness exactly once only when blocker semantic material changes.

Accepted semantics:

- new unresolved HALT/REVIEW blocker => readiness advance;
- unresolved -> RESOLVED => readiness advance;
- result/policy/state material change => readiness advance;
- audit-only wrapper changes such as version/time/actor/evidence do not advance;
- inactive/missing recovery control causes no readiness update;
- repository never commits or rolls back;
- no duplicate C13 blocker algorithm was introduced.

### C14 formal-run establish

For a new exact run boundary:

`fence lock -> boundary insert -> readiness advance`

Accepted semantics:

- new boundary => advance once;
- exact duplicate boundary => no advance;
- conflicting duplicate => fail closed / no advance;
- inactive/missing recovery control => no advance.

### C14 terminal finalize

Accepted ordering:

1. exact boundary pre-read to resolve canonical BrokerAccount;
2. active readiness-fence lock;
3. exact boundary re-read `FOR UPDATE`;
4. locked boundary must equal pre-read boundary;
5. terminal-outcome insert;
6. new terminal outcome => readiness advance once.

Accepted fail-closed cases:

- missing boundary;
- boundary drift between pre-read and locked re-read;
- conflicting terminal retry.

Exact duplicate terminal outcome is idempotent and does not advance readiness.

No C14 formal-run semantics were changed.

## Final verification

Runtime commit:

`feat(recovery): fence W4R-D1B reconciliation writers`

Changed files:

- `persistence/postgres/reconciliation.py`
- `tests/unit/test_c13_reconciliation_case_scope.py`
- `tests/unit/test_c14_reconciliation_run.py`

Execution evidence:

- targeted: `22 passed`
- compatibility: `103 passed`
- full regression: `1351 passed / 4 skipped`
- exact scope: PASS
- `git diff --check`: PASS
- semantic correction cycles: `0`
- tooling retries: `1`
- user-observed 5HR: `10%`
- migration / actual PostgreSQL / broker I/O: NO

Mechanical intake:

`MECHANICAL_INTAKE_PASS / SEMANTIC_REVIEW_REQUIRED`

Independent semantic review:

`PASS`

## Tooling learning

The executor attempted one already-known external-staging pytest route and encountered the known Windows common-root permission failure.

This did not affect semantic acceptance, but it is retained as workflow debt:

known failing routes should move from prose prohibition to machine-enforced preflight/route selection.

## Freeze

D1B source semantics are now frozen/read-only.

Any later semantic change requires explicit reauthorization.

D2/D3 semantics are not granted by this closure.
