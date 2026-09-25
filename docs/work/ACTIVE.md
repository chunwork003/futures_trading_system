# ACTIVE WORK PACKAGE

## 1. Work Package ID

GAP-08ABCD

---

## 2. Title

Persistence Foundation + Event Ledger

---

## 3. Status

COMPLETED / ACCEPTED

Design Freeze：COMPLETED。

Runtime Authorization：COMPLETED。

Launch Gate：

`CONSUMED`

Architecture ancestor：

`0b410ac8fb18887f96acc4e0bbde72d21cd16d6c`

Design freeze commit：

`17ef3eabe924a45e62fb4f22451c3c19b2497ff3`

Accepted runtime commit：

`98dc38ce39bdab191ce0bc6d71e37ef69059ec9c`

---

## 4. Recommended Model

GPT-5.6 Sol

Effort：輕度

Execution Mode：LEVEL_3A_BOUNDED

Model / effort不得中途切換。

Level 3B remains NOT_ENABLED。

---

## 5. Goal

一次建立 storage-neutral persistence contracts、PostgreSQL foundation、migration/UoW 與可實際承載 material event evidence 的 append-only event ledger。

這是第一個 expanded runtime calibration bundle，不拆回 A/B/C/D 四次 execution。

---

## 6. Blueprint Scope

Implements：

K110 K120 K130 K140 K150 K160 K170
K210 K220 K230 K240
K610 K620 K630 K640 K650 K660 K670 K680

19 leaves / weight 77。

Touches：

K300 K400 K500 K700 future consumers。

Does Not Implement：

K310-K540
K710-K770
K810-K930

K520 remains GAP-09-owned。

---

## 7. Baseline

Branch：master

Required architecture ancestor：

`0b410ac8fb18887f96acc4e0bbde72d21cd16d6c`

Recorded full regression：869 passed

Known warning：GAP-ENV-001 / PytestCacheWarning

Known untracked：data/

data/ must not be modified/staged。

---

## 8. Architecture Freeze

Canonical ownership：

- persistence/ = storage-neutral contracts。
- persistence/postgres/ = PostgreSQL implementation。
- persistence/postgres/migrations/ = PostgreSQL versioned SQL。

Analytical plane remains Parquet / DuckDB / Polars。

DuckDB postgres extension is not operational authority。

---

## 9. Dependency / Package Freeze

pyproject package discovery must include persistence*。

Optional PostgreSQL dependency：

psycopg[binary]==3.3.6

Use lazy import at driver boundary so base package/unit tests do not require PostgreSQL connectivity。

---

## 10. Public Storage-Neutral Contracts

Errors：

- PersistenceContractError(ValueError)
- PersistenceTransactionError(RuntimeError)
- PersistenceConflictError(RuntimeError)
- EventIdentityConflictError
- EventSequenceConflictError
- IdempotencyConflictError

Helpers：

- normalize_stable_id(str) -> str
- require_exact_decimal(Decimal) -> Decimal
- normalize_aware_utc(datetime) -> datetime

Protocols：

- AppendOnlyRepository.append(record) -> None
- SnapshotRepository.append_snapshot(snapshot) -> None
- SnapshotRepository.latest(key)
- SnapshotRepository.as_of(key, at)
- UnitOfWork context manager + commit/rollback

No generic CRUD API。

No update/delete on AppendOnlyRepository。

---

## 11. Numeric / Time / Identity

- exact persistence values use Decimal；float rejected。
- non-finite Decimal rejected。
- timestamps must be timezone-aware and normalize UTC。
- stable string IDs trim/nonblank。
- database/backend must not rewrite canonical ID。
- no automatic UUID migration。

---

## 12. UnitOfWork

- explicit commit only。
- exit without commit -> rollback。
- exception -> rollback + propagate。
- repository never commits。
- no hidden retry。
- no double finalize。

PostgresUnitOfWork：

- connection factory based。
- autocommit=False required。
- connection remains adapter-internal。

---

## 13. PostgreSQL Driver

connect_postgres(dsn)：

- lazy psycopg import。
- nonblank DSN。
- autocommit=False。
- never log DSN/credentials。
- missing driver -> PostgresDriverUnavailableError。

---

## 14. PostgreSQL Compatibility Contract

PostgresIntegrationStatus：

PENDING / VERIFIED / FAILED

PostgresCompatibilityEvidence immutable：

- major
- status
- server_version_num
- driver_version
- verified_on
- evidence

