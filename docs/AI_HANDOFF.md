# AI Handoff

## 1. Repository Baseline

Repository：

`futures_trading_system`

Development branch：

`master`

Architecture baseline：

`771f10f`

Recorded full regression：

`800 passed`

Known local untracked：

`data/`

`data/` 不得自動 stage。

---

## 2. Default Agent Reading

Runtime Work Package 預設只讀：

1. `AGENTS.md`
2. `docs/work/ACTIVE.md`

ACTIVE 明確要求時，再讀：

- `docs/CURRENT_STATE.md`
- `docs/CURRENT_WORK.md`
- `docs/V1_CAPABILITY_MAP.md`
- `docs/V1_SYSTEM_BLUEPRINT.md`
- relevant `docs/blueprint/*.md`
- `docs/ARCHITECTURE.md`
- `docs/GAP_REGISTER.md`
- `docs/adr/ADR-001-TRADING-CORE-BOUNDARIES.md`
- 指定 runtime source files

禁止每次 whole-repo / whole-documentation rescan。

---

## 3. Product Architecture

Python：

Quant / Data / Research / Feature / Strategy / Backtest / Optimization / Simulation / Trading Core。

ASP.NET Core：

Application / Workflow / Authorization / Operational API / Realtime / Broker orchestration。

React + TypeScript：

Main investment workspace。

PostgreSQL + PostGIS：

Operational System of Record / GIS extension。

Parquet：

Historical / feature / analytical data。

DuckDB + Polars：

Local research / analytical layer。

First broker：

Sinopac Shioaji。

Architecture 必須 broker-neutral，且不得阻塞未來 equity、ETF、其他 broker、其他 asset class。

---

## 4. Authoritative Trading Flow

    Market Data
    → Feature / Market State
    → Strategy
    → Strategy Intent
    → Multi-Strategy Decision
    → TargetAccountPosition
    → Risk
    → Order / OMS
    → Broker
    → Fill
    → AccountPosition
    → Reconciliation
    → Persistence
    → Review

---

## 5. Position Identity Invariant

固定：

    StrategyPosition
    != TargetAccountPosition
    != AccountPosition
    != BrokerPositionSnapshot

StrategyPosition：

個別 strategy logical position。

TargetAccountPosition：

Decision Layer 產生的 physical account target。

AccountPosition：

internal expected physical position。

BrokerPositionSnapshot：

broker actual observation。

Broker actual state 不得 silent overwrite internal expected state。

---

## 6. Direction Change

固定：

    EXIT
    → confirm FLAT
    → re-evaluate
    → ENTER opposite side

禁止 silent direct reversal。

---

## 7. Strategy Architecture

固定：

    StrategyDefinition != StrategyInstance

StrategyDefinition：

algorithm identity / factory / version。

StrategyInstance：

definition + versioned configuration + instrument/timeframe scope。

持倉期間不得 silent mutate strategy parameters。

Configuration change 預設於 safe boundary 生效。

---

## 8. Multi-Strategy Decision

Strategies 維護 independent logical positions。

Multi-Strategy Decision Layer 統合 intents。

Final account actions：

- HOLD。
- ADD。
- REDUCE。
- EXIT。
- ENTER。

Strategy 不直接決定 broker physical position。

---

## 9. Account Architecture

固定：

    LogicalAccount != BrokerAccount

LogicalAccount：

internal capital bucket / strategy allocation。

BrokerAccount：

physical broker identity/reference。

一個 BrokerAccount 可服務多個 LogicalAccount。

V1：

- CapitalSource = MANUAL。
- Cross-strategy capital borrowing = OFF by default。

---

## 10. Trading Modes

- BACKTEST。
- SIMULATED。
- BROKER_PAPER。
- LIVE_CONFIRM。
- LIVE_AUTO。

Market environment 與 execution environment 分離。

LIVE_AUTO：

default disabled。

---

## 11. Canonical Instrument / Contract

Canonical futures symbols：

- TX。
- MTX。
- TMF。

Canonical symbol 不得等同：

- dataset alias。
- broker product code。
- broker contract code。
- continuous contract symbol。

Instrument / Contract canonical ownership：

`domain/`

Broker native identity：

adapter-owned。

---

## 12. GAP-07 Result

GAP-07：

CLOSED。

Completed：

- InstrumentSpec。
- ContractSpec。
- TradingSessionRef。
- MarginScheduleEntry。
- MarginScheduleResolver。
- Backtest/Risk specification resolution。
- BrokerInstrumentReference。
- actual multiplier consumer。
- actual margin consumer。

