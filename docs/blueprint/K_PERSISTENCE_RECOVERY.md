# K — Persistence / Recovery

## Status

BUILDING / PROVISIONAL until Blueprint baseline acceptance。

---

## Domain Purpose

建立 PostgreSQL operational System of Record、append-only trading evidence、snapshots、idempotency、decision provenance 與 deterministic restart recovery。

Operational SOR：

    PostgreSQL

Historical analytical data：

    Parquet / DuckDB

不得互換 authority。

Target ownership：

    persistence/
        postgres/

---

## Capability Groups

| Group | Name | Responsibility |
|---|---|---|
| K100 | PostgreSQL Operational SOR | schema / types / migrations / transaction boundary |
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
| K110 | PostgreSQL SOR Boundary | PostgreSQL 是 operational trading truth persistence | DESIGN_FROZEN | 5 | K01 |
| K120 | Schema Versioning / Migration | DB schema change 必須 versioned / reviewable | DESIGNED | 4 | K01 |
| K130 | Operational Numeric Types | money/price/margin 使用 NUMERIC-compatible exact semantics | DESIGN_FROZEN | 4 | K01 |
| K140 | Operational Time Types | event / observation timestamps 使用 TIMESTAMPTZ | DESIGN_FROZEN | 4 | K01 |
| K150 | Stable Identifier Types | signal/decision/order/fill/trade/account IDs 不依 display text | DESIGNED | 4 | K01 |
| K160 | Transaction Boundary | related state/event writes 有明確 transaction semantics | DESIGNED | 5 | K01 |
| K170 | DB Documentation | important table/column/function 使用繁體中文 COMMENT | DESIGN_FROZEN | 2 | K01 |
| K210 | Repository Port Boundary | trading/domain 不直接依賴 PostgreSQL ORM/driver | DESIGN_FROZEN | 4 | K01 |
| K220 | Append Repository Contract | event/evidence insert 與 mutable projection update 分離 | DESIGNED | 4 | K01,K05 |
| K230 | Snapshot Repository Contract | latest / as-of snapshot query semantics | DESIGNED | 4 | K03 |
| K240 | Unit-of-Work Boundary | multi-write use case consistency contract | DESIGNED | 4 | K01 |
| K310 | Order Persistence | internal/broker order identity、status、intent linkage | DESIGNED | 4 | K02 |
| K320 | OrderEvent Persistence | append-only order lifecycle event | DESIGNED | 5 | K02,K05 |
| K330 | Fill Persistence | actual fill evidence durable storage | DESIGNED | 5 | K02 |
| K340 | Execution Correlation | intent → order → event → fill correlation/causation | DESIGNED | 4 | K02,K04 |
| K350 | Broker External ID Persistence | broker order/trade/deal identity 明確保存 | DESIGNED | 4 | K02 |
| K410 | AccountPositionSnapshot Persistence | internal expected state snapshot | DESIGNED | 4 | K03 |
| K420 | BrokerPositionSnapshot Persistence | broker actual observation history | DESIGNED | 4 | K03 |
| K430 | AccountSnapshot Persistence | cash/equity/margin/position observation | DESIGNED | 4 | K03 |
| K440 | ReconciliationCase Persistence | mismatch / evidence / resolution lifecycle | DESIGNED | 5 | K03,K07 |
| K450 | Expected / Actual Separation in Schema | expected 與 actual 不共用可 silent overwrite row | DESIGN_FROZEN | 5 | K03 |
| K510 | StrategyStateSnapshot | restart-required strategy state | DESIGNED | 4 | K06 |
| K520 | Incremental Feature State Snapshot | GAP-09 state 可 persistence/reconstruct | DESIGNED | 4 | K06 |
| K530 | Strategy Config / Version Link | state 可連 strategy/config version | DESIGNED | 3 | K06 |
| K540 | Safe Snapshot Boundary | snapshot 只在一致 state boundary 保存 | DESIGNED | 4 | K06 |
| K610 | Trading Event Ledger | append-only material trading event history | DESIGNED | 5 | K05 |
| K620 | Event ID | globally/stably unique event identity | DESIGNED | 3 | K05 |
| K630 | Occurred / Received Time | event occurrence 與接收時間分離 | DESIGNED | 4 | K05 |
| K640 | Event Sequence | source/entity ordering 可檢查 | DESIGNED | 4 | K05 |
| K650 | Event Version | event schema/version 可演進 | DESIGNED | 3 | K05 |
| K660 | Idempotency Key | duplicate request/event 可安全辨識 | DESIGNED | 5 | K05 |
| K670 | Correlation / Causation IDs | material workflow 可完整 trace | DESIGNED | 4 | K04,K05 |
| K680 | No Silent Event Mutation | historical execution evidence 不以 update 覆蓋原事件 | DESIGN_FROZEN | 5 | K05 |
| K710 | Recovery State Load | process start 載入 persisted expected / execution / strategy state | DESIGNED | 5 | K07 |
| K720 | Broker Actual Query Dependency | recovery 必須取得 broker actual observation | DESIGNED | 5 | K07 |
| K730 | Recovery Reconciliation | persisted expected vs actual broker state | DESIGNED | 5 | K07 |
| K740 | Strategy Reconstruction | account/reconciliation safe 後 reconstruct strategy state | DESIGNED | 5 | K06,K07 |
| K750 | Recovery Validation | identity / sequence / config / state consistency verification | DESIGNED | 5 | K07 |
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

## Core Persistent Entities

至少包含：

- TradingSession。
- TradingDecision。
- DecisionContext。
- RiskDecision。
- Order。
- OrderEvent。
- Fill。
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

- PostgreSQL：operational SOR。
- OrderEvent / Fill：execution evidence。
- AccountPositionSnapshot：internal expected projection history。
- BrokerPositionSnapshot：actual broker observation history。
- StrategyStateSnapshot：restart projection，不取代 strategy/config definition。
- DuckDB：research/analytical，不是 operational SOR。
- Parquet：historical/feature dataset，不是 operational SOR。

---

## Key Invariants

- operational money/price 使用 exact NUMERIC-compatible representation。
- operational timestamp 使用 TIMESTAMPTZ。
- append-only evidence 不 silent overwrite。
- event 與 snapshot responsibility 分離。
- recovery 不只依賴 TradeRecord。
- broker actual 不 silent overwrite expected state。
- domain/trading 不直接依賴 DB ORM。
- idempotency 必須 persistence-aware。
- schema migration 不可 destructive silent change。

---

## Sources

- SRC-POSTGRES-001。
- SRC-ADR-001。
- SRC-ARCH-001。

PostgreSQL implementation 前必須 pin project major version，再把 source registry 從 generic official docs 收斂到 pinned version。

---

## Current GAP Mapping

- K100-K770 → GAP-08。
- K810-K850 → GAP-PERSIST-001。
- K520 → GAP-09 persistence dependency。
- K910-K930 → V1 integration / operational readiness。

---

## Domain Acceptance

- K01～K07 全部有 leaf mapping。
- SOR / event / snapshot / provenance / recovery responsibility 分離。
- PostgreSQL 與 DuckDB/Parquet authority 不混淆。
- recovery flow 與 J startup readiness 對齊。
