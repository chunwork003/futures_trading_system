# State Authority Matrix

## Status

AUTHORITATIVE
---

| State / Data | Authority | Runtime Representation | Persistent / Storage Direction | Must Not Be Confused With |
|---|---|---|---|---|
| Raw source data | External/source dataset | ingestion source object | raw/local source | canonical cleaned data |
| Historical market data | Canonical historical dataset | MarketBar / frame | Parquet | live operational state |
| Analytical query state | Analytical layer | Polars / DuckDB relation | DuckDB metadata/query | operational SOR |
| Instrument specification | Canonical Domain | InstrumentSpec | future reference persistence | broker product object |
| Contract specification | Canonical Domain | ContractSpec | future reference persistence | broker contract object |
| Trading session rules | Trading Calendar / canonical reference | TradingSessionRef | reference data | hidden local clock |
| Margin reference | MarginSchedule | MarginScheduleEntry | effective-dated SOR | scenario RiskConfig override |
| Broker instrument mapping | Canonical broker-neutral mapping | BrokerInstrumentReference | future persistence | native sj.Contract |
| Strategy logical position | Decision layer | StrategyPosition | StrategyStateSnapshot | account physical position |
| Target account position | Decision layer | TargetAccountPosition | TradingDecision / target snapshot | broker actual position |
| Internal expected position | Account layer | AccountPosition | AccountPositionSnapshot | BrokerPositionSnapshot |
| Broker actual position | Broker observation | BrokerPositionSnapshot | BrokerPositionSnapshot record | AccountPosition |
| Trading decision | Decision layer | TradingDecision | decision record | broker order |
| Risk decision | Risk layer | RiskDecision | risk record | order status |
| Order intent | Execution layer | OrderIntent | order intent/order record | Signal |
| Order | OMS / execution | Order | Order record | TradeRecord |
| Order event | Execution event stream | OrderEvent | append-only event | projected position |
| Fill | Execution event truth | Fill | Fill record | requested order price |
| Trade record | Account/review projection | TradeRecord | trade record | authoritative fill history |
| Reconciliation result | Reconciliation layer | ReconciliationResult | ReconciliationCase | automatic repair |
| Operational trading state | PostgreSQL SOR | recovered state projection | PostgreSQL | DuckDB |
| UI view state | Application/UI projection | DTO/view model | optional application state | operational authority |

---

## Core Rules

### Expected vs Actual

    AccountPosition != BrokerPositionSnapshot

### Target vs Expected

    TargetAccountPosition != AccountPosition

### Strategy vs Physical

    StrategyPosition != TargetAccountPosition

### Execution Truth

Order / OrderEvent / Fill：

是 execution authority。

Position：

是 state projection。

TradeRecord：

是 completed economic/review representation。

### Operational Persistence

PostgreSQL：

future operational SOR。

DuckDB：

analytical/research。

Parquet：

historical / feature dataset。

三者不得 silent interchange authority。

## Decision Checkpoint 5C — Strategy / Policy Authority Separation

| State / Data | Authority | Must Not Be Confused With |
|---|---|---|
| StrategyDefinition / implementation revision | E Domain immutable strategy-definition authority | StrategyConfigVersion / deployment presence |
| StrategyInstance lifecycle identity | E lifecycle/config authority under R-09 | instrument_id / strategy_id / config hash |
| StrategyConfigVersion | E strategy-config authority | StrategyInstance identity / DecisionPolicyVersion |
| StrategyInstance instrument binding | E lifecycle binding referencing D canonical instrument authority | StrategyInstance identity / executable ContractSpec |
| DecisionPolicyVersion | G decision-policy authority | StrategyConfigVersion |
| Governing-context transition | R-09 lifecycle transition contract coordinating referenced E/G/D authorities | restart / deployment / current config file |

D Domain remains authority for instrument/contract identity semantics。

E Domain remains authority for strategy definition、instance/config lifecycle semantics。

G Domain remains authority for decision-policy semantics。

R-09 coordinates lifecycle/governing-context transition safety；it does not absorb D/E/G semantic ownership。

## Decision Checkpoint 5D — Temporal Authority Separation

| Time Concept | Semantic Authority | Must Not Be Confused With |
|---|---|---|
| occurred_at | represented fact-specific source/local occurrence authority | received_at / ordering sequence |
| received_at | first successful durable canonical ingress for immutable evidence identity | source occurrence time / replay time |
| observed_at | external observation boundary | historical state-change time / linearizable broker snapshot |
| recorded_at | explicitly defined local record/persistence boundary | database commit proof / causal order |
| captured_at | derived strategy/state capture boundary | source market occurrence time |
| effective_at | represented domain-effective state boundary | recorded_at / commit time |
| confirmed_at | confirmation-time boundary；authorization semantics remain R-13 | authority identity/permission itself |

Explicit sequence/revision/frontier identities remain causal/order authority；timestamps remain temporal/audit evidence。

## Decision Checkpoint 5E — Audit / Authorization / Completeness Authority Separation

| State / Evidence | Authority | Must Not Be Confused With |
|---|---|---|
| ReconciliationRun | J/K formal reconciliation audit authority | final READY authority / ReconciliationCase lifecycle / AccountStateHead |
| ReconciliationRun evaluated-input binding | exact immutable/versioned evaluated reconciliation world | mutable latest/current repository lookup |
| AuthorizationDecision | N/L-governed protected-action authority evidence consumed by core boundary | command identity / BrokerActionAttempt / broker idempotency |
| Authorization audit metadata | actor/reason/time/context audit fields | authorization proof by themselves |
| Market completeness proof | consumer-scoped canonical observation coverage authority | raw source health / candidate count / recent timestamp |
| Completeness currentness witness | deterministic applicability proof for evaluated data world | historical COMPLETE / wall-clock recency alone |

ReconciliationRun audit does not advance economic AccountStateHead merely because a Run is recorded/finalized。

Authorization does not itself create economic authority or broker side-effect safety。

Market completeness belongs to the strategy/data readiness axis and does not automatically HALT BrokerAccount execution authority。

Candidate runtime commit remains distinct from runtime authorization。
