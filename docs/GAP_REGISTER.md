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
| GAP-RECON-001 | P1 | REVIEW_AT_CHECKPOINT | No | Reconciliation / startup readiness | CLOSED |
| GAP-BROKER-001 | P1 | REVIEW_AT_CHECKPOINT | No | Explicit OrderIntent / PositionEffect | CLOSED |
| GAP-BROKER-002 | P2 | REVIEW_AT_CHECKPOINT | No | Capability matrix / mapping semantics | CLOSED |
| GAP-08 | P1 | REVIEW_AT_CHECKPOINT | Yes — acceptance | Trading State Persistence / Recovery | IN_PROGRESS / ARCHITECTURE_ACCEPTANCE_HOLD |
| GAP-PERSIST-001 | P1 | RECORD_AND_CONTINUE | No | Decision / Risk Provenance | OPEN |
| GAP-09 | P1 | REVIEW_AT_CHECKPOINT | No | Incremental Feature / Market State | PENDING |
| GAP-DATA-001 | P1 | RECORD_AND_CONTINUE | No; Production Live blocker later | Operational market-data completeness / gap detection | OPEN |
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

CLOSED / ACCEPTED。

Architecture / Design Freeze：

COMPLETED for J610-J780。

GAP-RECON-001A：

COMPLETED / ACCEPTED。

Runtime commit：

`d7dbd884f09e72d7737726409e11e0679206ed8d`

GAP-RECON-001B：

COMPLETED / ACCEPTED。

Runtime commit：

`4049f982474454556baf8734a5729ecbedc7a438`

Accepted scope：

- J610-J780。
- reconciliation result / policy / case。
- UNKNOWN_EXTERNAL_STATE。
- deterministic collection matching。
- startup expected/actual orchestration。
- READY / HALT / REVIEW gate。
- explicit strategy-state readiness dependency。
- no automatic corrective action。
- no silent startup repair。

Final verification：

- 001A full regression：821 passed。
- 001B targeted：58 passed。
- 001B compatibility：22 passed。
- 001B full regression：847 passed。

Persistence/recovery implementation remains GAP-08。

Corrective broker execution remains separately gated。

---

# GAP-BROKER-002 Detail

Status：

CLOSED / ACCEPTED。

Accepted runtime commit：

`7d7fdabcb99da59d3d23ccec62b11c6572ceea82`

Accepted Blueprint scope：

- I120。
- I130。
- I140。
- I940。

Accepted runtime：

- broker-neutral capability contract。
- support / verification mode contract。
- capability evidence/matrix。
- explicit unsupported/unverified failure。
- Sinopac documentation-only evidence matrix。

Verification：

- targeted：22 passed。
- compatibility：45 passed。
- full regression：869 passed。
- correction cycles：0。

Still deferred：

- I720 authentication。
- I730 reconnect/session recovery。
- I740 live account-selection enforcement。
- I820 network/broker error classification。
- I920 actual broker paper/simulation verification。
- I930 production connectivity verification。

Capability evidence does not authorize LIVE。

---


# GAP-08 Detail

Status：IN_PROGRESS / ARCHITECTURE_ACCEPTANCE_HOLD。

Accepted：

GAP-08ABCD Persistence Foundation + Event Ledger。

GAP-08EFGHI runtime candidate：

`6b62239bca1d11543944f9f078e577e16010bcbf`

Runtime verification：934 passed / 4 skipped / 1 warning。

User-observed 5HR usage：28%。

Blueprint scope：35 leaves / weight 151。

Runtime code is retained，but 35 / 151 is NOT ACCEPTED。

Post-runtime architecture review decision checkpoint：

