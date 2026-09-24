# Connection Matrix

## Status

AUTHORITATIVE
---

## 1. Primary Runtime Flow

| From | To | Contract / State | Rule |
|---|---|---|---|
| B Data Pipeline | D Canonical Domain | Market observation | External/raw data becomes canonical observation |
| C Calendar / Contract | D Canonical Domain | Session / contract reference | Domain uses canonical calendar/specification reference |
| D Canonical Domain | E Feature / Strategy | Market observation | Strategy never consumes broker native object |
| E Feature / Strategy | G Decision / Risk | StrategyIntent | Strategy does not directly decide physical account position |
| G Decision / Risk | H Execution / OMS | Risk-approved target/action | Execution must not bypass RiskDecision |
| H Execution / OMS | I Broker Adapter | Broker-neutral OrderIntent | Adapter owns native SDK mapping |
| I Broker Adapter | H Execution / OMS | OrderEvent / Fill | Native result mapped back to canonical execution event |
| H Execution / OMS | J Account | execution result | Fill/event updates internal expected account projection |
| I Broker Adapter | J Account | BrokerPositionSnapshot | Broker actual observation remains distinct |
| J Account | J Reconciliation | expected + actual | Pure comparison before policy/action |
| J Reconciliation | K Persistence / Recovery | result/case/readiness | Persist mismatch and recovery evidence |
| J Reconciliation | L Simulation / Live Safety | reconciliation health | Live guards consume readiness |
| K Persistence / Recovery | M Python Service | operational state | Service accesses through application/use-case boundary |
| M Python Service | N ASP.NET Core | versioned REST/JSON DTO | Domain objects are not wire DTOs |
| N ASP.NET Core | O React | HTTP / realtime DTO | React never talks directly to Python core/DB/broker |

---

## 2. Research Flow

    Raw / External Data
    → Validation
    → Cleaning
    → Aggregation
    → Canonical Historical Storage
    → Feature
    → Strategy
    → Backtest
    → Analysis
    → Optimization / OOS / WFO / Monte Carlo

Research pipeline：

可以使用 float。

Operational trading：

依 architecture boundary 使用 Decimal / explicit identifiers / timezone-aware timestamps。

---

## 3. Forbidden Dependency Directions

| Forbidden | Reason |
|---|---|
| `domain -> backtest` | Canonical domain 不能依賴 historical consumer |
| `trading -> backtest` | Trading core 不能依賴 simulation consumer |
| `trading -> adapters` | Core 不能依賴 broker implementation |
| `trading -> sj.*` | Broker SDK 不得洩漏 core |
| `trading -> PostgreSQL ORM` | Domain model != persistence entity |
| `backtest -> Shioaji network` | Deterministic historical runtime 不碰 live broker |
| `React -> PostgreSQL` | UI only through application API |
| `React -> Shioaji` | UI cannot access broker SDK |
| `ASP.NET -> Shioaji SDK` | Broker-native integration remains Python adapter boundary |
| `ASP.NET -> Python class import` | Cross-language boundary uses versioned DTO |

---

## 4. Direction Change

    LONG
    → EXIT
    → confirm FLAT
    → re-evaluate
    → ENTER SHORT

以及反方向相同。

任何 layer 不得 silent direct reversal。

---

## 5. Expected / Actual Flow

Expected：

    StrategyPosition
    → TargetAccountPosition
    → AccountPosition

Actual：

    Broker
    → BrokerPositionSnapshot

Comparison：

    AccountPosition
    + BrokerPositionSnapshot
    → Reconciliation

Broker actual：

不得直接 overwrite expected state。
