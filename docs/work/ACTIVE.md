# ACTIVE WORK PACKAGE

## 1. Work Package ID

GAP-08EFGHI

---

## 2. Title

Operational Persistence + Recovery

---

## 3. Status

READY_FOR_EXECUTION

Design Freeze：COMPLETED。

Runtime Authorization：AUTHORIZED。

Launch Gate：

`RELEASED_ARCHITECTURE_FREEZE`

Architecture ancestor：

`10fb882fded93b98b39f39258005dce7e232f898`

Design freeze commit：

`f463f82beb8426c36b91efbd03ad943918954b65`

---

## 4. Recommended Model

GPT-5.6 Sol

Effort：中度

Execution Mode：LEVEL_3A_BOUNDED

Model / effort不得中途切換。

Level 3B remains NOT_ENABLED。

---

## 5. Goal

一次完成 operational execution/account persistence、OMS canonical ownership、strategy state persistence與 restart recovery/readiness。

這是第一個目標推進總 lifecycle 約 5% 以上的大型 runtime sizing experiment。

---

## 6. Blueprint Implements

E510 E520

H170 H440 H450 H510 H520 H530 H540 H550 H830

J340 J810 J820 J830

K310 K320 K330 K340 K350
K410 K420 K430 K440 K450
K510 K530 K540
K710 K720 K730 K740 K750 K760 K770

35 leaves / weight 151。

Touches：E530 E540 / existing H/J/K accepted contracts。

Does Not Implement：

E310-E350 incremental feature runtime
H840 safe retry
K520
K810-K930
LIVE authorization

---

## 7. Baseline

Branch：master

Required ancestor：

`10fb882fded93b98b39f39258005dce7e232f898`

Recorded full regression：897 passed / 2 skipped

Known untracked：data/

data/ must not be modified/staged。

---

## 8. Canonical Execution

Implement trading.execution canonical OrderType / OrderStatus / Order / Fill / OrderEvent exactly as frozen in H blueprint。

Legacy backtest models remain compatibility surfaces。

No big-bang consumer migration。

---

## 9. OMS State Machine

Creation sequence 0：None -> PENDING。

Then enforce frozen legal transition table、contiguous sequence、terminal immutability、partial-cancel semantics。

OrderEvent uses existing TradingEvent/EventLedger as append-only evidence。

Order projection is derived mutable state only。

---

## 10. Execution Identity

Internal：order_id / event_id / fill_id。

External：broker_order_id / broker_trade_id / broker_deal_id remain separate opaque references。

Do not infer economics from IDs。

---

## 11. Atomic Execution UoW

One material execution update transaction atomically：

1. append OrderEvent
2. append new Fill evidence
3. save Order projection
4. append complete expected-position snapshot batch when position changes

Any failure rolls back all。

Repositories never commit。

---

## 12. Account Persistence

Implement complete-batch expected AccountPositionSnapshot and BrokerPositionObservation contracts。

Both support empty collection = FLAT。

Expected and actual use separate tables/repositories。

latest/as_of expected ordering：effective_at -> recorded_at -> snapshot_id。

Persisted broker observation is audit only；startup actual still comes from BrokerPositionProvider。

---

## 13. AccountSnapshot

Implement canonical immutable trading.account.AccountSnapshot with frozen fields/Decimal/time semantics。

At least one account monetary observation required。

---

## 14. ReconciliationCase Persistence

Append-only version history。

Resolution appends new version；never overwrites historical case evidence。

No corrective broker action。

---

## 15. StrategyInstance

Implement strategy.instance.StrategyInstance：

- strategy_instance_id
- strategy_id
- strategy_version
- config_version
- config_fingerprint
- instrument_id
- timeframe
- config_json

Canonical config fingerprint is SHA-256 of deterministic JSON。

Do not implement incremental feature state。

---

## 16. Stateful Strategy

Explicit protocol：

- state_schema_version
- export_state()
- restore_state()

Implement explicit codecs for EMA_CROSS、TREND_STATE、TREND_STATE_EXIT。

Do not persist arbitrary __dict__ / private attributes generically。

---

## 17. StrategyStateSnapshot

Implement frozen immutable snapshot envelope with exact identity/config/scope/schema/market-observation validation。

Snapshot boundary = completed market observation after strategy processing and before next observation。

K520 remains excluded。

---

## 18. Recovery

Fixed order：

load persisted execution/account
-> query broker actual
-> reconcile
-> unresolved-case gate
-> validate/load strategy snapshot
-> instantiate strategy
-> restore explicit codec
-> validate
-> READY/HALT/REVIEW

Never restore strategy before account/reconciliation permits continuation。

---

## 19. Recovery Failure Mapping

Account HALT -> HALT。
Account REVIEW -> REVIEW。
Missing snapshot -> HALT。
Unknown strategy/version -> HALT。
Config/fingerprint/scope mismatch -> HALT。
State schema mismatch -> HALT。
State restore failure -> HALT。
Market observation boundary mismatch -> HALT。

No silent repair/replay guess。

---

## 20. PostgreSQL

Add one versioned non-destructive migration after 0001_event_ledger.sql。

Separate tables for order projection、fills、expected snapshots、broker observations、account snapshots、reconciliation history、strategy snapshots。

OrderEvents remain in event_ledger。

Traditional Chinese comments required。

PG17/PG18 integration remains PENDING when DSNs absent。