- R-01 expected-state initialization/read semantics：DECIDED / CORRECTION_REQUIRED。
- R-02 account checkpoint/causal frontier：DECIDED / CORRECTION_REQUIRED。
- R-03A market observation logical key：DECIDED / CORRECTION_REQUIRED。
- R-03B market observation revision/content identity：DECIDED / CORRECTION_REQUIRED。
- R-03C revision ID/value-object contract：DECIDED / CORRECTION_REQUIRED。
- R-03D cross-environment/source authority：DECIDED / CORRECTION_REQUIRED。
- R-03 overall：DECIDED。
- R-04 overall：IN_PROGRESS / mandatory dependency。
- R-04A broker order discovery authority：DECIDED / CORRECTION_REQUIRED。
- R-04B durable broker correlation identity：DECIDED / CORRECTION_REQUIRED / capability gate。
- R-04C discovery classification / BrokerActionAttempt：DECIDED / CORRECTION_REQUIRED。
- R-04D discovery health / execution continuity：DECIDED / CORRECTION_REQUIRED。
- R-04E canonical execution reconstruction：DECIDED / CORRECTION_REQUIRED / capability gates remain。
- R-04F / R-04G / R-04H：OPEN。
- R-14 / GAP-DATA-001 market-data completeness/gap detection：OPEN / future production safety dependency。

Post-R-03 correction scope expansion：

- MarketObservation logical/revision canonical contract。
- deterministic mor1 revision identity / golden vectors。
- storage-neutral MarketObservationRevision operational persistence。
- PostgreSQL operational observation evidence adapter。
- candidate/provenance conflict/quarantine evidence。
- durable accepted observation before strategy delivery。
- derived-observation provenance。

This scope was not part of the original 35 leaves / weight 151 implementation candidate。

No new lifecycle weight is claimed yet；the correction Work Package must map/reweight it before runtime authorization。

Post-R-04A-E correction scope expansion：

- BrokerOrderStateProvider / authoritative account-scoped order discovery。
- broker_client_order_ref in durable sequence-0 PENDING authority boundary。
- BrokerActionAttempt / BrokerActionResolution / BrokerActionHead。
- BrokerDiscoveryObservation / DiscoveryCompleteness / ExecutionContinuityEpoch。
- BrokerReportInboxEntry / BrokerReportApplication。
- AccountRecoveryControl durable recovery fence。
- AccountAuthorityCommitReceipt / stable mutation fingerprint。
- AccountAuthorityCommitService or equivalent shared account-authority UoW。
- recovery OrderEvent / Fill / Order projection / expected snapshot / checkpoint atomic commit。
- terminal economic sealing and Fill-set economic authority。

R-04A-E scope was not part of the original 35 leaves / weight 151 implementation candidate。

No lifecycle weight is claimed yet。

Production capability gates：

- Shioaji client correlation round-trip verification。
- exact restart-stable FillKey verification。
- pinned event-id/tracking capability verification。
- PreSubmitted / Inactive / relevant Failed status semantics。
- quantity-modification recovery remains default-deny。

R-13 remains mandatory for high-risk manual unresolved-action clearance/retry。

Detailed authoritative record：

`docs/adr/ADR-002-RECOVERY-CONSISTENCY-MARKET-OBSERVATION.md`

Runtime Launch Gate：HOLD_FOR_POST_RUNTIME_ARCHITECTURE_DECISIONS。

Runtime Authorization：NOT_AUTHORIZED_FOR_FURTHER_EXECUTION。

K520：DEFERRED_TO_GAP_09。

PG17 / PG18：PENDING。

Parent GAP cannot close until the correction Work Package is frozen、implemented、verified and accepted。

# GAP-DATA-001 Detail

Related decision：R-14 — Market Data Completeness / Gap Detection。

Priority：P1。

Handling：RECORD_AND_CONTINUE。

Current blocker：No for the current R-03 identity decision/correction design；required before claiming production-live market-data completeness safety。

Problem：

A missing candidate observation is not equivalent to a quarantined candidate and is not evidence of a legitimate no-trade interval。

The system must eventually distinguish at least：

- legitimate no-trade interval。
- non-trading/session/calendar interval。
- source outage。
- transport failure。
- ingestion/data loss。

Until session/calendar-aware completeness detection exists，continuous-interval features/strategies may not silently treat absence as a valid empty market interval。

Blueprint relation：B250 / B720 / D340 / K520。

R-03 remains DECIDED；this GAP is a separate follow-up。

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