Initial POSTGRES_COMPATIBILITY_TARGETS：

- PostgreSQL 17 PENDING
- PostgreSQL 18 PENDING

detect_postgres_major(server_version_num) pure。

No automatic verification from version number alone。

No production/live authorization field or behavior。

---

## 15. PostgreSQL Namespace / Migration

Operational schema：trading

Migration metadata：trading.schema_migrations

Migration filename：NNNN_name.sql

Rules：

- ascending deterministic versions。
- duplicate version reject。
- applied version/name mismatch -> MigrationConflictError。
- runner does not commit/rollback。
- migration record written after migration SQL succeeds in same transaction。
- important TABLE/COLUMN/FUNCTION Traditional Chinese COMMENT。
- no destructive migration。

---

## 16. TradingEvent

Immutable Pydantic / extra forbid。

Fields：

event_id
event_type
source
entity_type
entity_id
occurred_at
received_at
sequence
event_version
idempotency_scope
idempotency_key
correlation_id optional
causation_id optional
payload_json

Rules：

- required strings trim/nonblank。
- sequence >= 0。
- event_version >= 1。
- timestamps aware + UTC normalized。
- no received_at >= occurred_at requirement。
- payload_json must be JSON object and canonicalized deterministically。

---

## 17. Event Identity / Idempotency

Event ID unique globally within ledger。

Sequence scope：

(source, entity_type, entity_id, sequence)

Idempotency scope：

(idempotency_scope, idempotency_key)

Semi-duplicate with different canonical event is conflict，not silent duplicate。

---

## 18. Event Append Result

EventAppendStatus：APPENDED / DUPLICATE

EventAppendResult：

- status
- event_id

DUPLICATE only for canonically identical persisted event。

---

## 19. EventLedgerRepository

Storage-neutral Protocol：

- append(event) -> EventAppendResult
- get(event_id)
- get_by_idempotency(scope, key)
- list_after(source, entity_type, entity_id, after_sequence, limit)

list_after：sequence ascending；limit > 0。

No update/delete。

---

## 20. PostgreSQL Event Ledger

Table：trading.event_ledger

Constraints：

- event_id PRIMARY KEY
- UNIQUE(idempotency_scope, idempotency_key)
- UNIQUE(source, entity_type, entity_id, sequence)
- sequence >= 0
- event_version >= 1
- occurred_at / received_at TIMESTAMPTZ
- payload JSONB

PostgresEventLedgerRepository never commits。

Conflict mapping must preserve：

- event identity conflict
- sequence conflict
- idempotency conflict

---

## 21. Optional Real PostgreSQL Verification

Environment variables：

POSTGRES17_TEST_DSN
POSTGRES18_TEST_DSN

If absent：integration tests SKIP and status remains PENDING。

If present：

- server major must match target exactly。
- run migration/event smoke in transaction。
- rollback test material。
- record evidence only when test actually passes。

No Docker/service installation without explicit environment support。

No fake VERIFIED result。

---

## 22. Allowed Runtime Files

Primary：