Margin precedence：

    explicit RiskConfig
    → canonical MarginSchedule
    → explicit no-margin
    → error

Missing canonical margin 不得 silent convert to zero。

Effective-date resolution 必須明確提供 as_of_date。

---

## 13. Time / Session

Canonical interval：

    [open, close)

Deferred：

- GAP-07-TIME-001。
- GAP-07-SESSION-001。
- GAP-07-SESSION-EXPIRY。

Operational timestamps：

timezone-aware。

Persistence：

PostgreSQL TIMESTAMPTZ。

Exchange/session interpretation：

Asia/Taipei。

---

## 14. Broker Boundary

Canonical identity 不等同 broker code。

BrokerInstrumentReference：

broker-neutral mapping。

Shioaji native contract / account / position objects：

adapter-only。

Core 不得保存 `sj.*` object。

---

## 15. Broker Execution Semantics

GAP-BROKER-001：

CLOSED / ACCEPTED。

Accepted runtime commit：

`b5d309cc91c6dbdf539c17a46662cdde46716224`

Canonical：

    PositionEffect = OPEN / REDUCE / CLOSE

Accepted Shioaji mapping：

- LONG + OPEN -> Buy + New。
- SHORT + OPEN -> Sell + New。
- LONG + REDUCE/CLOSE -> Sell + Cover。
- SHORT + REDUCE/CLOSE -> Buy + Cover。

Accepted invariants：

- explicit OrderIntent required by ShioajiBroker。
- no order-ID New/Cover inference。
- no FuturesOCType.Auto business inference。
- no DayTrade semantics。
- no direct reversal。

Reversal remains：

    CLOSE
    -> confirmed FLAT
    -> re-evaluate
    -> OPEN opposite

## 16. Account Sync Foundation

GAP-ACCOUNT-001：

CLOSED / ACCEPTED。

Accepted runtime commit：

`50813b679f818f3837a9f50fdcda9921495ab507`

Completed：

- BrokerAccount。
- canonical AccountPosition foundation。
- BrokerPositionSnapshot。
- separate read-only account / position capability interfaces。
- reverse broker contract resolution。
- Sinopac pure mapping。
- expected / actual pairwise mismatch detection。

Still prohibited：

- corrective broker order。
- automatic broker repair。
- silent expected / actual overwrite。

Next prerequisite：

GAP-BROKER-001 explicit OrderIntent / PositionEffect。

## 17. Reconciliation

Target inputs：

- internal expected state。
- persisted expected state。
- broker actual observation。

Target outputs：

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

V1 startup 預設偏向：

STRICT_HALT / MANUAL_REVIEW。

禁止 silent overwrite。

---

## 18. Persistence Direction

Future operational SOR：

PostgreSQL。

至少保存：

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

Execution authority：

Order / OrderEvent / Fill。

Position：

state projection。

TradeRecord：

completed economic/accounting/review representation。

Recovery 不得只依賴 TradeRecord。

---

## 19. Decision Provenance

Material action：

    Signal
    → Decision
    → Risk
    → Order
    → Fill
    → Position
    → Trade
    → Review

Future identifiers：

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

DecisionContext 可包含：

- strategy version。
- config version。
- git commit。
- feature version。
- market regime。
- indicator values。
- competing signals。
- target position。
- risk outcome。
- expected/actual execution data。
- future ML/news reference。

---

## 20. Recovery Direction

    load persisted state
    → query broker actual
    → reconcile
    → reconstruct strategy state
    → validate
    → READY

Mismatch：

依 policy halt / review / explicit recovery。

禁止 silent overwrite。

---

## 21. Numeric Boundary

Operational trading / persistence：

Decimal / NUMERIC。

Research：

float allowed。

Canonical margin reference：

不等同 RiskConfig scenario override。

Broker actual margin：

不等同 canonical reference margin。

---

## 22. Simulation Boundary

PaperBroker：

simple deterministic baseline。

SimulationBroker：

future separate component。

Target：

- latency。
- partial fills。
- reject。
- cancel。
- disconnect。
- stale status。
- delayed update。
- fault injection。

---

## 23. Python / ASP.NET Boundary

V1 default：

versioned REST / JSON。

ASP.NET Core：

不得 import/embed Python domain objects。

Domain model：

不等於 wire DTO。

Wire DTO：

