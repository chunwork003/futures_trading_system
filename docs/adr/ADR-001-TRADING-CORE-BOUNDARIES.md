# ADR-001：Trading Core Boundaries

## 1. Status

**ACCEPTED**

- Accepted Date：2026-09-24
- Acceptance scope：Architecture ownership、dependency direction、migration strategy。
- 此接受不代表 runtime migration 已完成；後續變更只能依 approved Work Package 與本 ADR migration sequence 執行。

## 2. Context

現有專案已有可測試的 backtest、paper lifecycle、multi-strategy decision、risk 與 Shioaji adapter foundation，但多數模型與服務歷史上集中於 `backtest/`。本 ADR 定義未來 Trading Platform 的 canonical ownership 與漸進式遷移；不改變 runtime 行為。

```text
Strategy Position != Target Account Position != Account Position != Broker Actual Position
Market Data -> Feature -> Strategy -> Strategy Intent -> Decision
            -> Target Account Position -> Portfolio/Risk -> OMS -> Broker
```

方向變更只能是 `EXIT -> confirm FLAT -> re-evaluate -> ENTER`。Expected 與 Actual 必須分開。

## 3. Existing Architecture Findings

- `backtest/models.py` 混合 signal、order/fill、position/trade、enum 與 `BacktestConfig`。
- `BacktestEngine` 的 next-bar、cost、SL/TP、forced liquidation、equity projection 與 deterministic reset 是成熟且受 regression 保護的 backtest 行為。
- `Broker` 是可用 core port，但 Paper、runner 與 Shioaji adapter 仍位於 `backtest/`。
- `ShioajiBroker` 直接使用 `sj.*`、Shioaji contract/trade object，且以 `ENTRY-` prefix 推定 New/Cover；後者是 GAP-BROKER-001。
- `domain/` 的 Instrument、Contract、Bar、Signal、Trade 與 richer 的 `backtest.models` / `MarketBar` 重複且欄位不同。
- `strategy/` 有 versioned definition/registry/runner；`strategies/` 有 strategy contract、concrete strategy 與另一個 registry。
- DuckDB schema、trading calendar 已保存 instrument、contract、margin、session 資料；它們是 repository/data source，不應成為另一份 runtime truth。

## 4. Decision

採取 **shared market domain + minimal trading core + ports/adapters + preserved backtest**：

1. `domain/` 長期擁有不帶 execution state 的 market identity 與 market observation。
2. `trading/` 長期擁有交易意圖、決策、帳戶目標、訂單／成交／部位狀態、風險決策與 reconciliation contract。
3. `backtest/` 是 `trading/` 的 deterministic historical simulation consumer，不再是 live/paper/broker canonical owner。
4. `strategy/` 是 framework / contracts / versioned definition / registry；`strategies/` 是 concrete implementations。
5. Shioaji-specific code 目標為 `adapters/sinopac/`，core 不得依賴 `sj.*`。

此為 ownership target，不要求一次建立全部 package 或搬移既有程式碼。

## 5. Target Package Boundaries

```text
domain/                         # instrument, contract, session, market observation
strategy/                       # definition, instance spec, contracts, registry
strategies/                     # concrete implementations
trading/                        # minimal cross-consumer core
  decision/                     # intent, target, attribution, decision/context
  execution/                    # order, fill, status, intent/effect, Broker port
  account/                      # logical/broker account, positions/snapshots
  risk/                         # sizing, capital management, risk decisions
  reconciliation/               # expected-vs-actual comparison
backtest/                       # replay, simulation semantics, cost, projection
adapters/sinopac/               # Shioaji mapping and API adapter
```

這是 namespace target。首次 migration 可用少量 `trading/` modules 表達；只有多 consumer 出現時才拆子 package。

## 6. Canonical Model Ownership

