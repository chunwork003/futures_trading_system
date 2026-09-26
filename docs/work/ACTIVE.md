# ACTIVE WORK PACKAGE

## GOV-01 Active Context Guard

`docs/CURRENT_STATE.md` is the canonical CURRENT runtime/planning governance projection。

This ACTIVE file preserves Work Package context/history and does NOT independently grant Runtime Authorization。

Runtime Authorization summary：NOT_AUTHORIZED。

Architecture Decision Baseline：`22ceaa729ab6e9da9c00ae52e09ae7116be5a743`。

Governance Planning Baseline：`f45742d9d16165f87f145f0d2bdc8d530772e5ee`；Correction-Freeze Baseline：`93fb846a9c9cd61eea44427a86a542fc95f9ac28`；latest bounded execution closure：`docs/work/GAP08_WAVE1_CLOSURE.md`。

Post-5E K520 / BG / scope-map / Delta-to-Contract conclusions、materialized leaves、DAG and reweight are frozen in `docs/work/GAP08_CORRECTION_FREEZE.md`。

V06 + C01 + C22 + C11 + C23 + C24 + C25 are COMPLETE；P1 and P2 are complete；no runtime leaf is currently authorized。

## 1. Work Package ID

GAP-08EFGHI

---

## 2. Title

Operational Persistence + Recovery

---

## 3. Status

RUNTIME_IMPLEMENTED_CANDIDATE

Runtime commit：`6b62239bca1d11543944f9f078e577e16010bcbf`

Runtime verification：934 passed / 4 skipped / 1 warning。

Architecture Acceptance：HOLD。

Decision Checkpoint 4：COMPLETE。

R-03：DECIDED。

R-04A-H：DECIDED。

R-04 overall：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

Runtime Authorization：NOT_AUTHORIZED。

Launch Gate：

`NOT_AUTHORIZED`

Original 35 leaves / weight 151：IMPLEMENTED CANDIDATE / NOT ACCEPTED。

Correction-Freeze bounded correction core：

C01～C25 weight 110 + V06 weight 3 = weight 113。

Original candidate + bounded correction core = weight 264。

V01～V05 broker capability verification = weight 19 separate。

V07 actual PostgreSQL environment conformance = weight 4 conditional。

Expanded correction scope：ARCHITECTURALLY_CLOSED / MATERIALIZED / DEDUPLICATED / REWEIGHTED / CORRECTION_FREEZE_COMPLETE。

## COMPLETED BOUNDED WORK PACKAGE — GAP-08-CORR-01

V06 + C01：

COMPLETE / VERIFIED。

Closure：

`docs/work/GAP08_C01_CLOSURE.md`

## COMPLETED BOUNDED WORK PACKAGE — GAP-08-CORR-02

C22：

COMPLETE / VERIFIED。

Authorization：

`docs/work/GAP08_AUTHORIZATION_C22.md`

Closure：

`docs/work/GAP08_C22_CLOSURE.md`

Runtime commit：

`e242d188b0029863d6df1b29889327dce623bd98`

Verification：

- targeted：21 passed。
- event-ledger compatibility：13 passed。
- full regression：955 passed / 4 skipped。
- runtime correction cycles：0。
- precheck tooling correction：1。

Correction-core progress：

    11 / 113 complete / verified
    102 remaining

STOP boundary：

REACHED。

## COMPLETED BOUNDED WORK PACKAGE — GAP-08-CORR-03

C11：

COMPLETE / VERIFIED。

Authorization：

`docs/work/GAP08_AUTHORIZATION_C11.md`

Closure：

`docs/work/GAP08_C11_CLOSURE.md`

Runtime commit：

`a2a54fa74152d720d42e39b211c1b80991496fa1`

Verification：

- targeted：23 passed。
- Shioaji compatibility：47 passed。
- full regression：959 passed / 4 skipped。
- runtime correction cycles：0。

V05：

NOT EXECUTED / NOT VERIFIED。

Observed local Shioaji package：

1.7.5。

This does not establish broker-semantic verification。

Correction-core progress：

    13 / 113 complete / verified
    100 remaining

STOP boundary：

REACHED。

## COMPLETED BOUNDED WORK PACKAGE — GAP-08-CORR-04

C23：

COMPLETE / VERIFIED。

Authorization：