---

## 21. Allowed Runtime Files

Primary canonical：

trading/execution.py
trading/account.py
trading/reconciliation.py only if persistence-facing compatibility requires bounded additions
trading/__init__.py

strategy/instance.py
strategy/state.py
strategy/registry.py
strategy/__init__.py

strategies/base.py
strategies/ema_cross.py
strategies/trend_state.py
strategies/trend_state_exit.py

Persistence：

persistence/contracts.py
persistence/events.py
persistence/execution.py
persistence/account.py
persistence/reconciliation.py
persistence/strategy_state.py
persistence/recovery.py
persistence/__init__.py

persistence/postgres/execution.py
persistence/postgres/account.py
persistence/postgres/reconciliation.py
persistence/postgres/strategy_state.py
persistence/postgres/event_ledger.py only for bounded reuse/integration
persistence/postgres/uow.py only for bounded integration
persistence/postgres/__init__.py
persistence/postgres/migrations/0002_operational_persistence.sql

Compatibility files only when required：

backtest/models.py
backtest/broker.py
backtest/execution_result.py
backtest/order_factory.py
backtest/paper_broker.py
backtest/shioaji_fill.py
backtest/shioaji_mapping.py
backtest/shioaji_broker.py

Tests may add bounded unit/integration files corresponding to this Work Package。

---

## 22. Forbidden

data/**
database/**
features/**
analysis/**
unrelated decision/risk/sizing code
K520 incremental feature implementation
H840 retry implementation
K810-K850 provenance
LIVE authorization
deployment/secrets
destructive migration
unrelated cleanup

---

## 23. Required Verification — Execution

- canonical model validation/immutability
- exact Decimal and timezone-aware time
- legal/illegal transition matrix
- sequence 0 creation
- contiguous sequence
- terminal immutability
- partial fill -> filled
- partial fill -> cancelled
- duplicate OrderEvent replay
- event identity/idempotency/sequence conflicts
- fill identity/dedup
- native broker-deal duplicate conflict
- correlation/causation chain
- order projection optimistic version conflict
- repository no commit
- atomic rollback across event/fill/order/expected snapshot

---

## 24. Required Verification — Account/Reconciliation

- OPEN/ADD/REDUCE/CLOSE fill projection
- no silent reversal
- expected complete snapshot including empty FLAT
- broker observation including empty FLAT
- expected/actual separate repository/table
- latest/as_of ordering/tie break
- AccountSnapshot Decimal/time
- append-only ReconciliationCase versions
- unresolved case gating
- resolution never submits broker action
- persisted expected loader compatibility
- broker actual still queried from provider

---

## 25. Required Verification — Strategy/Recovery

- StrategyInstance identity/config fingerprint
- config mismatch rejection
- explicit state export/restore for three strategies
- invalid state payload rejection
- uninterrupted vs restored next-decision equivalence
- missing snapshot HALT
- version mismatch HALT
- schema mismatch HALT
- market observation mismatch HALT
- account HALT prevents strategy restore
- account REVIEW prevents READY
- successful reconciliation + state restore -> READY
- K520 not required

---

## 26. PostgreSQL Integration

Use existing：

POSTGRES17_TEST_DSN
POSTGRES18_TEST_DSN

Absent -> SKIP / remain PENDING。

Present -> exact-major migration/repository/restart smoke in rollback-safe test scope。

Never fake VERIFIED。

---

## 27. Compatibility

Run existing：

- OrderIntent/PositionEffect
- PaperBroker/PaperTradingEngine
- async/partial/multi-fill
- Shioaji mapping/submission/status/deal dedup
- account/reconciliation
- event ledger
- strategy registry/multi-runner/concrete strategies
- direction-transition

Then full regression。

---

## 28. Acceptance

PASS requires all frozen semantics implemented with targeted/compatibility/full regression PASS。

PG17/18 may remain PENDING only when test DSNs absent。

No scope creep。

No data/ changes。

No governance docs modified by runtime executor。

---

## 29. Hard Stop

- canonical state model must change
- transaction authority ambiguity
- expected/actual cannot remain separated
- strategy private state cannot be explicitly serialized safely
- recovery needs K520/incremental feature semantics
- broker/live-money behavior requires guessing
- destructive migration required
- secret exposure
- unrelated regression
- data/ modified

---

## 30. Git

Commit message：

feat(persistence): add operational recovery persistence

Exact staging only。

Push origin master / fetch / verify。

No amend/rebase/force/reset-hard。

---

## 31. Dynamic Calibration

Record：

- user-observed 5HR
- wall time
- files read/created/modified
- tool ops
- retries
- correction cycles
- targeted/compatibility/full regression
- PG17/PG18 status
- implemented leaves/weight = 35 / 151

Do not estimate token/context if unavailable。

After acceptance compare lifecycle gain per 5HR against previous samples。

---

## 32. Documentation Responsibility

Runtime executor commits/pushes runtime only and then STOPS。

Do not close GAP-08。

Do not begin GAP-09。

Do not enable Level 3B。

---

## 33. Re-entry Scope

Read AGENTS.md + ACTIVE.md first。

Then bounded direct dependencies only。

No whole-repo rescan。

---

## 34. Runtime Launch Gate

Current：

    RELEASED_ARCHITECTURE_FREEZE

Runtime authorization：

    AUTHORIZED