應使用 stable IDs、version、timestamp、expected/actual、correlation/causation。

gRPC：

只有 profiling 證明 REST 不足才評估。

V1 不導入 Kafka/RabbitMQ。

---

## 24. UI Boundary

React：

只透過 Application API。

禁止：

- direct database。
- direct Shioaji。
- direct secrets。

---

## 25. LIVE Safety

LIVE_AUTO 前至少：

- Account Sync。
- Reconciliation。
- explicit OrderIntent / PositionEffect。
- persistence。
- restart recovery。
- stale-data guard。
- runtime risk。
- authorization scope。
- manual override。
- force-flat。
- kill switch。
- audit。
- capability/verification matrix。

目前：

LIVE_AUTO NOT AUTHORIZED。

---

## 26. Current Progress

Total V1 capability blocks：

92。

Engineering leaves：

603。

Lifecycle-weighted completion：

40.31%。

Architecture Design Coverage：87.23%。
Design Freeze Coverage：49.13%。
Runtime Implementation：35.19%。
Unit Verification：31.96%。
Integration Verification：31.87%。
Accepted Capability：31.87%。

Capability status：

COMPLETE 9 / PARTIAL 50 / NOT_STARTED 33。

Readiness：

- Operational：NOT_READY。
- Production Live：BLOCKED。
- LIVE_AUTO：NOT_AUTHORIZED。

## 27. Automation Efficiency

Formal Level 3A runtime sample 1 — GAP-ACCOUNT-001：

- GPT-5.6 Sol / 輕度。
- user-observed 5HR usage：12%。
- full regression：776 passed。
- implementation correction cycles：0。

GAP-ACCOUNT-001 deterministic Phase 4A acceptance：

- user-observed 5HR usage：5%。

Formal Level 3A runtime sample 2 — GAP-BROKER-001：

- GPT-5.6 Sol / 輕度。
- user-observed 5HR usage：14%。
- files inspected：約 22。
- files created/modified：20。
- tool operations：24。
- implementation correction cycles：0。
- command syntax retries：2。
- targeted：49 passed。
- compatibility：80 passed。
- full regression：800 passed。
- wall time：unavailable。
- token/context：unavailable。

Policy：

- 不用目前樣本線性推算 quota capacity。
- 維持 Level 3A。
- 第 3 個穩定 runtime Work Package 完成後再評估 Level 3B。

## 28. Next Mainline Candidate

Last completed：

GAP-BROKER-001 Explicit OrderIntent / PositionEffect。

Status：

CLOSED / ACCEPTED。

Runtime commit：

`b5d309cc91c6dbdf539c17a46662cdde46716224`

Next：

GAP-RECON-001 Reconciliation Policy / Startup Readiness。

Status：

READY_FOR_ARCHITECTURE_REVIEW。

Runtime authorization：

NOT_YET_AUTHORIZED。

下一步先凍結 J600/J700 reconciliation policy / startup readiness semantics，再建立新的 ACTIVE Work Package。

## 29. Hard Stop

立即停止受影響工作：

- real-money risk。
- broker semantics ambiguity。
- business-rule ambiguity。
- destructive migration。
- architecture invariant conflict。
- unrelated core regression。
- secrets/security。
- Git history/remote anomaly。

---

## 29A. Blueprint Governance

V1 Engineering Blueprint：

`docs/V1_SYSTEM_BLUEPRINT.md`

Supporting：

`docs/blueprint/`

Current status：

`AUTHORITATIVE`

GAP-ACCOUNT-001 runtime：

`COMPLETED / ACCEPTED`

Accepted runtime commit：

`50813b679f818f3837a9f50fdcda9921495ab507`

Blueprint baseline activation 已完成：

- A～O complete。
- 92/92 capability mapping PASS。
- connection / state authority / source registry / traceability PASS。
- 603 engineering leaves。
- current lifecycle-weighted completion 40.31%。
- baseline commit：`432c48fb63c3d8d2760c0f2f5338e205ded63d30`。

Blueprint baseline accepted 後，ACTIVE 必須列 Implements / Touches / Does Not Implement Blueprint IDs。

Runtime Codex 只讀 ACTIVE 指定的 Blueprint 與 source documents，不得 whole-repo rescan，也不得重新設計已凍結 architecture。

Broker / exchange / live-money semantics 優先使用 `docs/blueprint/SOURCE_REGISTRY.md` 的官方來源；不足時 HARD_BLOCK / REVIEW，不得猜測。