`docs/work/GAP08_AUTHORIZATION_C23.md`

Closure：

`docs/work/GAP08_C23_CLOSURE.md`

Runtime commit：

`4750d243ba050935220ffa7319ca7ab3b336f393`

Verification：

- targeted：63 passed。
- compatibility：15 passed。
- full regression：1022 passed / 4 skipped。
- runtime correction cycles：0。

Implemented：

- MarketObservationLogicalKey。
- MarketObservationContentFingerprint。
- MarketObservationRevisionId。
- explicit versioned byte framing。
- fixed cross-language golden vectors。
- exact Decimal/time/timeframe identity semantics。

C24：

NOT EXECUTED。

C25：

NOT EXECUTED。

Correction-core progress：

    18 / 113 complete / verified
    95 remaining

STOP boundary：

REACHED。

## COMPLETED BOUNDED WORK PACKAGE — GAP-08-CORR-05

C24：

COMPLETE / VERIFIED。

Authorization：

`docs/work/GAP08_AUTHORIZATION_C24.md`

Closure：

`docs/work/GAP08_C24_CLOSURE.md`

Runtime commit：

`8944ecaf674b22cf1fe1df908d9125ce15538f0f`

Verification：

- domain targeted：18 passed。
- PostgreSQL contract：17 passed。
- compatibility：83 passed。
- full regression：1057 passed / 4 skipped。
- runtime correction cycles：1。

Implemented：

- versioned MarketObservationAcceptancePolicy。
- immutable candidate/provenance evidence。
- immutable accepted revision evidence。
- candidate decision history。
- corroboration links。
- contiguous per-key revision_seq authority。
- conflict/quarantine head projection。
- database atomic uniqueness contract。
- NEW PostgreSQL migration 0003。

Migration execution：

NOT EXECUTED。

Actual PostgreSQL / V07：

NOT EXECUTED / NOT VERIFIED。

C25：

NOT EXECUTED。

Correction-core progress：

    23 / 113 complete / verified
    90 remaining

STOP boundary：

REACHED。

## COMPLETED BOUNDED WORK PACKAGE — GAP-08-CORR-06

Leaf：

C25 — Durable-before-Strategy Delivery / Revision Ref Migration。

Authorization：

- `docs/work/GAP08_AUTHORIZATION_C25.md`
- `docs/work/GAP08_AUTHORIZATION_C25_AMENDMENT_01.md`

Runtime commit：

`940f54c6d9b4ed7bf0e1d3c8627b49be3fdae495`

Status：

COMPLETE / VERIFIED。

Verification：

- C22 + C25 targeted：64 passed。
- C23/C24 compatibility：112 passed。
- full regression：1081 passed / 4 skipped。
- runtime correction cycles：2。

Implemented：

- durable accepted MarketObservationRevision before strategy delivery。
- exact revision-specific resolution。
- StrategyStateSnapshot canonical revision reference。
- ExecutionTriggerRef canonical revision reference。
- arbitrary legacy observation ID cannot authorize READY。
- legacy/canonical disagreement fail-closed。
- NEW migration 0004 created。

Migration execution：

NOT EXECUTED。

Actual PostgreSQL / V07：

NOT EXECUTED / NOT VERIFIED。

Closure：

`docs/work/GAP08_C25_CLOSURE.md`

Correction-core progress：

    27 / 113 complete / verified
    86 remaining

P2：

COMPLETE。

STOP boundary：

REACHED。

## COMPLETED BOUNDED WAVE — GAP08-W1-ACCOUNT-AUTHORITY

Status：

COMPLETE / VERIFIED / REVIEWER_ACCEPTED / CLOSED。

Accepted leaves：

    C02
        -> C04
        -> C21
        -> C03

Final Runtime HEAD：

`6b9db14ff0e6f104f59e418aae2aa8f99f3a2119`

Closure：

`docs/work/GAP08_WAVE1_CLOSURE.md`

Reviewer correction：

- RF01 PASS。
- RF02 PASS。
- targeted：39 passed。
- full regression：1119 passed / 4 skipped。

Migration 0005：

CREATED / NOT EXECUTED。

Correction-core progress：

    46 / 113 complete / verified
    67 remaining

Runtime Authorization：

NOT_AUTHORIZED。

W1 source-modification authorization：

