# V1 Capability Map

## 1. Purpose

AUTHORITATIVE V1 FUNCTION INVENTORY

本文件回答：

- V1 有哪些功能。
- 哪些完成。
- 哪些部分完成。
- 哪些尚未開始。
- 哪些是 Live blocker。
- Overall progress 如何計算。

GAP Register 記錄問題。

Capability Map 記錄產品與平台能力。

---

## 2. Status

- COMPLETE：已有 implementation 且主要 acceptance/regression 已通過。
- PARTIAL：已有 foundation，但 V1 acceptance 尚未完整。
- NOT_STARTED：尚未實作。
- DEFERRED：明確移至 Post-V1。
- LIVE_BLOCKER：未完成前不可 production live。

---

## 3. Progress Method

完成百分比不直接使用：

- LOC。
- file count。
- test count。

目前使用：

capability acceptance + relative engineering weight。

Provisional V1 weighted completion：

    45–52%

Center estimate：

    約 49%

Confidence：

    Medium-Low

下一次重新估算：

    GAP-ACCOUNT-001 + Reconciliation foundation 完成後

---

## 4. Domain Summary

| Domain | Count | Estimated Completion |
|---|---:|---:|
| A Governance / Development | 4 | ~75% |
| B Data Pipeline | 6 | ~80% |
| C Calendar / Contract Data | 5 | ~70% |
| D Canonical Domain | 6 | ~85% |
| E Feature / Strategy | 7 | ~70% |
| F Backtest / Research | 8 | ~85% |
| G Decision / Risk | 8 | ~80% |
| H Execution / Paper | 8 | ~70% |
| I Broker Adapter | 6 | ~55% |
| J Account / Reconciliation | 6 | ~10% |
| K Persistence / Recovery | 7 | ~5% |
| L Simulation / Live Safety | 7 | ~15% |
| M Python Service Boundary | 4 | ~0% |
| N ASP.NET Core Application | 5 | ~0% |
| O React Workspace | 5 | ~0% |
| TOTAL | 92 | 45–52% weighted |

---

# A — Governance / Development

| ID | Capability | Status | Remaining |
|---|---|---|---|
| A01 | Authoritative architecture/docs hierarchy | COMPLETE | Maintain |
| A02 | Work Package → tests → Git quality gate | COMPLETE | Maintain |
| A03 | Executable queue + full ACTIVE prompt | PARTIAL | Runtime validation |
| A04 | Continuous queue-driven Codex orchestration | NOT_STARTED | After 2–3 Level 3A validations |

---

# B — Data Pipeline

| ID | Capability | Status | Remaining |
|---|---|---|---|
| B01 | Multi-source market ingestion foundation | COMPLETE | Extend sources later |
| B02 | Tick/bar validation and cleaning | COMPLETE | Production QA later |
| B03 | Tick/1m/session bar aggregation | COMPLETE | More edge validation |
| B04 | Canonical Parquet analytical storage | PARTIAL | Align richer MarketBar/provenance |
| B05 | DuckDB analytical query/storage | PARTIAL | Schema/bootstrap refinement |
| B06 | Local data reproducibility/governance | PARTIAL | GAP-REPO-002 |

---

# C — Calendar / Contract Data

| ID | Capability | Status | Remaining |
|---|---|---|---|
| C01 | Trading dates/calendar | COMPLETE | Maintain |
| C02 | Day/night session resolution | COMPLETE | Consolidate duplicate rules |
| C03 | Holiday/exception handling | PARTIAL | Production completeness validation |
| C04 | Contract dates/repository/generation | COMPLETE | Multi-series refinement later |
| C05 | Continuous/listed roll resolution | PARTIAL | Full roll engine |

---

# D — Canonical Domain

| ID | Capability | Status | Remaining |
|---|---|---|---|
| D01 | InstrumentSpec | COMPLETE | Consumer migration only |
| D02 | ContractSpec | COMPLETE | Consumer migration only |
| D03 | TradingSessionRef | COMPLETE | Full timezone boundary pending |
| D04 | MarginSchedule / resolver | COMPLETE | DB/broker snapshot refinement |
| D05 | BrokerInstrumentReference | COMPLETE | Persistence/capability follow-up |
| D06 | Canonical MarketBar ownership | PARTIAL | Rich model ownership migration |