pyproject.toml
persistence/__init__.py
persistence/contracts.py
persistence/events.py
persistence/postgres/__init__.py
persistence/postgres/compatibility.py
persistence/postgres/driver.py
persistence/postgres/migrations.py
persistence/postgres/uow.py
persistence/postgres/event_ledger.py
persistence/postgres/migrations/*.sql

Tests：

tests/unit/test_persistence_contracts.py
tests/unit/test_postgres_foundation.py
tests/unit/test_event_ledger.py
tests/integration/test_postgres_foundation.py

Optional CLI only if useful and within frozen semantics：

scripts/verify_postgres_compatibility.py

---

## 23. Forbidden Areas

data/**
database/**
trading/**
backtest/**
strategy/**
strategies/**
features/**
adapters/**

No unrelated cleanup。

No broker execution changes。

No LIVE authorization。

---

## 24. Required Unit Verification

At minimum verify：

1. stable ID normalization/rejection。
2. Decimal exact/non-finite/float rejection。
3. aware datetime UTC normalization / naive reject。
4. Protocol runtime-checkable behavior。
5. UnitOfWork explicit commit。
6. rollback on uncommitted exit。
7. rollback on exception。
8. double finalize reject。
9. autocommit=True reject。
10. migration deterministic discovery。
11. duplicate migration version reject。
12. migration conflict detection。
13. migration runner does not commit。
14. compatibility targets exactly 17/18 PENDING。
15. server_version_num major detection。
16. PENDING evidence does not claim verification。
17. VERIFIED/FAILED evidence requires explicit metadata。
18. TradingEvent immutable/extra-forbid。
19. event string normalization。
20. event timestamps UTC。
21. event sequence/version validation。
22. canonical JSON object normalization。
23. append APPENDED。
24. identical retry -> DUPLICATE。
25. event identity conflict。
26. idempotency conflict。
27. sequence conflict。
28. get/get_by_idempotency。
29. list_after ordering/limit。
30. repository never commits。
31. migration SQL contains required PK/UNIQUE/CHECK/TIMESTAMPTZ/JSONB semantics。
32. Traditional Chinese DB comments present。

---

## 25. Targeted / Compatibility / Regression

Targeted：

.\.venv\Scripts\python.exe -m pytest tests\unit\test_persistence_contracts.py tests\unit\test_postgres_foundation.py tests\unit\test_event_ledger.py -q

Optional integration：

.\.venv\Scripts\python.exe -m pytest tests\integration\test_postgres_foundation.py -q

Absent DSNs may produce SKIP，not VERIFIED。

Compatibility：

.\.venv\Scripts\python.exe -m pytest tests\unit\test_trading_account.py tests\unit\test_reconciliation.py tests\unit\test_trading_execution.py -q

Then full regression：

.\.venv\Scripts\python.exe -m pytest -q

---

## 26. Acceptance

PASS requires：

- frozen public contracts exact。
- storage-neutral domain boundary preserved。
- PostgreSQL code isolated。
- migration/UoW semantics explicit。
- operational event ledger implemented。
- no silent conflict/overwrite。
- PostgreSQL 17/18 remain PENDING unless real integration passes。
- targeted PASS。
- compatibility PASS。
- full regression PASS。
- git diff --check PASS。
- data/ untouched。

---

## 27. Hard Stop

STOP if：

- frozen persistence authority must change。
- generic CRUD abstraction becomes necessary。
- trading/domain must import psycopg。
- destructive migration required。
- idempotency conflict semantics ambiguous。
- transaction authority ambiguous。
- secret/DSN exposure。
- unrelated core regression。
- data/ modified。

---

## 28. Git

Commit message：

feat(persistence): add foundation and event ledger

Exact stage only allowed runtime/test files。

Push origin master，fetch，verify local == remote。

Final status only known data/。

No amend / rebase / force push / reset --hard。

---

## 29. Dynamic Calibration

This bundle intentionally expands scope versus prior Level 3A samples。

Do not judge success by low quota alone。

Final report must include：

- user-observed 5HR supplied later。
- wall time if observable。
- files read/created/modified。
- tool operations。
- correction cycles。
- retries。
- targeted/compatibility/full regression。
- PostgreSQL 17 integration status。
- PostgreSQL 18 integration status。
- implemented leaves / weight = 19 / 77。

Compare accepted work / resource after deterministic acceptance。

---

## 29A. Runtime Completion Evidence

Result：PASS。

Accepted runtime commit：

`98dc38ce39bdab191ce0bc6d71e37ef69059ec9c`

Verification：

- targeted：28 passed。
- PostgreSQL integration：2 skipped。
- compatibility：80 passed。
- full regression：897 passed / 2 skipped。
- git diff --check：PASS。
- final status：only `?? data/`。

PostgreSQL compatibility：

- 17：PENDING。
- 18：PENDING。

Calibration：

- user-observed 5HR：12%。
- files read：8。
- files created：14。
- existing files modified：1。
- tool operations：23。
- retries：1。
- correction cycles：1。
- wall time：約 12m09s。
- token/context：UNAVAILABLE。

Accepted Blueprint：

19 leaves / weight 77。

Next runtime：

NOT AUTHORIZED until GAP-08EF architecture/design freeze and gate release。

---

## 30. Documentation Responsibility

Codex runtime does not update deterministic governance/metrics/queue closure docs。

After runtime commit/push/report：STOP。

Do not begin GAP-08EF。

Do not enable Level 3B。

---

## 31. Re-entry Scope

Read first：

AGENTS.md
docs/work/ACTIVE.md

Then only minimum dependency reads：

pyproject.toml
trading/account.py
trading/reconciliation.py

and directly relevant existing tests required for compatibility。

No whole-repo rescan。

---

## 32. Runtime Launch Gate

Current：

    CONSUMED

Runtime authorization：

    COMPLETED
