# System Architecture

## 1. Status

AUTHORITATIVE

Architecture baseline date：

2026-09-24

Repository baseline：

master@771f10f

Recorded full regression：

745 passed

ADR-001：

ACCEPTED。

本文件描述 V1 及可延伸至 Post-V1 的完整系統架構。

---

# 2. Product Goal

建立 futures-first、broker-neutral、可逐步演進為完整個人投資平台的系統。

V1 包含：

- Taiwan futures historical data。
- data validation / cleaning。
- trading calendar。
- feature engine。
- strategy framework。
- backtest。
- optimization / OOS / WFO / Monte Carlo。
- multi-strategy decision。
- position sizing / portfolio risk。
- paper / simulation。
- Sinopac Shioaji adapter。
- broker account / position synchronization。
- reconciliation。
- trading state persistence。
- restart recovery。
- incremental feature / market state。
- live safety control。
- Python service boundary。
- ASP.NET Core application。
- React Web Workspace。
- audit / review。

Post-V1 才考慮：

- full multi-asset product coverage。
- additional brokers。
- mature ML / AI。
- News Intelligence。
- GIS / property。
- mobile。
- distributed event infrastructure。
- microservices。
- full drawing engine。

Architecture 不得阻塞 Post-V1 extension。

---

# 3. Technology Responsibility

## 3.1 Python

負責：

- ingestion。
- validation。
- cleaning。
- aggregation。
- calendar。
- domain。
- features。
- strategies。
- backtest。
- research。
- optimization。
- simulation。
- trading core。
- risk calculations。
- broker adapters。
- Python service API。

## 3.2 ASP.NET Core

未來負責：

- application use cases。
- workflow。
- authentication。
- authorization。
- approval gate。
- broker/account orchestration。
- operational API。
- realtime API。
- system administration。
- configuration workflow。
- React BFF/API。

## 3.3 React + TypeScript

未來負責：

- main investment workspace。
- research/backtest UI。
- strategy/config UI。
- account/order/position UI。
- risk/live controls。
- audit/review UI。
- system status。

## 3.4 PostgreSQL + PostGIS

未來負責：

- operational System of Record。
- trading state。
- audit state。
- authorization/configuration。
- GIS extension。

## 3.5 Parquet

負責：

- historical market data。
- feature dataset。
- analytical dataset。
- future ML dataset。

## 3.6 DuckDB

負責：

- local analytical query。
- research metadata。
- analytical validation。

不得作為 future live operational SOR。

---

# 4. High-Level Architecture

    React Workspace
            |
            | HTTPS / WebSocket
            v
    ASP.NET Core Application
            |
            | Versioned REST / JSON
            v
    Python Quant / Trading Service
            |
            +-----------------------------+
            |                             |
            v                             v
    Research / Backtest             Trading Core
            |                             |
            v                             v
    Data / Features               Persistence Ports
            |                             |
            v                             v
    Parquet / DuckDB               PostgreSQL SOR

                                            |
                                            v
                                     Broker Adapter
                                            |
                                            v
                                      Sinopac/Shioaji

---

# 5. Authoritative Trading Flow

    Market Data
    → Canonical Market Observation
    → Feature / Incremental Market State
    → Strategy
    → Strategy Intent
    → Strategy Virtual Position
    → Multi-Strategy Decision Layer
    → Target Account Position
    → Portfolio / Risk
    → Risk Decision
    → Order Intent / OMS
    → Broker Adapter
    → Broker
    → Fill / Order Event
    → Internal Account Position
    → Broker Position Snapshot
    → Reconciliation
    → Persistence / Recovery
    → Review / Audit

---

# 6. State Identity Invariants

必須永遠區分：

    StrategyPosition
    != TargetAccountPosition
    != AccountPosition
    != BrokerPositionSnapshot

## StrategyPosition

某一 StrategyInstance 的 logical position。

不是 physical broker position。

## TargetAccountPosition

Multi-Strategy Decision Layer 對 account physical exposure 的期望 target。

## AccountPosition

系統 internal expected consolidated position。

## BrokerPositionSnapshot

broker API 回報的 actual observation。

BrokerPositionSnapshot：

不得 silent overwrite AccountPosition。

---

# 7. Direction Change Invariant

LONG → SHORT：

    EXIT LONG
    → confirm FLAT
    → re-evaluate strategies/risk
    → ENTER SHORT

