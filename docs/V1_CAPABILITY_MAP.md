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

Engineering detail：

`V1_SYSTEM_BLUEPRINT.md`

Blueprint baseline 完成後：

每一個 capability block 必須 mapping 至一個或多個 engineering leaf。

Blueprint baseline 已啟用：

本文件的 92 capability blocks 已完成 603 engineering-leaf rebase；official progress metric 使用 lifecycle-weighted 43.46% baseline。

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

Lifecycle-weighted completion：

    43.46%

Architecture Design Coverage：

    87.23%

Design Freeze Coverage：

    51.47%

Runtime Implementation：

    38.84%

Unit Verification：

    35.61%

Integration Verification：

    35.52%

Accepted Capability：

    35.52%

Metric basis：

    603 engineering leaves / total weight 2137

Capability status：

    COMPLETE 11 / PARTIAL 49 / NOT_STARTED 32

Readiness：

    Operational NOT_READY
    Production Live BLOCKED
    LIVE_AUTO NOT_AUTHORIZED

---

## 4. Domain Summary

| Domain | Count | Estimated Completion |
|---|---:|---:|
| A Governance / Development | 4 | 70.68% |
| B Data Pipeline | 6 | 66.44% |
| C Calendar / Contract Data | 5 | 59.77% |
| D Canonical Domain | 6 | 77.25% |
| E Feature / Strategy | 7 | 50.11% |
| F Backtest / Research | 8 | 90.40% |
| G Decision / Risk | 8 | 67.86% |
| H Execution / Paper | 8 | 68.01% |
| I Broker Adapter | 6 | 63.88% |
| J Account / Reconciliation | 6 | 79.48% |
| K Persistence / Recovery | 7 | 11.58% |
| L Simulation / Live Safety | 7 | 3.66% |
| M Python Service Boundary | 4 | 12.42% |
| N ASP.NET Core Application | 5 | 11.26% |
| O React Workspace | 5 | 10.31% |
| TOTAL | 92 | 43.46% lifecycle-weighted |

---

# A — Governance / Development

| ID | Capability | Status | Remaining |
|---|---|---|---|
| A01 | Authoritative architecture/docs hierarchy | PARTIAL | Maintain |
| A02 | Work Package → tests → Git quality gate | PARTIAL | Maintain |
| A03 | Executable queue + full ACTIVE prompt | PARTIAL | Runtime validation |
| A04 | Continuous queue-driven Codex orchestration | NOT_STARTED | After 2–3 Level 3A validations |

---

# B — Data Pipeline

| ID | Capability | Status | Remaining |
|---|---|---|---|
| B01 | Multi-source market ingestion foundation | PARTIAL | Extend sources later |
| B02 | Tick/bar validation and cleaning | PARTIAL | Production QA later |
| B03 | Tick/1m/session bar aggregation | COMPLETE | More edge validation |
| B04 | Canonical Parquet analytical storage | PARTIAL | Align richer MarketBar/provenance |
| B05 | DuckDB analytical query/storage | PARTIAL | Schema/bootstrap refinement |
| B06 | Local data reproducibility/governance | PARTIAL | GAP-REPO-002 |

---

# C — Calendar / Contract Data

| ID | Capability | Status | Remaining |
|---|---|---|---|
| C01 | Trading dates/calendar | PARTIAL | Maintain |
| C02 | Day/night session resolution | PARTIAL | Consolidate duplicate rules |
| C03 | Holiday/exception handling | PARTIAL | Production completeness validation |
| C04 | Contract dates/repository/generation | PARTIAL | Multi-series refinement later |
| C05 | Continuous/listed roll resolution | PARTIAL | Full roll engine |

---

# D — Canonical Domain

| ID | Capability | Status | Remaining |
|---|---|---|---|
| D01 | InstrumentSpec | PARTIAL | Consumer migration only |
| D02 | ContractSpec | PARTIAL | Consumer migration only |
| D03 | TradingSessionRef | PARTIAL | Full timezone boundary pending |
| D04 | MarginSchedule / resolver | PARTIAL | DB/broker snapshot refinement |
| D05 | BrokerInstrumentReference | PARTIAL | Persistence/capability follow-up |
| D06 | Canonical MarketBar ownership | PARTIAL | Rich model ownership migration |

---

# E — Feature / Strategy

