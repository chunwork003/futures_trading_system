# K — Persistence / Recovery

## Status

BUILDING / PROVISIONAL until Blueprint baseline acceptance。

---

## Domain Purpose

建立 storage-neutral operational persistence contracts、append-only trading evidence、snapshots、idempotency、decision provenance 與 deterministic restart recovery。

V1 operational implementation family：

    PostgreSQL adapter

Domain / repository contracts：

    storage-neutral

Initial PostgreSQL compatibility targets：

    PostgreSQL 17
    PostgreSQL 18

Project-supported PostgreSQL major：

    determined only by explicit integration verification

Historical / analytical plane：

    Parquet
    DuckDB
    Polars

Authority separation：

- operational persistence authority 與 analytical storage/query authority 不互換。
- PostgreSQL-specific implementation 不向 trading/domain 洩漏。
- 不建立 PostgreSQL / DuckDB / Parquet 共用 generic CRUD repository。

Target ownership：

    persistence/
        storage-neutral contracts / ports
        postgres/
            PostgreSQL-specific implementation

DuckDB PostgreSQL extension only serves optional analytical bridge use cases。

---


## Capability Groups

| Group | Name | Responsibility |
|---|---|---|
| K100 | Operational SOR / PostgreSQL Adapter | storage-neutral authority contract / PostgreSQL implementation / compatibility / transaction boundary |
| K200 | Persistence Ports | domain-facing repository contracts |
| K300 | Execution Persistence | Order / OrderEvent / Fill |
| K400 | Account / Position Persistence | expected / broker snapshots / reconciliation |
| K500 | Strategy State | strategy / feature restart state |
| K600 | Event Ledger / Idempotency | append-only evidence / sequence / duplicate protection |
| K700 | Restart Recovery | reconstruct / query broker / reconcile / READY |
| K800 | Decision / Risk Provenance | material action trace |
| K900 | Backup / Restore / Retention | operational recoverability |

---

## Engineering Leaves

| ID | Name | Purpose | Lifecycle | Weight | Maps |
|---|---|---|---|---:|---|
| K110 | Operational SOR Boundary | storage-neutral operational authority；PostgreSQL 為 V1 adapter family | ACCEPTED | 5 | K01 |
| K120 | Schema Versioning / Migration | DB schema change 必須 versioned / reviewable | ACCEPTED | 4 | K01 |
| K130 | Operational Numeric Types | money/price/margin 使用 NUMERIC-compatible exact semantics | ACCEPTED | 4 | K01 |
| K140 | Operational Time Types | event / observation timestamps 使用 TIMESTAMPTZ | ACCEPTED | 4 | K01 |
| K150 | Stable Identifier Types | signal/decision/order/fill/trade/account IDs 不依 display text | ACCEPTED | 4 | K01 |
| K160 | Transaction Boundary | related state/event writes 有明確 transaction semantics | ACCEPTED | 5 | K01 |
| K170 | DB Documentation | important table/column/function 使用繁體中文 COMMENT | ACCEPTED | 2 | K01 |
| K210 | Repository Port Boundary | trading/domain 不直接依賴 PostgreSQL ORM/driver | ACCEPTED | 4 | K01 |
| K220 | Append Repository Contract | event/evidence insert 與 mutable projection update 分離 | ACCEPTED | 4 | K01,K05 |
| K230 | Snapshot Repository Contract | latest / as-of snapshot query semantics | ACCEPTED | 4 | K03 |
| K240 | Unit-of-Work Boundary | multi-write use case consistency contract | ACCEPTED | 4 | K01 |
| K310 | Order Persistence | internal/broker order identity、status、intent linkage | DESIGN_FROZEN | 4 | K02 |
| K320 | OrderEvent Persistence | append-only order lifecycle event | DESIGN_FROZEN | 5 | K02,K05 |
| K330 | Fill Persistence | actual fill evidence durable storage | DESIGN_FROZEN | 5 | K02 |
| K340 | Execution Correlation | intent → order → event → fill correlation/causation | DESIGN_FROZEN | 4 | K02,K04 |
| K350 | Broker External ID Persistence | broker order/trade/deal identity 明確保存 | DESIGN_FROZEN | 4 | K02 |
| K410 | AccountPositionSnapshot Persistence | internal expected state snapshot | DESIGN_FROZEN | 4 | K03 |
| K420 | BrokerPositionSnapshot Persistence | broker actual observation history | DESIGN_FROZEN | 4 | K03 |
| K430 | AccountSnapshot Persistence | cash/equity/margin/position observation | DESIGN_FROZEN | 4 | K03 |
| K440 | ReconciliationCase Persistence | mismatch / evidence / resolution lifecycle | DESIGN_FROZEN | 5 | K03,K07 |
| K450 | Expected / Actual Separation in Schema | expected 與 actual 不共用可 silent overwrite row | DESIGN_FROZEN | 5 | K03 |
| K510 | StrategyStateSnapshot | restart-required strategy state | DESIGN_FROZEN | 4 | K06 |
| K520 | Incremental Feature State Snapshot | GAP-09 state 可 persistence/reconstruct | DESIGNED | 4 | K06 |
| K530 | Strategy Config / Version Link | state 可連 strategy/config version | DESIGN_FROZEN | 3 | K06 |
| K540 | Safe Snapshot Boundary | snapshot 只在一致 state boundary 保存 | DESIGN_FROZEN | 4 | K06 |
| K610 | Trading Event Ledger | append-only material trading event history | ACCEPTED | 5 | K05 |
| K620 | Event ID | globally/stably unique event identity | ACCEPTED | 3 | K05 |
| K630 | Occurred / Received Time | event occurrence 與接收時間分離 | ACCEPTED | 4 | K05 |
| K640 | Event Sequence | source/entity ordering 可檢查 | ACCEPTED | 4 | K05 |
| K650 | Event Version | event schema/version 可演進 | ACCEPTED | 3 | K05 |
| K660 | Idempotency Key | duplicate request/event 可安全辨識 | ACCEPTED | 5 | K05 |
| K670 | Correlation / Causation IDs | material workflow 可完整 trace | ACCEPTED | 4 | K04,K05 |
| K680 | No Silent Event Mutation | historical execution evidence 不以 update 覆蓋原事件 | ACCEPTED | 5 | K05 |
| K710 | Recovery State Load | process start 載入 persisted expected / execution / strategy state | DESIGN_FROZEN | 5 | K07 |
| K720 | Broker Actual Query Dependency | recovery 必須取得 broker actual observation | DESIGN_FROZEN | 5 | K07 |
| K730 | Recovery Reconciliation | persisted expected vs actual broker state | DESIGN_FROZEN | 5 | K07 |
| K740 | Strategy Reconstruction | account/reconciliation safe 後 reconstruct strategy state | DESIGN_FROZEN | 5 | K06,K07 |
| K750 | Recovery Validation | identity / sequence / config / state consistency verification | DESIGN_FROZEN | 5 | K07 |
| K760 | Recovery READY Gate | validation success 才允許 operational continuation | DESIGN_FROZEN | 5 | K07 |
| K770 | Recovery HALT / Manual Review | unresolved mismatch 不 silent recover | DESIGN_FROZEN | 5 | K07 |
| K810 | TradingDecision Persistence | target / action / attribution evidence | DESIGNED | 4 | K04 |
| K820 | DecisionContext Persistence | strategy/config/git/feature/market context | DESIGNED | 4 | K04 |
| K830 | RiskDecision Persistence | allow/reject/reason/input evidence | DESIGNED | 4 | K04 |
| K840 | Material Action Provenance | Signal → Decision → Risk → Order → Fill → Position → Trade | DESIGN_FROZEN | 5 | K04 |
| K850 | HOLD Provenance Policy | HOLD 可 lightweight / sampled，不等同 material action | DESIGNED | 3 | K04 |
| K910 | Backup Policy | operational SOR 有可執行 backup policy | NOT_DESIGNED | 4 | K01,K07 |
| K920 | Restore Drill | restore 後可驗證 state / event / reconciliation | NOT_DESIGNED | 5 | K07 |
| K930 | Retention / Archival | event/audit/snapshot retention 明確 | NOT_DESIGNED | 3 | K01 |