---

# E — Feature / Strategy

| ID | Capability | Status | Remaining |
|---|---|---|---|
| E01 | Batch feature modules | COMPLETE | Extend indicators as needed |
| E02 | Feature builder / registry | COMPLETE | Maintain |
| E03 | Incremental Feature / Market State | NOT_STARTED | GAP-09 |
| E04 | Strategy base / concrete strategy flow | COMPLETE | Maintain |
| E05 | StrategyDefinition / version registry | COMPLETE | StrategyInstance/config expansion |
| E06 | Multi-strategy runner | COMPLETE | Runtime operational integration later |
| E07 | strategy/ vs strategies/ ownership cleanup | PARTIAL | Opportunistic migration only |

---

# F — Backtest / Research

| ID | Capability | Status | Remaining |
|---|---|---|---|
| F01 | Deterministic next-bar BacktestEngine | COMPLETE | Preserve semantics |
| F02 | Commission/slippage/fill accounting | COMPLETE | Advanced models later |
| F03 | LONG/SHORT/SL/TP/exit lifecycle | COMPLETE | Preserve regression |
| F04 | Portfolio/equity/drawdown projection | COMPLETE | Operational account separate |
| F05 | Performance/trade statistics | PARTIAL | Final Return/Sharpe validation |
| F06 | Optimization/sensitivity/stability | COMPLETE | Scale/performance later |
| F07 | OOS/Walk-Forward | COMPLETE | More strategy coverage later |
| F08 | Monte Carlo/comparison tooling | COMPLETE | Reporting integration later |

---

# G — Decision / Risk

| ID | Capability | Status | Remaining |
|---|---|---|---|
| G01 | Strategy virtual positions | COMPLETE | Ownership migration later |
| G02 | Strategy conflict resolution | COMPLETE | Maintain |
| G03 | TargetAccountPosition | COMPLETE | Operational account consumer pending |
| G04 | Attribution/netting | COMPLETE | Persistence pending |
| G05 | Direction-change wait-for-flat | COMPLETE | Broker operational integration |
| G06 | PortfolioRiskManager | COMPLETE | Account-aware live risk |
| G07 | Position sizing/capital management | COMPLETE | Operational integration |
| G08 | Auditable RiskDecision | PARTIAL | Canonical model + persistence |

---

# H — Execution / Paper

| ID | Capability | Status | Remaining |
|---|---|---|---|
| H01 | Order/Fill foundation | COMPLETE | Canonical ownership migration |
| H02 | Broker submit/query/fills/cancel port | COMPLETE | Account capability separate |
| H03 | Async/partial/terminal lifecycle | COMPLETE | Expanded production states |
| H04 | PaperBroker deterministic baseline | COMPLETE | Preserve |
| H05 | PaperTradingEngine | COMPLETE | Canonical contract migration later |
| H06 | PaperTradingRunner/polling | COMPLETE | Incremental state integration |
| H07 | Explicit OrderIntent / PositionEffect | NOT_STARTED | GAP-BROKER-001 |
| H08 | Production OMS idempotency/status model | PARTIAL | Persistence/live phases |

---

# I — Sinopac / Shioaji Adapter

| ID | Capability | Status | Remaining |
|---|---|---|---|
| I01 | Contract/native mapping | COMPLETE | Adapter relocation later |
| I02 | Submit/status/cancel | COMPLETE | Explicit PositionEffect |
| I03 | Fill conversion/dedup/partial fill | COMPLETE | Production verification |
| I04 | BrokerInstrumentReference seam | COMPLETE | Persistence later |
| I05 | Broker account/position snapshot | NOT_STARTED | GAP-ACCOUNT-001 |
| I06 | Broker capability matrix | NOT_STARTED | GAP-BROKER-002 |

---

# J — Account / Reconciliation

| ID | Capability | Status | Remaining |
|---|---|---|---|
| J01 | LogicalAccount | NOT_STARTED | Canonical account model |
| J02 | BrokerAccount | NOT_STARTED | Canonical broker model |
| J03 | Internal AccountPosition | PARTIAL | Existing minimal model insufficient |
| J04 | BrokerPositionSnapshot | NOT_STARTED | Adapter observation model |
| J05 | ReconciliationResult / policies | NOT_STARTED | Comparison + mismatch classification |
| J06 | Startup sync / readiness gate | NOT_STARTED | Required before live |

