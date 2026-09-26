# GAP-08 Bounded Runtime Authorization — V06 + C01

## 1. Authorization Status

BOUNDED_RUNTIME_AUTHORIZED。

This authorization applies only to：

- V06 — Repository Persistence Baseline Verification。
- C01 — Expected State Authority Read Contract。

Execution order is mandatory：

    V06 PASS
        ->
    C01 implementation

If V06 does not PASS，C01 MUST NOT begin。

No other GAP-08 correction leaf is authorized。

---

## 2. Baselines

Architecture Decision Baseline：

`22ceaa729ab6e9da9c00ae52e09ae7116be5a743`

GOV-01 Governance Planning Baseline：

`f45742d9d16165f87f145f0d2bdc8d530772e5ee`

Correction-Freeze Baseline：

`93fb846a9c9cd61eea44427a86a542fc95f9ac28`

Runtime Candidate：

`6b62239bca1d11543944f9f078e577e16010bcbf`

Authorization Baseline：

the docs-only commit containing this authorization document。

The exact authorization commit SHA must be used as the runtime execution precheck HEAD。

---

## 3. Authorized Leaf Set

AUTHORIZED：

- V06。
- C01。

NOT AUTHORIZED：

- C02～C25。
- V01～V05。
- V07。

C01 may not silently absorb responsibility owned by C02、C03、C04、C12 or any later leaf。

---

## 4. Environment Scope

Authorized environment：

LOCAL_REPOSITORY_AND_TEST_ONLY。

Allowed：

- repository source inspection。
- static migration inspection。
- fake/mock/unit-test PostgreSQL repository behavior。
- Python unit tests。
- full regression with external PostgreSQL DSNs disabled。

Not allowed：

- connection to actual PostgreSQL 17/18 environment。
- migration execution。
- external broker connection。
- paper broker network I/O。
- production broker I/O。
- production environment verification。

---

## 5. Side-Effect Envelope

Runtime source modification：

AUTHORIZED_FOR_C01_ONLY。

Repository verification：

AUTHORIZED_FOR_V06_ONLY。

DB Side Effects：

NOT_ALLOWED。

Migration File Modification：

NOT_ALLOWED。

Migration Execution：

NOT_ALLOWED。

Broker Network I/O：

NOT_ALLOWED。

Broker Paper I/O：

NOT_ALLOWED。

Production Broker I/O：

NOT_ALLOWED。

V01～V05 capability verification：

NOT_AUTHORIZED。

V07 actual PostgreSQL environment verification：

NOT_AUTHORIZED。

---

## 6. V06 — Repository Persistence Baseline Verification

V06 is a read-only prerequisite。

It must verify that the existing foundation can be preserved：

- deterministic migration discovery。
- version/name migration conflict detection。
- caller-owned transaction finalization。
- PostgresUnitOfWork rollback/commit semantics。
- autocommit=False boundary。
- TradingEvent/EventLedger append-only foundation。
- PostgreSQL remains the operational persistence adapter family。
- DuckDB / analytical storage is not operational recovery authority。
- `0001` / `0002` are historical migration artifacts and must not be rewritten。

Required V06 tests：

    .\.venv\Scripts\python.exe -m pytest tests\unit\test_postgres_foundation.py tests\unit\test_operational_postgres.py -q

V06 PASS does not claim：

- PostgreSQL 17 integration verified。
- PostgreSQL 18 integration verified。
- actual environment conformance。
- schema completeness for C02～C25。

If V06 finds a frozen-contract contradiction requiring foundation redesign：

STOP。

Do not begin C01。

---

## 7. C01 — Expected State Authority Read Contract

### Frozen authority

C01 implements only the bounded expected-state read correction required by R-01 / R-05。

The authoritative result model must distinguish：

    NOT_INITIALIZED
    EXPLICIT_FLAT
    EXPECTED_POSITIONS

Read/integrity failures are not domain state。

### Required semantics

A valid persisted complete snapshot with zero positions：

    -> EXPLICIT_FLAT

A valid persisted complete snapshot with one or more positions：

    -> EXPECTED_POSITIONS

Missing snapshot without positive lifecycle/init authority：

    -> MUST NOT become EXPLICIT_FLAT
    -> MUST NOT become EXPECTED_POSITIONS
    -> MUST NOT silently become NOT_INITIALIZED
    -> must surface explicit typed baseline/read failure until later C02/C03 authority can prove lifecycle state

Repository/DB read failure：

    -> explicit ExpectedStateReadError or equivalent frozen typed boundary

Malformed/inconsistent persisted snapshot：

    -> explicit ExpectedSnapshotIntegrityError or equivalent frozen typed boundary

NOT_INITIALIZED must remain representable as a distinct domain result for later authoritative lifecycle proof。

### Legacy compatibility rule

Existing `ExpectedPositionLoader.load_positions()` compatibility may remain。

However：

    missing snapshot
        MUST NOT return ()

Only positively explicit FLAT may return：

    ()

Non-empty authoritative snapshot may return：

    snapshot.positions

Unknown/missing baseline must fail explicitly。

### Preferred bounded rewrite

C01 is marked：

BOUNDED_REWRITE_PREFERRED。

