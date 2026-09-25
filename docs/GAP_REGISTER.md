# GAP Register

## Purpose

GAP Register 記錄：

- correctness issue。
- architecture gap。
- migration debt。
- live blocker。
- environment/repository issue。
- follow-up。

GAP Register 不是產品 roadmap。

完整功能：

`V1_CAPABILITY_MAP.md`

完整 engineering decomposition：

`V1_SYSTEM_BLUEPRINT.md`

Blueprint ID：

不是 GAP ID。

Blueprint 描述 planned capability。

GAP 描述問題 / 缺口 / blocker / follow-up。

Mainline：

`CURRENT_WORK.md`

---

## Classification

### Priority

- P0：money/live safety 或 current correctness blocker。
- P1：V1 mainline required。
- P2：important follow-up。
- P3：Post-V1。
- OBS：observation only。

### Handling

- AUTO_FIX。
- RECORD_AND_CONTINUE。
- REVIEW_AT_CHECKPOINT。
- HARD_BLOCK。

---

# Current Main GAPs

| ID | Priority | Handling | Current Blocking | Scope | Status |
|---|---|---|---|---|---|
| GAP-ACCOUNT-001 | P1 | REVIEW_AT_CHECKPOINT | No | Broker Account / Position Sync | CLOSED |
| GAP-RECON-001 | P1 | REVIEW_AT_CHECKPOINT | No | Reconciliation / startup readiness | IN_PROGRESS |
| GAP-BROKER-001 | P1 | REVIEW_AT_CHECKPOINT | No | Explicit OrderIntent / PositionEffect | CLOSED |
| GAP-BROKER-002 | P2 | RECORD_AND_CONTINUE | No | Capability matrix / mapping semantics | PARTIAL |
| GAP-08 | P1 | REVIEW_AT_CHECKPOINT | No | Trading State Persistence / Recovery | PENDING |
| GAP-PERSIST-001 | P1 | RECORD_AND_CONTINUE | No | Decision / Risk Provenance | OPEN |
| GAP-09 | P1 | REVIEW_AT_CHECKPOINT | No | Incremental Feature / Market State | PENDING |
| GAP-SIM-001 | P2 | RECORD_AND_CONTINUE | No | SimulationBroker / fault injection | OPEN |
| GAP-LIVE-001 | P0 | HARD_BLOCK | Production Live | LIVE_AUTO authorization / runtime safety | OPEN |
| GAP-APP-001 | P1 | RECORD_AND_CONTINUE | No | ASP.NET Core Application/API | PLANNED |
| GAP-WEB-001 | P1 | RECORD_AND_CONTINUE | No | React Workspace | PLANNED |
| GAP-REVIEW-001 | P2 | RECORD_AND_CONTINUE | No | Review / audit | OPEN |

---

# Architecture / Migration GAPs

| ID | Priority | Handling | Blocking Current | Scope | Status |
|---|---|---|---|---|---|
| GAP-ARCH-001 | P2 | RECORD_AND_CONTINUE | No | Backtest/trading/broker ownership migration | OPEN |
| GAP-ARCH-002 | P2 | RECORD_AND_CONTINUE | No | domain/backtest model duplication | OPEN |
| GAP-ARCH-003 | P2 | RECORD_AND_CONTINUE | No | strategy/strategies duplication | OPEN |
| GAP-07-TIME-001 | P1 | RECORD_AND_CONTINUE | No; Live blocker later | timezone-aware boundary | OPEN |
| GAP-07-SESSION-001 | P2 | RECORD_AND_CONTINUE | No | duplicated session rules | OPEN |
| GAP-07-SESSION-EXPIRY | P1 | RECORD_AND_CONTINUE | No; Live blocker later | expiry-day session consolidation | OPEN |
| GAP-07-MARGIN-001 | P2 | RECORD_AND_CONTINUE | No | DuckDB refinement / broker actual margin | PARTIAL |

---

# Repository / Environment GAPs

| ID | Priority | Handling | Blocking Current | Scope | Status |
|---|---|---|---|---|---|
| GAP-REPO-001 | P2 | RECORD_AND_CONTINUE | No | GitHub default main vs dev master | OPEN |
| GAP-REPO-002 | P2 | RECORD_AND_CONTINUE | No | local data governance | OPEN |
| GAP-ENV-001 | P2 | RECORD_AND_CONTINUE | No | pytest cache/temp warning | OPEN |
| GAP-DOC-001 | P2 | RECORD_AND_CONTINUE | No | stale supplemental docs | PARTIAL |

---

# Closed Major GAPs

## GAP-03

Execution Lifecycle。

Status：

CLOSED。

Included：

- pending order sync。
- fill dedup。
- partial fill accumulation。
- terminal handling。
- async exit。
- paper runner integration。
- LONG lifecycle。
- SHORT lifecycle。
- partial entry。
- partial exit。
- SL / TP。