---

# K — Persistence / Recovery

| ID | Capability | Status | Remaining |
|---|---|---|---|
| K01 | PostgreSQL operational SOR | NOT_STARTED | Schema + adapter |
| K02 | Order/OrderEvent/Fill persistence | NOT_STARTED | GAP-08 |
| K03 | Position/account snapshots | NOT_STARTED | GAP-08 |
| K04 | Decision/Risk provenance persistence | NOT_STARTED | GAP-PERSIST-001 |
| K05 | Trading event ledger/idempotency | NOT_STARTED | GAP-08 |
| K06 | Strategy state snapshot | NOT_STARTED | Recovery |
| K07 | Restart recovery + broker reconciliation | NOT_STARTED | GAP-08 |

---

# L — Simulation / Live Safety

| ID | Capability | Status | Remaining |
|---|---|---|---|
| L01 | SimulationBroker fault model | NOT_STARTED | GAP-SIM-001 |
| L02 | Trading mode contract | PARTIAL | Runtime orchestration |
| L03 | LIVE authorization gate | NOT_STARTED | GAP-LIVE-001 |
| L04 | Manual override/force-flat/kill switch | NOT_STARTED | GAP-LIVE-001 |
| L05 | Runtime stale/reconciliation/risk guards | NOT_STARTED | GAP-LIVE-001 |
| L06 | Secrets/operational authorization/audit | PARTIAL | Application/security phase |
| L07 | Production verification matrix | NOT_STARTED | Pre-live gate |

---

# M — Python Service Boundary

| ID | Capability | Status | Remaining |
|---|---|---|---|
| M01 | Versioned REST/JSON Python service | NOT_STARTED | Service host |
| M02 | Domain → wire DTO mapping | NOT_STARTED | Contracts |
| M03 | Research/backtest job API | NOT_STARTED | Application boundary |
| M04 | Trading/account/risk API | NOT_STARTED | Operational core dependency |

---

# N — ASP.NET Core Application

| ID | Capability | Status | Remaining |
|---|---|---|---|
| N01 | ASP.NET Core solution/projects | NOT_STARTED | Scaffold |
| N02 | Application use cases/workflow | NOT_STARTED | Orchestration |
| N03 | Authentication/authorization | NOT_STARTED | Security |
| N04 | Operational API/realtime | NOT_STARTED | HTTP + SignalR |
| N05 | Config/approval/broker orchestration | NOT_STARTED | V1 workflow |

---

# O — React Workspace

| ID | Capability | Status | Remaining |
|---|---|---|---|
| O01 | App shell/navigation/layout | NOT_STARTED | React foundation |
| O02 | Research/backtest workspace | NOT_STARTED | API dependency |
| O03 | Strategy/parameter workspace | NOT_STARTED | API dependency |
| O04 | Account/order/position/risk/live workspace | NOT_STARTED | Operational API |
| O05 | Review/audit/system-status workspace | NOT_STARTED | Persistence/review |

---

# 5. Mainline Remaining

主要 engineering weight：

    Account / Position Sync
    → OrderIntent / PositionEffect
    → Reconciliation
    → Persistence / Recovery / Provenance
    → Incremental Feature / Market State
    → Simulation / Live Safety
    → Python Service Boundary
    → ASP.NET Core
    → React Workspace
    → Full V1 Integration

---

# 6. Production Live Blockers

Production live 前至少：

- GAP-BROKER-001。
- GAP-ACCOUNT-001。
- Reconciliation。
- GAP-08。
- material provenance。
- GAP-07-TIME-001。
- GAP-07-SESSION-EXPIRY。
- critical SimulationBroker validation。
- GAP-LIVE-001。
- broker capability/verification matrix。

---

# 7. Post-V1 Deferred

不計入 V1 weighted completion：

- full multi-asset coverage。
- additional brokers。
- mature ML/AI。
- News Intelligence。
- GIS/property。
- mobile。
- Kafka/RabbitMQ。
- microservices。
- advanced drawing engine。