| Model | Canonical owner | 理由 |
|---|---|---|
| Instrument | `domain` | 資產身分，供 research、calendar、backtest、broker 共用。 |
| Contract | `domain` | 上市契約 lifecycle；GAP-07 擴充 specification。 |
| MarketBar | `domain` | 完整 OHLCV / contract / session / provenance observation；採 existing richer `MarketBar` 作遷移起點。 |
| Signal / Strategy Intent | `trading.decision` | strategy 的可執行邏輯意圖，不能等同 broker order；舊 Signal 先相容。 |
| StrategyDefinition | `strategy` | versioned algorithm identity 與 factory/contract。 |
| StrategyInstance | `strategy` | definition + versioned config + instrument/timeframe scope。 |
| StrategyPosition | `trading.decision` | 個別 strategy 邏輯持倉，不是 physical account position。 |
| TargetAccountPosition | `trading.decision` | 多策略 netting / conflict resolution 的期望帳戶目標。 |
| AccountPosition | `trading.account` | internal consolidated expected physical position。 |
| BrokerPositionSnapshot | `trading.account` | broker 回報 actual observation，永不覆寫 expected state。 |
| Order | `trading.execution` | canonical OMS order，不帶 SDK type。 |
| OrderIntent / PositionEffect | `trading.execution` | OPEN/CLOSE/REDUCE 明確語意，取代 ID prefix 推論。 |
| OrderStatus | `trading.execution` | broker-neutral lifecycle state。 |
| Fill | `trading.execution` | actual execution event；未來納入 broker fill ID / external reference。 |
| Trade | `trading.account` | completed economic outcome；backtest 可投影，不是其專屬模型。 |
| LogicalAccount | `trading.account` | capital bucket / strategy allocation；V1 manual capital。 |
| BrokerAccount | `trading.account` | real broker identity/config reference，可對應多個 LogicalAccount。 |
| RiskDecision | `trading.risk` | 可稽核 accept/reject/limit decision。 |
| TradingDecision | `trading.decision` | target/action 的可稽核輸出。 |
| DecisionContext | `trading.decision` | provenance：versions、market state、features、causation。 |
| ReconciliationResult | `trading.reconciliation` | expected internal state 與 actual broker snapshot 的差異。 |

`domain/` 只擁有 broker-neutral 的 Instrument、Contract、exchange、currency、multiplier、tick size、session/reference metadata 與 canonical identifiers。Instrument / Contract 只有一個 canonical representation；database entity、config DTO、Shioaji contract object 都是 adapter/data representation。

`adapters/sinopac/` 擁有 `sj.Contract`、Shioaji contract IDs、native enum、`FuturesOCType`、broker native metadata 與 broker object lifecycle。若未來需要 `BrokerInstrumentReference`，它必須是 broker-neutral reference concept，再由 adapter mapping 到 native broker contract；不得把 Shioaji metadata 直接加入 canonical `Contract`。

## 7. Dependency Rules

```text
domain, strategy, trading  <-  backtest / Python application runners
domain, strategy, trading  <-  adapters/sinopac, persistence adapters
Python/C# application      ->  ports/use cases, never broker SDK internals
```

- `domain` 不依賴 trading、backtest、broker SDK 或 ORM。
- `trading` 可參照 domain identity，不依賴 backtest、adapter、DuckDB、PostgreSQL ORM 或 `sj.*`。
- `backtest` 可依賴 domain/trading contract；不得反向成為 live model owner。
- adapter 實作 trading port，負責 canonical model ↔ external SDK/entity mapping。
- application orchestration 選擇 adapter、處理 lifecycle；core 不做 I/O。

## 8. Backtest Boundary

Backtest 長期負責 historical clock/replay、next-bar semantics、deterministic simulation、cost/slippage model、backtest portfolio/equity projection、trade/metrics input 與 research comparison。

Backtest 不擁有 broker port、broker account、broker actual position、reconciliation、persistent OMS state、live polling 或 broker-specific mapping。既有 `BacktestEngine`、`ExecutionEngine`、`PositionManager`、`Portfolio` 保留行為與 tests；僅在 core contract 已有 consumer 且 compatibility gate 通過後才逐步改變 import ownership。

## 9. Trading Core Boundary

需要 `trading/`，但只建立跨 backtest、simulation、broker、persistence 重複消費的 core contract。最小首次範圍是 execution models/port、decision target/action、account expected-vs-actual snapshot、risk decision contract。不要先建立 service locator、event bus、DDD aggregate hierarchy 或空 package。

`TradingDecision` 由 strategy intents、target、risk outcome 組成；`DecisionContext` 記錄 provenance。reversal orchestration 必須顯式保存 waiting-for-flat，而非讓 `DecisionAction` 直接產生反向 order。

## 10. Broker Adapter Boundary

`adapters/sinopac/` 擁有 Shioaji API、enum、trade object、contract resolution、status/action/price mapping、external ID 與 deal-sequence deduplication。它實作 `trading.execution.Broker` port，輸入／輸出僅使用 canonical core models。