---

## Post-Runtime Recovery Decision Checkpoint

ADR-002 R-01 / R-02 / R-03 / R-04A-E are authoritative for current GAP-08 acceptance correction。

Required correction direction：

- missing expected snapshot = NOT_INITIALIZED，never implicit FLAT。
- read failure and checkpoint/snapshot integrity failure are distinct typed failures。
- BrokerAccount is the minimum recovery isolation scope。
- BrokerAccount owns a contiguous transactional AccountStateHead revision。
- every account authority revision gets one exact AccountRecoveryCheckpoint。
- checkpoint exact-references expected_snapshot_id；no SELECT-latest recovery fallback。
- sequence-0 PENDING and broker_client_order_ref are durable before broker submission。
- material-emitting strategy snapshots and initial PENDING causal boundary commit atomically。
- MarketObservation revision references must resolve to durable immutable observation evidence。
- BrokerActionAttempt / BrokerActionResolution are append-only material authority evidence。
- BrokerActionHead is concurrency projection，not historical authority。
- BrokerDiscoveryObservation / health/raw broker evidence are observation evidence and do not advance AccountStateHead by themselves。
- ExecutionContinuityEpoch records local post-reconciliation continuity re-anchor without rewriting historical degradation。
- BrokerReportInboxEntry durably captures broker ingress before deferred canonical application。
- BrokerReportApplication records application/corroboration/defer/conflict evidence without mutating historical inbox rows。
- AccountRecoveryControl is durable operational concurrency control and is separate from AccountStateHead economic authority。
- one atomic material authority commit equals one BrokerAccount revision。
- one revision contains at most one canonical OrderEvent but may contain multiple Fill / BrokerActionResolution records。
- recovery_cut_revision must match locked AccountStateHead before authority mutation commit。
- stale reconstruction aborts/re-evaluates；it is not silently applied。
- position-changing Fill requires a complete new expected snapshot in the same transaction。
- status-only authority mutation carries forward prior exact expected_snapshot_id。
- terminal canonical economic state is immutable after accepted closure。
- canonical Fill set is the sole internal filled-economic projection authority。
- AccountAuthorityCommit has stable pre-commit identity + mutation fingerprint。
- ambiguous COMMIT is resolved by querying committed receipt before retry。
- committed_revision is a commit result，not idempotency identity。
- V1 AccountAuthorityCommitReceipt may use the existing append-only Trading Event Ledger as physical persistence envelope。
- live and recovery paths must share one account-authority persistence primitive；no parallel recovery persistence authority。
- K520 remains deferred；unknown historical feature/state correction impact -> REVIEW。