---

## G-5

Multi-Strategy Decision Architecture。

Status：

CLOSED。

---

## GAP-06

Position Sizing / Capital Allocation。

Status：

CLOSED。

---

## GAP-07

Contract / Futures Specification。

Status：

CLOSED。

Completed：

- A0 canonical product semantics。
- A InstrumentSpec。
- B ContractSpec。
- C TradingSessionRef。
- D MarginSchedule。
- E specification resolution seam。
- F BrokerInstrumentReference。
- E2 actual multiplier consumer。
- E3 actual margin consumer。

---

# GAP-BROKER-001 Detail

Status：

CLOSED / ACCEPTED。

Architecture freeze commit：

`d74de0cbad75fa32f39fd2e6a04dc7f865c527bb`

Accepted runtime commit：

`b5d309cc91c6dbdf539c17a46662cdde46716224`

Completed：

- PositionEffect = OPEN / REDUCE / CLOSE。
- immutable broker-neutral OrderIntent。
- explicit position-effect validation。
- LONG OPEN = Buy + New。
- SHORT OPEN = Sell + New。
- LONG REDUCE/CLOSE = Sell + Cover。
- SHORT REDUCE/CLOSE = Buy + Cover。
- FuturesOCType.Auto business inference prohibited。
- DayTrade semantics excluded。
- order ID prefix no longer determines broker execution semantics。

Verification：

- targeted：49 passed。
- compatibility：80 passed。
- full regression：800 passed。

Remaining：

Corrective reconciliation execution is not part of this closed GAP。


# GAP-ACCOUNT-001 Detail

Status：

CLOSED / ACCEPTED。

Accepted runtime commit：

`50813b679f818f3837a9f50fdcda9921495ab507`

Full regression：

776 passed。

Target：

broker-neutral：

- BrokerAccount。
- BrokerPositionSnapshot。
- account query capability。
- position query capability。
- internal expected AccountPosition comparison。

Allowed before GAP-BROKER-001：

read-only snapshot and mismatch detection。

Architecture review decision：

- account/position query 使用 separate read-only capability interface。
- 不擴充 existing execution Broker ABC。
- existing `backtest.account_position.AccountPosition` 保持 compatibility，不在此 GAP 搬移。
- 不預建完整 target package hierarchy。
- only immediate implementation packages/modules may be created。

Not allowed：

automatic corrective broker order。

---

# GAP-RECON-001 Detail

Status：

IN_PROGRESS。

Architecture / Design Freeze：

COMPLETED for J610-J780。

GAP-RECON-001A：

    Policy / Result / Case

    J610 J620 J630 J640 J650 J660 J670 J680 J690

Status：

COMPLETED / ACCEPTED。

Accepted runtime commit：

`d7dbd884f09e72d7737726409e11e0679206ed8d`

Verification：

- targeted：32 passed。
- compatibility：22 passed。
- full regression：821 passed。
- correction cycles：0。

GAP-RECON-001B：

    Collection / Startup Readiness

    J710 J720 J730 J740 J750 J760 J770 J780

Status：

READY_FOR_WORK_PACKAGE_PREPARATION。

Runtime Launch Gate：

NOT_RELEASED。

Runtime Authorization：

NOT_YET_AUTHORIZED。

Frozen safety：

- deterministic collection matching only。
- explicit ExternalStateUnknownError boundary。
- no catch-all downgrade。
- strategy_state_ready explicit dependency。
- no silent expected overwrite。
- no automatic broker repair。
- no automatic corrective OrderIntent。
- no persistence implementation。

Closure rule：

Parent GAP closes only after GAP-RECON-001B acceptance。


# GAP-08 Detail

Target：

- PostgreSQL operational SOR。
- Order persistence。
- OrderEvent persistence。
- Fill persistence。
- Position snapshots。
- Account snapshots。
- trading event history。
- idempotency。
- strategy state snapshot。
- restart recovery。
- broker reconciliation after restart。

---

# GAP-09 Detail

Target：

Incremental Feature / Market State。

Paper/live：

不得每根 bar 重新運算整份 historical dataset。

---

# GAP-LIVE-001 Detail

Before LIVE_AUTO：

- authorization。
- time bound。
- account scope。
- symbol scope。
- loss limits。
- position limits。
- suspension。
- reconciliation health。
- stale-data guard。
- manual override。
- force-flat。
- kill switch。
- audit。
- production verification matrix。

Status：

LIVE BLOCKER。

---

# New GAP Rule

新問題若非 current blocker：

先記錄。

不得立即產生新的 implementation stage。

只有：

- current correctness。
- safety。
- mandatory dependency。

才可以插入 mainline。