CONSUMED / CLOSED。

Next dependency-coherent Wave candidate：

    C08
        -> C05
        -> C06

W2 weight：

14。

W2 execution coherence：

VERIFIED。

W2 source-modification authorization：

BOUNDED_AUTHORIZED_FOR_GAP08_W2_RF01。

W2 runtime candidate：

`ff57c216cf0b3a1d1c894442a4a14b8a210db7f4`

Reviewer status：

HOLD / RF01_REQUIRED。

RF01 authorization：

`docs/work/GAP08_WAVE2_AUTHORIZATION_AMENDMENT_01.md`

Next actual work：

CODEX RF01 only；C08/C05 read-only。

STOP：

after RF01 verification/push；return to reviewer，do not start W3 or governance closure。

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

35 leaves / weight 151（original runtime candidate only；expanded correction delta is frozen separately in `docs/work/GAP08_CORRECTION_FREEZE.md`）。

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

## 34. Historical Runtime Launch Gate — SUPERSEDED

> SUPERSEDED：The authorization values in this historical launch section applied to the original runtime candidate execution only and do not grant current authority。
>
> Canonical CURRENT authority is `docs/CURRENT_STATE.md`，where Runtime Authorization = `NOT_AUTHORIZED`。

Current：

    RELEASED_ARCHITECTURE_FREEZE

Runtime authorization：

    AUTHORIZED

## Historical Decision Checkpoint 5A — Active Queue — SUPERSEDED

Completed：

- R-01 DECIDED / AMENDED。
- R-02 DECIDED / AMENDED。
- R-03 DECIDED / UNCHANGED。
- R-04 DECIDED / AMENDED。
- R-05 DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

Runtime Authorization：NOT_AUTHORIZED。

Current architecture task：

    R-06 + R-07 Recovery Boundary Cluster

Do not re-open R-01 through R-05 without a concrete contradiction/new authoritative evidence。

Do not begin bounded runtime correction until correction scope freeze/reweight and explicit authorization are complete。

## Historical Decision Checkpoint 5B — Active Queue — SUPERSEDED

Completed：

- R-06 DECIDED。
- R-07 DECIDED。

Current architecture task：

    R-08 + R-09 identity/config authority cluster

R-08：StrategyInstance instrument vs symbol identity。

R-09：strategy_instance_id / config_version / lifecycle authority。

Runtime Authorization：NOT_AUTHORIZED。

Do not re-open R-06/R-07 without concrete contradiction or new authoritative evidence。

Do not begin runtime correction until the correction package is frozen、reweighted and explicitly authorized。

## Historical Decision Checkpoint 5C — Active Queue — SUPERSEDED

Completed：

- R-08 DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-09 DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

Current architecture task：

    R-10 formal closure
    then R-11 occurred_at / received_at clock authority

Runtime Authorization：NOT_AUTHORIZED。

Do not re-open R-08/R-09 without concrete contradiction or new authoritative evidence。

Do not begin runtime correction until correction scope freeze/reweight and explicit authorization。

## Historical Decision Checkpoint 5D — Active Queue — SUPERSEDED

Completed：

- R-10 DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-11 DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

Current architecture task：

    R-12 ReconciliationRun audit contract

Runtime Authorization：NOT_AUTHORIZED。

Do not re-open R-10/R-11 without concrete contradiction or new authoritative evidence。

Do not begin runtime correction until correction scope freeze/reweight and explicit authorization。

## Historical Decision Checkpoint 5E — Active Queue — ARCHITECTURE RECORD

Completed：
- R-12 DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-13 DECIDED / BOUNDARY_CLASSIFIED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-14 DECIDED / BOUNDARY_CLASSIFIED / GAP-08_ENFORCEMENT_CORRECTION_REQUIRED / GAP-DATA-001_DEFERRED_PRODUCTION_DEPENDENCY。

No runtime Work Package is authorized。

Current architecture/governance task：
    K520 defer confirmation
    then Broker capability gate classification

After classification：
    correction-scope map
    -> reweight
    -> explicit bounded runtime authorization decision

Do not re-open R-01 through R-14 without concrete contradiction or new authoritative evidence。
Do not infer runtime authorization from candidate commit、architecture closure、classification completion or test history。
Runtime Authorization：NOT_AUTHORIZED。