核心禁止依賴 `sj.*`、Shioaji enum、trade object 或 contract object。adapter dependency 永遠是 `adapter -> trading/domain`。GAP-BROKER-001 必須先引入 explicit `OrderIntent` / `PositionEffect`，再移除 `ENTRY-` prefix 對 New/Cover 的推論。

## 11. Simulation / Paper Boundary

- `PaperBroker` 保留為 simple deterministic broker：requested price 立即 fill，適合 unit test 與 baseline。
- `PaperTradingEngine` 保留為 Python application orchestration：pending order、fill application、PositionManager/Portfolio coordination；不是 canonical broker domain。
- `PaperTradingRunner` 保留為 market-data polling runner；它是 application runner，不是 simulation core。
- `SimulationBroker` 未來實作同一 port，負責 configurable fill delay、partial fill、reject、cancel、disconnect、stale status 等 fault injection。它屬 GAP-SIM-001，不能用 PaperBroker 的立即成交取代。

## 12. Risk / Portfolio / Account Boundary

- `trading.risk.sizing`：intent/price/stop/capital -> desired quantity；研究與 runtime 共用。
- `trading.risk.capital`：LogicalAccount capital reference、allocation、exposure policy；不等於 sizing。
- `trading.risk`：PreTradeRisk 在 submit 前產出 `RiskDecision`；RuntimeRisk 監控 equity、margin、limits、stale/reconciliation state，必要時要求 protective action。先定義責任，不在本 ADR 實作。
- `trading.account`：LogicalAccount、BrokerAccount、AccountPosition、BrokerPositionSnapshot、TradeRecord、account/equity snapshots。
- `backtest.Portfolio`：保留為 historical projection，不是 live broker account truth。

V1 manual capital 是 LogicalAccount input，不要求 broker cash。cross-strategy capital borrowing 預設 OFF；例外需要明確 policy 與 audit。

## 13. Market / Contract Boundary

GAP-07 應以 `domain` 的 Instrument / Contract Specification 為 canonical read model：instrument identity、contract identity、exchange、currency、multiplier、tick size、execution-neutral static specification、trading session reference 與 contract lifecycle。

Margin Schedule / Margin Requirement 是 effective-dated、time-varying domain data，不是 Contract 的永久 immutable attribute。現有 `database/schema/06_margin.sql` 的 `effective_date` 方向應保留，並在 GAP-07 pre-check 確認 exact model。`BacktestConfig` 只能提供 scenario override；`RiskConfig`、Shioaji adapter 不得各自維護 margin truth。

Trading Session 由 `trading_calendar` 提供 calendar/session policy，domain 以 stable identifier/reference 使用。research、backtest、simulation、live 都讀同一 specification/repository port，避免 config、risk、broker、database 各自成為 truth。

## 14. Persistence Boundary

Domain/trading model 不等於 PostgreSQL ORM/entity：

```text
domain/trading models <- application use case <- persistence port <- PostgreSQL adapter/entity
```

GAP-08 persistence adapter 必須保存 Order、Fill、Position、TradingDecision、RiskDecision、ReconciliationResult、StrategyState、account/equity snapshot 與 immutable trading event history。adapter 將 entity 映射為 core model；core 不 import ORM。restart 時 application 載入 expected state、讀 broker actual snapshot、產出 reconciliation；禁止 silent overwrite。

Order / Fill 是 execution authoritative truth；Position 是 account / position state。TradeRecord 是 execution 加上 position/account lifecycle 所衍生的 completed trade、accounting、review representation，不能反向成為 Order、Fill 或 Broker Position 的 authoritative source。persistence/recovery 必須由 authoritative events/state 重建，不得只依賴 completed Trade table。

## 15. Python / C# Boundary

Python Quant Engine 保留 quant/data/features/strategies/backtest/optimization/simulation/risk calculation library，以及可由 CLI、Backtest、Web application 共用的 trading core contracts。ASP.NET Core Application 負責 user workflow、authorization、operational API、realtime connection、approval gate、system-of-record orchestration 與 React BFF/API；不得直接 import 或 embed Python domain objects。

V1 default integration 是 versioned REST / JSON service boundary。Domain model 不等於 wire DTO；API layer 可將 domain model mapping 為 application DTO。跨語言 payload 使用 stable IDs、version、timestamp、expected/actual fields、causation/correlation IDs；不暴露 Python class、Pydantic internals 或 broker SDK object。