Scope expansion beyond original 35 / 151 now includes both R-03 operational market-observation evidence and R-04 broker recovery/action/inbox/authority-commit infrastructure。

All expanded scope remains unweighted and runtime-unauthorized until R-04F/G/H close and a replacement correction Work Package is frozen。

Retention/archive remains K930；no evidence required by recovery/audit may be silently deleted。

This checkpoint does not promote K lifecycle values。

## Core Persistent Entities

至少包含：

- TradingSession。
- MarketObservationCandidateEvidence。
- MarketObservationRevision。
- TradingDecision。
- DecisionContext。
- RiskDecision。
- Order。
- OrderEvent。
- Fill。
- BrokerActionAttempt。
- BrokerActionResolution。
- BrokerDiscoveryObservation。
- ExecutionContinuityEpoch。
- BrokerReportInboxEntry。
- BrokerReportApplication。
- AccountAuthorityCommitReceipt。
- AccountRecoveryCheckpoint。
- AccountRecoveryControl。
- AccountPositionSnapshot。
- BrokerPositionSnapshot。
- StrategyStateSnapshot。
- TradeRecord。
- ReconciliationCase。
- ManualOverride。
- Authorization。

---

## Identifier Baseline

至少考慮：

- signal_id。
- decision_id。
- order_id。
- broker_order_id。
- fill_id。
- trade_id。
- strategy_id。
- strategy_instance_id。
- logical_account_id。
- broker_account_id。
- correlation_id。
- causation_id。
- idempotency_key。

---

## Event Metadata

至少：

- event_id。
- occurred_at。
- received_at。
- sequence。
- version。

---

## Recovery Flow

    Process Start
    → Load Persisted Expected State
    → Query Broker Actual State
    → Reconcile
    → Reconstruct Strategy / Incremental State
    → Validate
    → READY

Mismatch：

    HALT
    or MANUAL_REVIEW
    or explicit authorized recovery workflow

不得 silent overwrite。

---

## Connections

| From | To | Contract |
|---|---|---|
| H300/H400 | K300/K600 | Order / OrderEvent / Fill |
| G400/G900 | K800 | Decision / Risk provenance |
| J300/J400 | K400 | expected / broker snapshots |
| J600 | K440 | ReconciliationCase |
| E300/E500 | K500 | incremental / strategy state |
| K700 | J700 | recovered expected state / startup readiness |
| K | M/N/O | application-facing persistent operational truth through ports/APIs |

---

## Authority

- persistence/domain contracts：storage-neutral operational semantics。
- PostgreSQL adapter family：V1 operational SOR implementation。
- PostgreSQL major support：explicit compatibility evidence，not architecture assumption。
- OrderEvent / Fill：execution evidence。
- AccountPositionSnapshot：internal expected projection history。
- BrokerPositionSnapshot：actual broker observation history。
- StrategyStateSnapshot：restart projection，不取代 strategy/config definition。
- Parquet：historical / feature dataset authority。
- DuckDB：research / analytical query engine，不是 operational SOR。
- Polars：DataFrame / research / feature computation，不是 operational SOR。
- DuckDB PostgreSQL extension：optional analytical bridge，不是 operational dependency。

Operational path：

    Domain
    -> Persistence Port
    -> PostgreSQL Adapter
    -> explicitly verified PostgreSQL major

Analytical path：

    Parquet + optional PostgreSQL analytical read
    -> DuckDB
    -> Polars / Python research

---


## Key Invariants

- repository/domain contract 不依賴 PostgreSQL major-specific API。
- PostgreSQL-specific SQL / psycopg type 只存在 persistence/postgres boundary。
- PostgreSQL 17 / 18 support 必須 individually integration-verified。
- official vendor support 不等同 project production support。
- operational money/price 使用 exact NUMERIC-compatible representation。
- Python Decimal 不經 binary float 中轉。
- operational timestamp 使用 timezone-aware semantics；PostgreSQL adapter 映射 TIMESTAMPTZ。
- canonical stable IDs 不因 backend 改變而改變。
- append-only evidence 不 silent overwrite。
- event 與 snapshot responsibility 分離。
- broker actual 不 silent overwrite expected state。
- domain/trading 不直接依賴 DB driver / ORM。
- idempotency 必須 persistence-aware。
- schema migration 不可 destructive silent change。
- Parquet / DuckDB / Polars analytical plane 不得成為 operational write authority。
- DuckDB postgres extension 不得成為 startup/recovery prerequisite。

---


## Sources

- SRC-POSTGRES-001。
- SRC-POSTGRES-VERSIONING-001。
- SRC-POSTGRES-17-001。
- SRC-POSTGRES-18-001。
- SRC-PSYCOPG-001。
- SRC-DUCKDB-001。
- SRC-DUCKDB-POSTGRES-001。
- SRC-DUCKDB-EXTENSIONS-001。
- SRC-POLARS-001。
- SRC-ADR-001。
- SRC-ARCH-001。