SHORT → LONG：

    EXIT SHORT
    → confirm FLAT
    → re-evaluate strategies/risk
    → ENTER LONG

禁止 silent direct reversal。

---

# 8. Target Python Package Architecture

Target ownership：

    domain/
        instruments
        contracts
        margins
        trading_session
        market observation
        broker-neutral market identity

    strategy/
        StrategyDefinition
        StrategyInstance specification
        strategy contracts
        registry
        runner

    strategies/
        concrete implementations

    trading/
        decision/
            StrategyIntent
            StrategyPosition
            TargetAccountPosition
            TradingDecision
            DecisionContext
            attribution

        execution/
            Order
            OrderEvent
            Fill
            OrderStatus
            OrderIntent
            PositionEffect
            Broker port
            OMS contracts

        account/
            LogicalAccount
            BrokerAccount
            AccountPosition
            BrokerPositionSnapshot
            AccountSnapshot
            TradeRecord

        risk/
            PositionSizing
            CapitalManagement
            RiskDecision
            PreTradeRisk
            RuntimeRisk

        reconciliation/
            ReconciliationResult
            ReconciliationCase
            ReconciliationPolicy

    backtest/
        deterministic replay
        historical clock
        next-bar semantics
        execution simulation
        cost/slippage
        historical portfolio
        backtest reports

    simulation/
        SimulationBroker
        latency model
        partial-fill model
        reject/cancel/disconnect model

    adapters/
        sinopac/
            Shioaji API adapter
            native contract mapping
            enum mapping
            order mapping
            account/position mapping

    persistence/
        postgres/
            trading repositories
            event/audit repositories

    service/
        versioned REST/JSON Python API

    apps/
        server/
            ASP.NET Core solution

        web/
            React + TypeScript workspace

這是 target ownership。

禁止 big-bang migration。

---

# 9. Current Physical Repository

目前 tracked Python architecture 主要：

    aggregation/
    analysis/
    backtest/
    cleaning/
    cli/
    domain/
    features/
    ingestion/
    storage/
    strategy/
    strategies/
    trading_calendar/
    scripts/
    tests/

目前大量 trading runtime model 歷史性存在：

    backtest/

這是 migration state。

不代表 backtest 是未來 live trading canonical owner。

---

# 10. Data Subsystem

## 10.1 Ingestion

Current：

    ingestion/

責任：

- source request。
- TXF / MXF / TWII source。
- Yahoo。
- GitHub historical source。
- source metadata。
- raw validation。

## 10.2 Cleaning

Current：

    cleaning/

責任：

- tick cleaning。
- bar cleaning。
- structural validation。

## 10.3 Aggregation

Current：

    aggregation/

責任：

- tick → 1m。
- generic resample。
- session-aware aggregation。
- 5m。
- 15m。
- 30m。
- 60m。

## 10.4 Analytical Storage

Current：

    storage/

責任：

- canonical Parquet。
- DuckDB connection。
- analytical storage。

## 10.5 Authority

Historical data：

Parquet。

Analytical query：

DuckDB。

Operational trading state：

future PostgreSQL。

---

# 11. Trading Calendar Subsystem

Current：

    trading_calendar/

責任：

- trading date。
- day/night session。
- holidays。
- exceptions。
- contract dates。
- instrument repository。
- contract repository。
- session resolver。
- session normalizer。

Canonical interval：

    [open, close)

Known remaining：

- timezone-aware inbound boundary。
- session rule duplication consolidation。
- expiry-day special session consolidation。
- full continuous/listed roll engine。

---

# 12. Canonical Domain

Current：

    domain/

已建立：

- InstrumentSpec。
- ContractSpec。
- TradingSessionRef。
- MarginScheduleEntry。
- MarginScheduleResolver。
- BrokerInstrumentReference。
- legacy compatibility models。

Canonical futures symbols：

- TX。
- MTX。
- TMF。

Canonical symbol 不等於：

- dataset alias。
- broker product code。
- broker contract code。
- continuous contract symbol。

---

# 13. Feature Subsystem

Current：

    features/

包含：

- price。
- trend。
- momentum。
- volatility。
- volume。
- technical。
- basis。
- rolling。
- registry。
- builder。

目前主要為 batch historical feature。

Remaining V1：