| ID | Capability | Status | Remaining |
|---|---|---|---|
| E01 | Batch feature modules | PARTIAL | Extend indicators as needed |
| E02 | Feature builder / registry | PARTIAL | Maintain |
| E03 | Incremental Feature / Market State | NOT_STARTED | GAP-09 |
| E04 | Strategy base / concrete strategy flow | COMPLETE | Maintain |
| E05 | StrategyDefinition / version registry | PARTIAL | StrategyInstance/config expansion |
| E06 | Multi-strategy runner | PARTIAL | Runtime operational integration later |
| E07 | strategy/ vs strategies/ ownership cleanup | PARTIAL | Opportunistic migration only |

---

# F — Backtest / Research

| ID | Capability | Status | Remaining |
|---|---|---|---|
| F01 | Deterministic next-bar BacktestEngine | COMPLETE | Preserve semantics |
| F02 | Commission/slippage/fill accounting | COMPLETE | Advanced models later |
| F03 | LONG/SHORT/SL/TP/exit lifecycle | COMPLETE | Preserve regression |
| F04 | Portfolio/equity/drawdown projection | PARTIAL | Operational account separate |
| F05 | Performance/trade statistics | PARTIAL | Final Return/Sharpe validation |
| F06 | Optimization/sensitivity/stability | PARTIAL | Scale/performance later |
| F07 | OOS/Walk-Forward | PARTIAL | More strategy coverage later |
| F08 | Monte Carlo/comparison tooling | PARTIAL | Reporting integration later |

---

# G — Decision / Risk

| ID | Capability | Status | Remaining |
|---|---|---|---|
| G01 | Strategy virtual positions | PARTIAL | Ownership migration later |
| G02 | Strategy conflict resolution | PARTIAL | Maintain |
| G03 | TargetAccountPosition | COMPLETE | Operational account consumer pending |
| G04 | Attribution/netting | PARTIAL | Persistence pending |
| G05 | Direction-change wait-for-flat | PARTIAL | Broker operational integration |
| G06 | PortfolioRiskManager | PARTIAL | Account-aware live risk |
| G07 | Position sizing/capital management | PARTIAL | Operational integration |
| G08 | Auditable RiskDecision | NOT_STARTED | Canonical model + persistence |

---

# H — Execution / Paper

| ID | Capability | Status | Remaining |
|---|---|---|---|
| H01 | Order/Fill foundation | PARTIAL | Canonical ownership migration |
| H02 | Broker submit/query/fills/cancel port | COMPLETE | Account capability separate |
| H03 | Async/partial/terminal lifecycle | PARTIAL | Expanded production states |
| H04 | PaperBroker deterministic baseline | PARTIAL | Preserve |
| H05 | PaperTradingEngine | COMPLETE | Canonical contract migration later |
| H06 | PaperTradingRunner/polling | COMPLETE | Incremental state integration |
| H07 | Explicit OrderIntent / PositionEffect | PARTIAL | Explicit semantics accepted; direction-transition operational integration remains |
| H08 | Production OMS idempotency/status model | PARTIAL | Persistence/live phases |

---

# I — Sinopac / Shioaji Adapter

| ID | Capability | Status | Remaining |
|---|---|---|---|
| I01 | Contract/native mapping | PARTIAL | Adapter relocation later |
| I02 | Submit/status/cancel | PARTIAL | Explicit PositionEffect accepted; production verification remains |
| I03 | Fill conversion/dedup/partial fill | PARTIAL | Production verification |
| I04 | BrokerInstrumentReference seam | PARTIAL | Persistence later |
| I05 | Broker account/position snapshot | PARTIAL | Canonical mapping foundation accepted; real provider/paper verification pending |
| I06 | Broker capability matrix | NOT_STARTED | GAP-BROKER-002 |

---

# J — Account / Reconciliation

| ID | Capability | Status | Remaining |
|---|---|---|---|
| J01 | LogicalAccount | NOT_STARTED | Canonical account model |
| J02 | BrokerAccount | PARTIAL | BrokerAccount foundation accepted; logical mapping/account snapshot pending |
| J03 | Internal AccountPosition | PARTIAL | Canonical expected model accepted; fill/event projection and legacy migration pending |
| J04 | BrokerPositionSnapshot | PARTIAL | BrokerPositionSnapshot foundation accepted; real provider/startup observation pending |
| J05 | ReconciliationResult / policies | COMPLETE | Pairwise comparison、policy/case 與 deterministic collection reconciliation accepted |
| J06 | Startup sync / readiness gate | COMPLETE | Startup orchestration/readiness accepted; persistence/recovery backend remains K Domain |

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
| L06 | Secrets/operational authorization/audit | NOT_STARTED | Application/security phase |
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