PostgreSQL implementation 不由 architecture 預設單一 major。

Initial integration targets：

    PostgreSQL 17
    PostgreSQL 18

Project support becomes VERIFIED only after explicit compatibility evidence。

---


## GAP-08 Architecture Review

Status：

ARCHITECTURE_REVIEW_COMPLETED / DECOMPOSED。

Runtime：

NOT_YET_AUTHORIZED。

Architecture pattern：

    storage-neutral contracts
    + backend-specific adapters

V1 operational adapter family：

    PostgreSQL

Analytical plane：

    Parquet + DuckDB + Polars

No generic cross-engine CRUD repository。

### Backend Compatibility Baseline

| Backend | Major | Vendor Supported | Psycopg Documented | Project Integration | Production Authorized |
|---|---:|---|---|---|---|
| PostgreSQL | 17 | YES | YES | PENDING | NO |
| PostgreSQL | 18 | YES | YES | PENDING | NO |

Rules：

- project support becomes VERIFIED only after explicit integration tests。
- no default major selected implicitly by domain/repository code。
- deployment must select an explicitly verified major。

### Canonical Ownership

Storage-neutral contracts：

    persistence/

PostgreSQL implementation：

    persistence/postgres/

Versioned PostgreSQL migrations：

    persistence/postgres/migrations/

### Stable Identity

- existing canonical IDs remain authority。
- backend surrogate key不得取代 domain stable ID。
- broker external ID 與 internal ID authority 分離。

### Numeric Contract

Domain：Decimal / exact numeric semantics。

PostgreSQL adapter：NUMERIC-compatible mapping。

Analytical conversions不得反向定義 operational canonical numeric contract。

### Time Contract

Domain：timezone-aware datetime。

PostgreSQL adapter：TIMESTAMPTZ-compatible mapping。

occurred_at / received_at / observed_at responsibility 分離。

### Event / Snapshot

- append-only evidence 不 silent mutate。
- snapshots are historical observations。
- latest / as-of 是 repository query semantics。

### Expected / Actual

- internal expected state 與 broker actual observation 分離。
- actual cannot overwrite expected。
- reconciliation cannot rewrite historical broker evidence。

### Transaction Boundary

- UnitOfWork owns multi-write commit / rollback。
- repository 不 hidden commit。
- transaction failure explicit propagate。
- no infinite / silent retry。

PostgreSQL isolation/retry details belong to GAP-08B。

### DuckDB PostgreSQL Bridge

Allowed：analytical read / research / ETL / audit exploration。

Forbidden：operational Order/Fill persistence、startup recovery、transaction authority、live durability boundary。

### Runtime Decomposition

| Order | Work Package | Blueprint Leaves | Scope | Status |
|---:|---|---|---|---|
| 1 | GAP-08ABCD | K110 K120 K130 K140 K150 K160 K170 K210 K220 K230 K240 K610 K620 K630 K640 K650 K660 K670 K680 | Persistence Foundation + Event Ledger | ACCEPTED |
| 2 | GAP-08EFGHI | K310 K320 K330 K340 K350 K410 K420 K430 K440 K450 K510 K530 K540 K710 K720 K730 K740 K750 K760 K770 | Operational Persistence + Recovery | READY_FOR_EXECUTION |
| 3 | GAP-08GHI | merged into GAP-08EFGHI | Strategy State + Recovery / Readiness | MERGED |

GAP-08ABCD：first expanded runtime calibration bundle。

Scope combines storage-neutral contracts、PostgreSQL adapter foundation、migration/transaction semantics、event ledger、version/sequence/idempotency/correlation。

PostgreSQL 17 / 18 support remains PENDING unless actual integration evidence is produced。

K520：

    DEFERRED_TO_GAP_09

GAP-08 closes after GAP-08ABCD and merged GAP-08EFGHI acceptance；K520 remains GAP-09-owned。

Level 3B remains NOT_ENABLED。

---

## GAP-08ABCD Architect Design Freeze

Status：

DESIGN_FROZEN。

Runtime bundle：

    GAP-08ABCD

Title：

    Persistence Foundation + Event Ledger

Blueprint Implements：

    K110 K120 K130 K140 K150 K160 K170
    K210 K220 K230 K240
    K610 K620 K630 K640 K650 K660 K670 K680

Total：19 leaves / weight 77。

### Canonical Ownership

Storage-neutral contracts：

    persistence/

PostgreSQL implementation：

    persistence/postgres/

PostgreSQL migrations：

    persistence/postgres/migrations/

No persistence contract may import psycopg。

No trading / strategy / backtest package may import psycopg。

### Package / Dependency Freeze

pyproject package discovery must include：

    persistence*

PostgreSQL optional dependency：

    psycopg[binary]==3.3.6

The dependency is adapter implementation detail；domain public contracts remain Psycopg-neutral。

### Persistence Contract Errors

Public errors：

    PersistenceContractError(ValueError)
    PersistenceTransactionError(RuntimeError)
    PersistenceConflictError(RuntimeError)
    EventIdentityConflictError(PersistenceConflictError)
    EventSequenceConflictError(PersistenceConflictError)
    IdempotencyConflictError(PersistenceConflictError)