Incremental Feature / Market State Engine。

Paper / live 不應每根 bar 重掃全部 historical frame。

---

# 14. Strategy Subsystem

Current：

    strategy/
    strategies/

Target responsibility：

## strategy/

- StrategyDefinition。
- StrategyInstance specification。
- strategy contracts。
- versioning。
- registry。
- runners。

## strategies/

- concrete implementations。

目前存在 registry / contract duplication。

屬漸進 migration。

不得為 cleanup 阻塞 mainline。

---

# 15. Backtest Subsystem

Current：

    backtest/

成熟並受 regression 保護：

- deterministic sequential replay。
- next-bar execution。
- LONG。
- SHORT。
- SL。
- TP。
- intrabar priority。
- signal exit。
- end-of-data exit。
- commission。
- slippage。
- actual fill accounting。
- risk integration。
- sizing integration。
- canonical multiplier resolution。
- canonical margin resolution。

Backtest 長期只負責 historical deterministic simulation consumer。

不應擁有：

- live broker account truth。
- broker actual position。
- operational persistence。
- live reconciliation。

---

# 16. Research / Validation Subsystem

Current：

    analysis/
    backtest/

已有：

- equity。
- drawdown。
- trade statistics。
- performance report。
- optimization。
- sensitivity。
- parameter stability。
- OOS。
- Walk-Forward。
- Monte Carlo。
- sizing comparison。

Remaining：

- final Return semantics validation。
- final Sharpe semantics validation。
- operational review integration。

---

# 17. Multi-Strategy Decision Subsystem

目前多數 implementation 歷史性位於：

    backtest/

已完成 foundation：

- strategy virtual position。
- conflict resolver。
- strategy priority。
- target account position。
- attribution。
- netting。
- HOLD。
- ADD。
- REDUCE。
- EXIT。
- ENTER。
- direction-change waiting-for-flat lifecycle。

Strategy 不直接決定 broker physical position。

---

# 18. Risk / Capital Subsystem