gRPC 在 V1 不預設導入，僅於 performance profiling 證明 REST / JSON 不足時評估。direct process invocation 允許 development、CLI、local tooling，但不得作為 Web Application 的主要 production boundary。message/event 是未來 extension point；V1 不導入 Kafka、RabbitMQ 或複雜 distributed event architecture。

## 16. Compatibility Strategy

1. 新增 canonical contract，無行為變更；舊 `backtest.*` 保持 importable。
2. 舊路徑提供 compatibility re-export / adapter，並建立 deprecation inventory；不大量 rename。
3. 每次只遷移一個 consumer slice，保留 old/new equivalence tests。
4. 新功能只依賴新 boundary；既有行為由 targeted tests 與 full regression 保護。
5. 全部 internal consumers 遷移、persistence/reconciliation verified、至少一個 release cycle 後，才提案移除 alias；移除須獨立 Work Package。

Migration gates：small commit、targeted test、full regression、`git diff --check`、scope validation、可獨立 revert。不可同時搬模型、改語意、改 schema。

## 17. Migration Sequence

| Phase | Work | Gate / outcome |
|---|---|---|
| A | 接受 ADR；建立 canonical inventory 與 compatibility plan | 無 runtime refactor。 |
| B | GAP-07：Instrument / Contract Specification read boundary，保留 domain/database mapping | 一份 shared contract truth。 |
| C | GAP-BROKER-001：OrderIntent/PositionEffect；adapter mapping 使用明確語意 | 不再以 prefix 判定 New/Cover。 |
| D | GAP-ACCOUNT-001：BrokerAccount snapshot、AccountPosition、reconciliation use case/port | startup 可偵測 mismatch。 |
| E | GAP-08 + GAP-PERSIST-001：event/persistence port、recovery、provenance | restart 不遺失 state。 |
| F | GAP-SIM-001：SimulationBroker/fault model；保留 PaperBroker baseline | 故障條件可驗證。 |
| G | 逐 slice 遷移 paper runner / Shioaji adapter 至 adapter/application boundary | compatibility imports 保持。 |
| H | GAP-APP-001 / GAP-WEB-001：versioned API 接入 workflow | 不暴露 broker SDK。 |

## 18. Deferred Items

- 完整 multi-asset taxonomy、broker capability matrix 的完整產品覆蓋。
- 通用 event bus、CQRS/ES framework、full ORM migration、microservices 拆分。
- News Intelligence、Local LLM、mature ML、GIS / Property、Mobile、production server、full drawing engine。

## 19. Consequences

正面：保留成熟 backtest 行為；broker-neutral、persistence/recovery、未來 C# operational layer 有清楚接點；expected/actual 不再混淆。

代價：短期保留 compatibility alias 與雙模型 mapping；每個 slice 需 equivalence tests；M0-B 後仍需 GAP-07 和 broker semantics 才能形成可執行核心。

## 20. Risks

- 過早搬移可破壞 611 regression baseline，故 model migration 必須在功能 GAP 內小步進行。
- Contract Specification 未完成前，RiskConfig、BacktestConfig、broker metadata 仍可能漂移。
- 未定義 OrderIntent 前，live broker New/Cover 是 safety blocker。
- persistence/reconciliation 未完成前，LIVE_AUTO 不可授權。

## 21. Validation / Acceptance Criteria

- Architect 確認 canonical ownership、dependency direction、Python/C# V1 interface、migration order。
- ADR 不修改 runtime、tests、database、data 或 dependency。
- 每個 migration slice 有 targeted/full regression、compatibility test、small commit、independent revert path。
- GAP-07 不建立第二份 contract truth；GAP-08 不讓 ORM entity 成為 domain model；adapter 不洩漏 SDK type 至 core。

## 22. Do Not Do

- 不重寫 BacktestEngine、MultiStrategy Decision Layer、Position Sizing、Paper lifecycle 或 Shioaji adapter。
- 不一次改所有 imports、mass rename 或刪除 existing models。
- 不由 order ID naming 猜測 long-term broker semantics。
- 不把 BrokerActualPosition 當 AccountPosition，或把 Portfolio 當 broker truth。
- 不在 M0-B 開始 runtime refactor、database migration、Live execution 或 dependency installation。