PostgreSQL adapter errors：

    PostgresDriverUnavailableError(RuntimeError)
    MigrationConflictError(RuntimeError)

### Stable Identifier Contract

Public helper：

    normalize_stable_id(value: str) -> str

Rules：

- trim。
- blank rejected。
- storage backend does not rewrite canonical identity。
- no automatic UUID migration。
- broker external ID remains separate from internal ID。

### Exact Numeric Contract

Public helper：

    require_exact_decimal(value: Decimal) -> Decimal

Rules：

- only Decimal accepted for persistence-critical exact values。
- NaN / Infinity rejected。
- no float conversion。
- PostgreSQL adapter binds Decimal directly to NUMERIC-compatible columns。

### Time Contract

Public helper：

    normalize_aware_utc(value: datetime) -> datetime

Rules：

- naive datetime rejected。
- normalized result uses UTC。
- business event timestamps are caller supplied。
- PostgreSQL TIMESTAMPTZ mapping does not create hidden business time。

### AppendOnlyRepository

runtime-checkable Protocol：

    append(record) -> None

No update / delete contract。

### SnapshotRepository

runtime-checkable Protocol：

    append_snapshot(snapshot) -> None
    latest(key)
    as_of(key, at)

Rules：

- snapshot append creates historical observation。
- latest / as_of are query semantics。
- no silent overwrite of previous snapshot。
- as_of time must be timezone-aware。

Concrete account/position snapshot persistence remains GAP-08EF。

### UnitOfWork

runtime-checkable Protocol：

    __enter__
    __exit__
    commit()
    rollback()

Semantics：

- explicit commit only。
- exit without commit -> rollback。
- exception -> rollback and propagate。
- repository never independently commits。
- no hidden retry。
- finalized UnitOfWork cannot commit/rollback twice。

### PostgreSQL UnitOfWork

PostgresUnitOfWork accepts a connection factory。

Connection must use autocommit=False。

Adapter-internal connection access may exist under persistence/postgres only；domain code must type against UnitOfWork。

### Driver Boundary

Public PostgreSQL adapter function：

    connect_postgres(dsn: str)

Rules：

- lazy psycopg import。
- nonblank DSN required。
- autocommit=False。
- credentials/DSN must not be logged。
- missing driver -> PostgresDriverUnavailableError。

### PostgreSQL Compatibility

PostgresIntegrationStatus exact values：

    PENDING
    VERIFIED
    FAILED

PostgresCompatibilityEvidence immutable fields：

    major: int
    status: PostgresIntegrationStatus
    server_version_num: int | None
    driver_version: str | None
    verified_on: date | None
    evidence: tuple[str, ...]

Rules：

- PENDING carries no claimed integration evidence。
- VERIFIED / FAILED require explicit server version、driver version、verified date、nonblank evidence。
- compatibility evidence does not authorize production/live。

Initial constant：

    POSTGRES_COMPATIBILITY_TARGETS

contains PostgreSQL 17 and 18 as PENDING。

Public pure helper：

    detect_postgres_major(server_version_num: int) -> int

No automatic PENDING -> VERIFIED promotion merely because major is 17 or 18。

### Database Namespace

V1 PostgreSQL operational schema：

    trading

Migration metadata：

    trading.schema_migrations

Important PostgreSQL TABLE / COLUMN / FUNCTION receives Traditional Chinese COMMENT。

### Migration Contract

Migration filename：

    NNNN_name.sql

Rules：

- deterministic ascending version ordering。
- duplicate version rejected。
- applied version + different name -> MigrationConflictError。
- migration runner never commits or rolls back。
- UnitOfWork / caller owns transaction。
- migration record inserted only after SQL succeeds in same transaction。
- destructive migration outside this Work Package。

Bootstrap may idempotently ensure trading schema and schema_migrations metadata before planning versioned migrations。

### TradingEvent

Immutable Pydantic model / extra forbid。

Fields：

    event_id: str
    event_type: str
    source: str
    entity_type: str
    entity_id: str
    occurred_at: datetime
    received_at: datetime
    sequence: int
    event_version: int
    idempotency_scope: str
    idempotency_key: str
    correlation_id: str | None = None
    causation_id: str | None = None
    payload_json: str

Rules：

- IDs / names trim + nonblank。
- sequence >= 0。
- event_version >= 1。
- occurred_at / received_at timezone-aware and normalized UTC。
- received_at >= occurred_at is NOT required because clock/source skew is possible。
- payload_json must parse to a JSON object。
- payload_json normalized to deterministic canonical JSON text。
- optional correlation/causation IDs nonblank when present。

### Event Sequence Scope

Sequence identity：

    (source, entity_type, entity_id, sequence)

This scope is unique in PostgreSQL event ledger。

### Idempotency Scope

Idempotency identity：

    (idempotency_scope, idempotency_key)

This pair is unique in PostgreSQL event ledger。

### Event Append Result

EventAppendStatus exact values：

    APPENDED
    DUPLICATE

EventAppendResult immutable fields：

    status: EventAppendStatus
    event_id: str

Duplicate is returned only when persisted event is canonically identical。