CODEX may replace the internal expected-state loading abstraction when doing so is simpler and safer than layering compatibility conditionals。

The rewrite must remain confined to C01 ownership。

Do not implement：

- AccountStateHead。
- AccountRecoveryCheckpoint。
- EXPECTED_STATE_INITIALIZED persistence。
- revision-1 bootstrap。
- RecoveryCut。
- final READY/HALT aggregation。
- broker reconciliation changes。

Those belong to later leaves。

---

## 8. Allowed Runtime Files

Primary allowed：

- `persistence/account.py`
- `persistence/postgres/account.py`

Conditional compatibility/export only when strictly required：

- `persistence/__init__.py`
- `persistence/postgres/__init__.py`

Tests：

- `tests/unit/test_operational_postgres.py`
- new bounded unit test file for expected-state authority if useful

No other runtime file is authorized without HARD_BLOCK review。

---

## 9. Forbidden Runtime Areas

Forbidden：

- `persistence/recovery.py`
- `persistence/postgres/migrations/**`
- `trading/reconciliation.py`
- `trading/execution.py`
- `backtest/**`
- `adapters/**`
- `strategy/**`
- `strategies/**`
- `features/**`
- `database/**`
- `data/**`
- broker/live credential or connectivity code

If C01 appears to require any forbidden runtime area：

STOP。

Do not widen scope。

---

## 10. Positive Acceptance Criteria

C01 PASS requires direct tests proving：

1. explicit empty persisted snapshot is classified EXPLICIT_FLAT。
2. non-empty persisted snapshot is classified EXPECTED_POSITIONS。
3. result models are immutable / exact where applicable。
4. explicit NOT_INITIALIZED domain state can be represented independently of FLAT。
5. legacy compatibility returns `()` only for explicit FLAT。
6. legacy compatibility returns positions for authoritative non-empty snapshot。
7. DB/repository errors preserve typed read-failure semantics。
8. malformed persisted snapshot preserves typed integrity-failure semantics。

---

## 11. Negative Acceptance Criteria

C01 MUST directly prove：

1. missing snapshot does not return `()`。
2. missing snapshot does not silently become EXPLICIT_FLAT。
3. missing snapshot does not silently become EXPECTED_POSITIONS。
4. missing snapshot does not claim NOT_INITIALIZED without positive lifecycle authority。
5. DB read error does not become a domain state。
6. corrupt snapshot does not fall back to latest/empty/default state。
7. no C02/C03/C12 authority is accidentally implemented inside C01。

Negative acceptance is mandatory。

---

## 12. Test Boundary

Before tests，external PostgreSQL integration DSNs must be disabled for this Work Package：

    POSTGRES17_TEST_DSN
    POSTGRES18_TEST_DSN

Targeted C01 tests：

    .\.venv\Scripts\python.exe -m pytest tests\unit\test_operational_postgres.py -q

If a new bounded test file is created，include it in the targeted command。

Compatibility check when applicable：

    .\.venv\Scripts\python.exe -m pytest tests\unit\test_reconciliation.py -q

Full regression：

    .\.venv\Scripts\python.exe -m pytest -q

The full regression must run with actual PostgreSQL integration DSNs disabled。

No broker network test is authorized。

---

## 13. Stop Conditions

STOP and report without guessing if：

- V06 foundation verification fails。
- C01 requires schema/migration change。
- C01 requires actual AccountStateHead lifecycle authority。
- positive NOT_INITIALIZED proof cannot be implemented without C02/C03。
- C01 requires `persistence/recovery.py` modification。
- existing public semantics conflict with frozen R-01/R-05 authority。
- full regression exposes an unrelated architecture failure。
- more than two scope-internal correction cycles are required。
- broker or real DB access would be required。

NOT_INITIALIZED positive lifecycle proof may remain deferred to C02/C03。

That does not permit missing snapshot -> FLAT。

---

## 14. Git Policy

Execution sequence：

    precheck exact Authorization Baseline
    -> V06 verification
    -> if PASS, C01 implementation
    -> targeted tests
    -> compatibility tests if applicable
    -> full regression
    -> git diff --check
    -> exact scope validation
    -> commit
    -> push
    -> final report
    -> STOP

No amend。

No rebase。

No force push。

No automatic start of C22 or C11。

---

## 15. Commit Scope

Expected runtime commit：

C01 only。

Suggested commit message：

`fix(persistence): distinguish authoritative expected state reads`

V06 produces verification evidence but does not require a separate runtime commit when no repository change is required。

---

## 16. Final Report Required

Report：

- Authorization Baseline。
- V06 PASS / FAIL + evidence。
- C01 implementation summary。
- bounded rewrite used：YES / NO。
- files changed。
- positive acceptance tests。
- negative acceptance tests。
- targeted tests。
- compatibility tests。
- full regression。
- skipped tests / warnings。
- external PostgreSQL DSNs disabled：YES / NO。
- migration executed：NO。
- broker I/O performed：NO。
- git diff --check。
- commit SHA。
- push result。
- working-tree status。
- newly discovered GAPs。
- recommendation for next leaf。

---

## 17. Stop Boundary

After C01 commit / push / final report：

STOP。

C22、C11、C02 or any other correction leaf remains NOT_AUTHORIZED until the next explicit authorization decision。