目前：

    backtest/risk.py
    backtest/*sizing*
    backtest/*capital*

已有：

- initial margin。
- maintenance margin。
- max contracts。
- max margin utilization。
- forced liquidation。
- Fixed Quantity。
- Fixed Amount。
- Fixed Risk。
- Stop-Based Risk。
- Per-Contract Risk。
- Fixed Ratio。
- Moving Peak。
- Moving Average。
- Previous Period。
- Capital Protection。

Remaining：

- canonical RiskDecision。
- account-aware live exposure。
- runtime risk。
- persistence / provenance。

---

# 19. Execution / OMS Subsystem

Current foundation：

- Order。
- Fill。
- OrderStatus。
- Broker ABC。
- submit。
- get order。
- get fills。
- cancel。
- partial fills。
- async lifecycle。
- terminal cancellation。
- terminal rejection。

Critical remaining：

    OrderIntent
    PositionEffect

目前 Shioaji adapter 仍存在：

    order_id.startswith("ENTRY-")

推定 New / Cover。

此行為必須由 explicit execution semantics 取代。

Target order state：

- PENDING_SUBMIT。
- SUBMITTED。
- PARTIALLY_FILLED。
- FILLED。
- PENDING_CANCEL。
- CANCELLED。
- REJECTED。
- EXPIRED。
- UNKNOWN。

External action 必須 idempotent。

Retry 前必須先 reconciliation。

---

# 20. Paper / Simulation

## PaperBroker

Simple deterministic immediate-fill baseline。

用途：

- unit test。
- deterministic baseline。

不是 realistic simulator。

## PaperTradingEngine

負責：

- pending order。
- fill application。
- PositionManager。
- Portfolio。
- Risk。

## PaperTradingRunner

負責：

- polling。
- market data。
- strategy。
- paper orchestration。

## SimulationBroker

Future V1：

- latency。
- partial fill。
- reject。
- cancel。
- disconnect。
- stale status。
- delayed status。
- fault injection。

SimulationBroker 與 PaperBroker 分離。

---

# 21. Sinopac / Shioaji Adapter

Current historical location：

    backtest/shioaji_*

Target：

    adapters/sinopac/

Adapter 擁有：

- `sj.*`。
- native contract。
- native enum。
- API calls。
- Shioaji order/trade object。
- broker external IDs。
- deal-sequence dedup。
- broker account mapping。
- broker position mapping。

Core 禁止依賴 `sj.*`。

Current foundation：

- contract resolution。
- order submission。
- status synchronization。
- cancellation。
- fill conversion。
- fill deduplication。
- partial fill。
- BrokerInstrumentReference seam。

Missing：

- broker account snapshot。
- broker position snapshot。
- capability matrix。
- production connection/session lifecycle。
- explicit PositionEffect mapping。
- production verification。

---

# 22. Account Subsystem

Target：

    trading/account

需要：

## LogicalAccount

內部 capital allocation / strategy allocation。

## BrokerAccount

實體 broker account identity / configuration reference。

不得保存 secret 或 native SDK object。

## AccountPosition

internal expected consolidated physical position。

## BrokerPositionSnapshot

broker 回報 actual observation。

## AccountSnapshot

future：

- cash。
- equity。
- margin。
- positions。
- observed time。

Current：

只有 minimal AccountPosition foundation。

Operational account model 尚未完成。

---

# 23. Reconciliation Subsystem

Target：

    trading/reconciliation

Inputs：

- persisted expected state。
- internal runtime state。
- broker actual snapshot。

至少輸出：

- MATCH。
- INTERNAL_ONLY。
- BROKER_ONLY。
- DIRECTION_MISMATCH。
- QUANTITY_MISMATCH。
- CONTRACT_MISMATCH。
- UNKNOWN_EXTERNAL_STATE。

Policies：

- STRICT_HALT。
- BROKER_AUTHORITATIVE。
- INTERNAL_AUTHORITATIVE。
- MANUAL_REVIEW。

V1 startup 預設應偏向：

- STRICT_HALT。
- MANUAL_REVIEW。

禁止 silent overwrite。

---

# 24. Account Sync / OrderIntent Sequencing

ADR migration sequence要求 explicit execution semantics。

目前 mainline 又需要先建立 Account Sync foundation。

正式規則：

## 可以先做

Read-only：

- BrokerAccount。
- BrokerPositionSnapshot。
- broker account query port。
- broker position query port。
- snapshot mapping。
- mismatch detection。

## 不可以先做

任何：

- corrective order。
- forced broker close/open。
- automatic mismatch repair。

Corrective broker execution 必須先完成：

    GAP-BROKER-001
    OrderIntent / PositionEffect

---

# 25. Persistence / Recovery

Future operational PostgreSQL SOR 至少保存：

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

Identifiers：

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

Event metadata：

- event_id。
- occurred_at。
- received_at。
- sequence。
- version。

---

# 26. Recovery Flow

    Process Start
    → Load Persisted Expected State
    → Query Broker Actual State
    → Reconcile
    → Reconstruct Strategy State
    → Validate
    → READY

Mismatch：

依 policy：

- halt。
- manual review。
- explicit recovery workflow。

禁止 silent overwrite。

---

# 27. Decision Provenance

Material action 應可追蹤：

    Signal
    → Decision
    → Risk
    → Order
    → Fill
    → Position
    → Trade
    → Review

DecisionContext 未來可包含：

- strategy version。
- config version。
- git commit。
- feature version。
- market regime。
- indicator values。
- competing signals。
- target account position。
- risk outcome。
- expected price。
- actual price。
- future ML/news reference。

Target account position 發生 material change：

保存完整 context。

HOLD：

允許 lightweight / sampled record。

---

# 28. Trading Modes

固定概念：

- BACKTEST。
- SIMULATED。
- BROKER_PAPER。
- LIVE_CONFIRM。
- LIVE_AUTO。

Market environment 與 execution environment 必須分離。

LIVE_AUTO：

default disabled。

---

# 29. Live Safety

LIVE_AUTO 前至少需要：

- explicit authorization。
- time-bound authorization。
- account scope。
- symbol scope。
- loss limit。
- position limit。
- runtime suspension。
- stale-data guard。
- reconciliation health。
- manual override。
- FORCE_FLAT。
- PAUSE_STRATEGY。
- kill switch。
- secrets management。
- audit trail。

---

# 30. Python Service Boundary

ASP.NET Core 不直接 import Python domain object。

V1 default：

    Versioned REST / JSON

Domain model：

不等於 wire DTO。

Wire contract 應支援：

- stable IDs。
- version。
- timestamp。
- expected / actual。
- correlation ID。
- causation ID。

gRPC：

只有 profiling 證明 REST 不足時才評估。

Kafka / RabbitMQ：

V1 不導入。

---

# 31. ASP.NET Core Application Architecture

Target logical projects：

    InvestmentPlatform.Api
    InvestmentPlatform.Application
    InvestmentPlatform.Contracts
    InvestmentPlatform.Infrastructure
    InvestmentPlatform.Realtime

## Api

- HTTP endpoint。
- authentication boundary。
- input validation。
- DTO mapping。

## Application

- use cases。
- workflow。
- approval。
- orchestration。

## Contracts

- versioned DTO。
- public application contracts。

## Infrastructure

- PostgreSQL。
- Python service client。
- external integrations。
- configuration。
- authorization implementation。

## Realtime

- SignalR。
- account/order/position update。
- system status。
- risk/live notifications。

ASP.NET 不直接碰 Shioaji SDK。

---

# 32. React Workspace Architecture

Target workspace：

- App Shell / Navigation。
- Research Workspace。
- Backtest Workspace。
- Strategy Workspace。
- Account Workspace。
- Orders / Positions。
- Risk / Live Control。
- Review / Audit。
- System Status。

React：

只呼叫 application API。

禁止：

- direct DB。
- direct broker。
- embedded secrets。

---

# 33. Security Boundary

Secrets：

不得放 repository。

Broker credential：

由 future infrastructure / secret provider 管理。

Authorization：

與 strategy logic 分離。

LIVE authorization：

必須：

- 可撤銷。
- 可過期。
- 限制 account。
- 限制 symbol。
- 限制 position。
- 限制 loss。
- 留 audit。

---

# 34. Observability

Future runtime 至少需要：

- structured logs。
- correlation ID。
- order lifecycle trace。
- reconciliation status。
- broker connection status。
- market-data freshness。
- risk state。
- persistence health。
- current trading mode。
- authorization state。

Observability 不是 execution authoritative truth。

---

# 35. Dependency Direction

固定：

    domain
      ↑
    strategy / trading
      ↑
    backtest / simulation / adapters / service
      ↑
    application
      ↑
    web

禁止：

- domain → broker SDK。
- trading → Shioaji。
- trading → ORM entity。
- React → database。
- React → broker。
- ASP.NET Core → Shioaji SDK。

---

# 36. Migration Strategy

禁止 big-bang refactor。

固定做法：

1. 建 canonical contract。
2. 保留 compatibility。
3. 移一個 consumer。
4. 加 equivalence / targeted tests。
5. full regression。
6. small commit。
7. 下一 consumer。

成熟 BacktestEngine 行為優先保留。

---

# 37. V1 Closure Definition

V1 不以檔案數判定。

至少需要：

- historical data 可重現。
- research/backtest 可重現。
- strategy/config/version 可追蹤。
- multi-strategy decision 可驗證。
- risk/sizing 可驗證。
- paper/simulation lifecycle 可驗證。
- broker account/position 可同步。
- mismatch 可 reconciliation。
- trading state 可 persistence。
- restart 可 recovery。
- incremental market state 可運作。
- live safety gate 完整。
- Python service boundary 穩定。
- ASP.NET Core application 可完成主要 workflow。
- React workspace 可完成主要 workflow。
- review/audit trace 完整。
- full V1 integration regression 完成。

即使 V1 software completion：

LIVE_AUTO real money 仍需獨立 production verification 與 authorization。
---

# Engineering Blueprint Layer

System architecture：

定義：

- layer。
- canonical ownership。
- dependency direction。
- system invariants。
- technology responsibility。

Engineering Blueprint：

`V1_SYSTEM_BLUEPRINT.md`

進一步定義：

- A～O Domains。
- capability groups。
- engineering leaves。
- upstream / downstream。
- current / target / migration。
- external source。
- acceptance。
- test。
- weight / lifecycle。
- GAP / Work Package mapping。

Blueprint 不得：

- 改寫本文件既有 architecture invariant。
- 建立第二份 canonical truth。
- 因 target architecture 存在就執行 big-bang migration。

Architecture：

    定義「系統怎麼組成」

Blueprint：

    定義「系統如何拆成可施工、可追蹤、可量化的工程項目」

ACTIVE：

    定義「這一次允許實作哪些 Blueprint leaves」