Same identity / sequence / idempotency key with different canonical event must raise explicit conflict。

### EventLedgerRepository

storage-neutral runtime-checkable Protocol：

    append(event: TradingEvent) -> EventAppendResult
    get(event_id: str) -> TradingEvent | None
    get_by_idempotency(scope: str, key: str) -> TradingEvent | None
    list_after(source, entity_type, entity_id, after_sequence, limit) -> tuple[TradingEvent, ...]

list_after ordering：

    sequence ascending

limit must be positive。

No update/delete API。

### PostgreSQL Event Ledger

Canonical table：

    trading.event_ledger

Required constraints：

- event_id primary key。
- UNIQUE(idempotency_scope, idempotency_key)。
- UNIQUE(source, entity_type, entity_id, sequence)。
- sequence >= 0。
- event_version >= 1。
- occurred_at / received_at TIMESTAMPTZ。
- payload uses JSONB storage。

PostgresEventLedgerRepository never commits。

### Optional Integration Verification

Environment variables：

    POSTGRES17_TEST_DSN
    POSTGRES18_TEST_DSN

Integration tests：

- absent DSN -> explicit SKIP。
- provided DSN -> server major must exactly match expected target。
- verification runs inside transaction and rolls back test material。
- no production authorization。

If no real PostgreSQL test environment exists during this Work Package：

    PostgreSQL 17 = PENDING
    PostgreSQL 18 = PENDING

and Work Package must not claim VERIFIED。

### Explicitly Not Implemented

- Order / Fill entity persistence。
- AccountPosition / BrokerPosition persistence。
- ReconciliationCase persistence。
- Strategy state persistence。
- restart recovery orchestration。
- LIVE authorization。
- backup/restore。
- DuckDB as operational repository。
- PostgreSQL 17/18 production certification without evidence。

### Dynamic Work Package Calibration

This is the first expanded persistence bundle。

Sizing is measured by outcome efficiency，not a fixed quota target。

After runtime record：

- user-observed 5HR usage。
- wall time。
- files read/changed。
- tool operations。
- correction cycles。
- accepted leaves / weight。
- progress gain。

Next bundle may expand or contract based on accepted work per resource and correction/safety behavior。

---

## GAP-08ABCD Runtime Acceptance

Status：

ACCEPTED。

Runtime commit：

    98dc38ce39bdab191ce0bc6d71e37ef69059ec9c

Accepted scope：

    19 leaves / weight 77

Verification：

- targeted：28 passed。
- PostgreSQL integration：2 skipped because test DSNs absent。
- compatibility：80 passed。
- full regression：897 passed / 2 skipped。
- git diff --check：PASS。
- PG17：PENDING。
- PG18：PENDING。

Runtime evidence：

- storage-neutral persistence contracts。
- PostgreSQL driver / UnitOfWork / migration foundation。
- compatibility evidence contract。
- canonical TradingEvent。
- append-only PostgreSQL event ledger。
- explicit identity / sequence / idempotency conflict semantics。
- no PostgreSQL production verification claim。
- no LIVE authorization implication。

Calibration：

- user-observed 5HR：12%。
- wall time：約 12m09s。
- files read：8。
- files created：14。
- existing files modified：1。
- tool operations：23。
- command/tool retries：1。
- implementation correction cycles：1。
- token/context：UNAVAILABLE。

Dynamic sizing observation：

expanded scope did not increase 5HR usage above previous sample average；
future sizing remains empirical and must still respect public-semantics / authority / recovery safety seams。

---

## GAP-08EFGHI Architect Design Freeze

Status：DESIGN_FROZEN。

Title：

    Operational Persistence + Recovery

Runtime target：

    one expanded Level 3A execution

Blueprint Implements：

    E510 E520
    H170 H440 H450 H510 H520 H530 H540 H550 H830
    J340 J810 J820 J830
    K310 K320 K330 K340 K350
    K410 K420 K430 K440 K450
    K510 K530 K540
    K710 K720 K730 K740 K750 K760 K770

Total：

    35 leaves / weight 151

E530 / E540 remain frozen constraints but are not claimed as runtime acceptance scope。

K520 remains DEFERRED_TO_GAP_09。

### PostgreSQL Tables / Authority

V1 migration adds separate operational objects for：

- orders projection。
- fills append-only evidence。
- expected-position snapshot batches/items。
- broker-position observation batches/items。
- account snapshots。
- reconciliation-case history。
- strategy-state snapshots。

OrderEvent uses existing append-only trading.event_ledger；no duplicate mutable OrderEvent table。

Important TABLE/COLUMN/FUNCTION continue Traditional Chinese COMMENT requirement。

### Execution Repository Contracts

OrderRepository：

- add initial order projection。
- get by order_id。
- save next projection with optimistic expected version。
- lookup optional broker order ID。
- repository never commits。

FillRepository：

- append-only。
- get/list by order。
- duplicate internal fill ID -> identical duplicate or explicit conflict。
- native broker deal identity when present is uniqueness evidence。

OrderEventRepository：

- domain-specific adapter over EventLedgerRepository。
- append / get / list order events by contiguous sequence。
- no update/delete。

### Atomic Execution Boundary

One UnitOfWork must atomically cover the material processing of one new execution event：

1. append OrderEvent。
2. append zero or more new Fill evidence。
3. update derived Order projection。
4. append resulting complete expected-position snapshot batch when account projection changes。

Any failure rolls back all four effects。

Repositories never independently commit。

Broker actual observation is a separate observation transaction and never joins fill projection as hidden actual authority。

### ReconciliationCase History

Persistence model：append-only version history。

Fields：

    case_id
    version >= 1
    recorded_at
    reconciliation_case
    actor_ref optional
    evidence tuple[str, ...]

Rules：

- unique(case_id, version)。
- resolution appends a new immutable version。
- previous version is never updated/deleted。
- latest(case_id) is derived query semantics。
- persistence never executes corrective broker action。

### StrategyStateSnapshot

Canonical persistence owner：

    persistence/strategy_state.py

Immutable fields：

    snapshot_id
    strategy_instance_id
    strategy_id
    strategy_version
    config_version
    config_fingerprint
    instrument_id
    timeframe
    state_schema_version >= 1
    last_market_observation_id
    captured_at
    state_json JSON object

Strategy state codecs own state_json schema。

### Stateful Strategy Contract

Runtime-checkable protocol：

    state_schema_version
    export_state() -> JSON object
    restore_state(state) -> None

Initial strategy codecs required for：

- EMA_CROSS：previous EMA20 / EMA60。
- TREND_STATE：previous state。
- TREND_STATE_EXIT：previous state / virtual position / pending entry state。

Private attributes are not persisted directly outside explicit codec methods。

### Safe Strategy Snapshot Boundary

Snapshot is valid only after one completed market observation has finished strategy processing and before the next observation begins。

Snapshot represents logical strategy state only；it does not claim broker/account execution is simultaneously complete。

Recovery therefore reconciles persisted execution/account state before restoring strategy state。

READY requires snapshot.last_market_observation_id to exactly match the caller-required recovery observation boundary。

Missing/mismatched snapshot never silently replays guessed feature state。

### Recovery Order

Fixed sequence：

1. load persisted Order / Fill / expected account projections。
2. query BrokerPositionProvider actual state。
3. reconcile expected vs actual。
4. evaluate unresolved persisted ReconciliationCase history。
5. only when account/reconciliation permits continuation，load StrategyInstance + StrategyStateSnapshot。
6. validate strategy definition/version/config fingerprint/scope/state schema/market observation boundary。
7. instantiate strategy from canonical StrategyDefinition + StrategyInstance config。
8. restore through explicit state codec。
9. produce READY / HALT / REVIEW。

### Recovery Readiness Mapping

- account reconciliation HALT -> HALT。
- account reconciliation REVIEW -> REVIEW。
- unresolved HALT ReconciliationCase -> HALT。
- unresolved REVIEW_REQUIRED case -> REVIEW。
- missing strategy snapshot -> HALT。
- unknown strategy/version -> HALT。
- config/version/fingerprint/scope mismatch -> HALT。
- state schema mismatch -> HALT。
- state decode/restore failure -> HALT。
- market observation boundary mismatch -> HALT。
- READY only when account result is READY and every required strategy state restores successfully。

No automatic repair。

### Explicit Exclusions

- K520 incremental feature state。
- feature-history reconstruction design。
- H840 automatic safe broker retry。
- K810-K850 decision/risk provenance。
- LIVE authorization。
- backup/restore policy。
- destructive migration。
- big-bang conversion of all backtest consumers。

### Progress Experiment

Current lifecycle before freeze：47.30%。

Design-freeze lifecycle target：47.92%。

If all 35 leaves / weight 151 become ACCEPTED，projected lifecycle is approximately 53.57%，a gain of approximately 6.27 percentage points from current accepted baseline。

This is a sizing experiment，not a completion guarantee or quota target。

---

## Current GAP Mapping

- K110-K510 / K530-K770 → GAP-08。
- K810-K850 → GAP-PERSIST-001。
- K520 → GAP-09 persistence dependency。
- K910-K930 → V1 integration / operational readiness。

---

## Domain Acceptance

- K01～K07 全部有 leaf mapping。
- SOR / event / snapshot / provenance / recovery responsibility 分離。
- PostgreSQL 與 DuckDB/Parquet authority 不混淆。
- recovery flow 與 J startup readiness 對齊。

## Recovery Decision Checkpoint 4 — Recovery Authority Closure

R-04A-H are architecture-decided；ADR-002 is authoritative。

Persistence/recovery correction direction：

- BrokerActionAttempt / Resolution / Head are durable retry-safety authority。
- existing unresolved attempt forbids blind external re-invocation。
- AccountRecoveryControl owns recovery-session/final-handoff concurrency，separate from economic AccountStateHead。
- callback/broker-report evidence must remain durably capturable while account is REVIEW/HALT。
- recovery reconstruction、broker-action resolution and live execution share one BrokerAccount authority-commit primitive。
- READY handoff must verify the evaluated AccountStateHead is still current and no unapplied material evidence arrived。
- stale recovery evaluation causes abort/re-evaluation。
- READY / REVIEW / HALT transitions do not themselves advance economic AccountStateHead。
- production manual/out-of-band release depends on R-13 and remains default-deny until implemented。

Expanded R-03/R-04 scope must be mapped and lifecycle-reweighted before correction runtime authorization。

## Recovery Decision Checkpoint 5A — Complete RecoveryCut Contract

R-05 establishes a coherent complete RecoveryCut as the persistence read boundary。

AccountStateHead revision identifies the BrokerAccount material authority frontier but is not sufficient by itself to identify the entire recovery cut when required recovery evidence can change without advancing account_revision。

Required RecoveryCut currentness semantics must cover，where applicable：

- durable broker-report/callback inbox arrival/application state。
- AccountRecoveryControl / recovery-session generation。
- other explicitly recovery-critical non-revision-advancing dependencies。

No physical representation is mandated。

A single consistency witness may cover multiple dependency classes；architecture does not require one high-water/version field per dependency。

AccountAuthorityCommitReceipt belongs to authority validation closure and is validated against the corresponding authority commit。

Required transitive recovery closure must be complete before result may be labelled `VALID`。

Full historical archive replay is not required。

`BASELINE_NOT_ESTABLISHED` requires positive durable lifecycle/initialization proof；missing authority rows alone are insufficient。

All records claimed as one RecoveryCut must satisfy the verified persistence-consistency-domain requirement。

## Recovery Decision Checkpoint 5B — Strategy / Reconciliation Recovery Frontiers

Strategy recovery persistence semantics：

- minimum logical unit = StrategyInstance。
- one StrategyInstance may require one or multiple exact MarketObservation frontiers。
- algorithmic statelessness does not waive required durable consumption/causal/material-output frontier evidence。
- fresh/stateless/genesis eligibility requires positive StrategyInstance lifecycle/config authority。
- absence of StrategyStateSnapshot alone is insufficient。

Exact StrategyInstance/config/policy identity and migration authority remain R-09。

Reconciliation persistence semantics：

- one ReconciliationCase has exactly one primary BrokerAccount recovery scope。
- case lifecycle is discrepancy/control/audit authority，not AccountStateHead economic authority。
- case open/update/close alone does not advance AccountStateHead。
- economic mutation follows AccountAuthorityCommit。

Any reconciliation state/evidence used as a material R-04H readiness prerequisite is recovery-critical non-revision-advancing evidence and must be represented in the complete RecoveryCut/currentness proof。

Audit/history-only case changes with no current readiness effect need not invalidate activation。

Shared causes may affect multiple accounts，but do not create cross-account ReconciliationCase authority scope。

## Decision Checkpoint 5C — Strategy Governing Context Transition

Strategy recovery governing context may include，as applicable：

- StrategyInstance identity。
- exact StrategyDefinition / implementation revision。
- exact StrategyConfigVersion。
- canonical instrument binding。
- exact DecisionPolicyVersion。
- compatible durable strategy / decision-layer state。

A governing-context lifecycle transition has three conceptual recoverable classifications：

1. `PRE_TRANSITION` — prior governing context remains authoritative。
2. `TRANSITION_IN_PROGRESS` — an authorized durable transition has crossed its transition boundary but the target context is not yet eligible for normal trading activation。
3. `POST_TRANSITION` — new governing context and all required compatible durable state have been successfully established。

These are architectural recovery classifications；no particular enum/table representation is prescribed。

A merely planned/staged transition intent does not automatically mean TRANSITION_IN_PROGRESS；classification is determined by the durable transition/effective boundary。

`TRANSITION_IN_PROGRESS` must：

- retain exact transition provenance。
- identify authoritative pre-transition context。
- identify intended target context。
- never select a side from current deployment presence。
- never become StrategyTradingReady / DecisionCohortTradingReady。
- be explicitly resumed、completed、rolled back where contractually allowed，or otherwise resolved under authorized lifecycle semantics。

The system must never expose a successfully activated mixed governing context whose required authorities/state belong to incompatible sides of the transition。

When several governing authorities must change together to preserve one decision contract，the transition must preserve one equivalent crash invariant。

A single SQL transaction is not architecturally required，but best-effort/eventual dual-write is not equivalent。

The transition effective boundary must be durable and deterministically recoverable。

PRE_TRANSITION / POST_TRANSITION classification does not itself grant TradingReady；all normal R-06/R-04/risk/business readiness gates still apply。

## Recovery Decision Checkpoint 5D — Initialization Provenance / Time Evidence

Initialization revision 1 must resolve one unique canonical initialization AccountPositionSnapshot。

That snapshot references the exact EXPECTED_STATE_INITIALIZED event；the initialization event/authority commit resolves required upstream broker/reference/authorization provenance。

Conflicting additional canonical initialization snapshot at revision 1 is integrity failure。

BROKER_SEED is initialization-time position genesis，not fabricated historical execution。

For temporal evidence：

- received_at is immutable once first successfully durably bound to immutable evidence identity。
- retries/replays/rebuilds do not rewrite canonical received_at。
- unknown/unverified source occurrence time remains explicit。
- repositories do not silently invent domain timestamps。
- canonical timestamp values require known timezone semantics and canonical UTC representation。
- recorded_at is not durable-commit/order authority unless a separately frozen persistence contract explicitly defines another semantic。

Account revisions/checkpoints/receipts remain persistence/recovery authority；wall-clock timestamps are evidence only。
