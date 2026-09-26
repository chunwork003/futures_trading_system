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

Status：IN_PROGRESS / ARCHITECTURE_ACCEPTANCE_HOLD / CORRECTION_FREEZE_COMPLETE / V06_C01_C22_C11_COMPLETE / C23_BOUNDED_AUTHORIZED。

Accepted：

- GAP-08ABCD Persistence Foundation + Event Ledger。

GAP-08EFGHI runtime candidate：

`6b62239bca1d11543944f9f078e577e16010bcbf`

Runtime verification：934 passed / 4 skipped / 1 warning。

Original blueprint scope：35 leaves / weight 151。

Original runtime candidate remains IMPLEMENTED CANDIDATE / NOT ACCEPTED。

Correction-Freeze planning package：

`docs/work/GAP08_CORRECTION_FREEZE.md`

Latest bounded execution：

`docs/work/GAP08_C11_CLOSURE.md`

Completed / verified leaves：

- V06 — COMPLETE / PASS。
- C01 — COMPLETE / VERIFIED。
- C22 — COMPLETE / VERIFIED。
- C11 — COMPLETE / VERIFIED。

Latest runtime commit：

`a2a54fa74152d720d42e39b211c1b80991496fa1`

C11 verification：

- targeted：23 passed。
- Shioaji compatibility：47 passed。
- full regression：959 passed / 4 skipped。
- runtime correction cycles：0。

V05：

NOT EXECUTED / NOT VERIFIED。

Installed Shioaji observation：

1.7.5 enum surface observed locally；no broker-semantic verification claim。

Executed / verified correction-core weight：

13 / 113。

Remaining correction-core engineering weight：

100。

Runtime Authorization：

NOT_AUTHORIZED。

Frozen DAG recheck：

    P1
        C01 COMPLETE
        -> C22 COMPLETE
        -> C11 COMPLETE

P1：

COMPLETE。

Next frozen phase：

    P2
        C23
        -> C24
        -> C25

Next candidate：

C23 — Canonical MarketObservation Identity + Revision。

C23：

BOUNDED_AUTHORIZED_C23_ONLY。

C24：

BLOCKED_ON_C23。

C25：

BLOCKED_ON_C24。

V05：

NOT_AUTHORIZED。

Only C23 is currently authorized；C24、C25、C02、V05 and all other leaves remain NOT_AUTHORIZED。

Migration execution：

NOT_AUTHORIZED。

Actual PostgreSQL access：

NOT_AUTHORIZED。

Broker I/O：

NOT_AUTHORIZED。
Reweight：

- C01～C25 correction/implementation/enforcement：110。
- V06 repository persistence verification：3。
- bounded correction core：113。
- original candidate 151 + bounded correction core 113 = 264。
- V01～V05 broker capability verification：19 separate。
- full mapped envelope excluding environment-specific V07：283。
- V07 actual PostgreSQL environment conformance：4 conditional。
- maximum mapped envelope when V07 is explicitly scoped：287。

Architecture decision status：

- R-01：DECIDED / CORRECTION_REQUIRED。
- R-02：DECIDED / CORRECTION_REQUIRED。
- R-03A/B/C/D：DECIDED / CORRECTION_REQUIRED。
- R-03 overall：DECIDED。
- R-04A/B/C/D/E/F/G/H：DECIDED / CORRECTION_REQUIRED。
- R-04 overall：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

R-04 capability gates remain implementation/production authorization requirements。

Post-runtime correction expansion includes MarketObservation operational evidence、restart broker discovery/correlation、BrokerActionAttempt lifecycle、broker evidence continuity、canonical Fill reconstruction、recovery concurrency fencing、shared AccountAuthorityCommit and BrokerAccount readiness aggregation。

This expanded scope remains outside the original 35 / 151 candidate and is now separately materialized、deduplicated and reweighted；it is not hidden inside the previous weight。

Linked dependencies/follow-ups：

- R-12 ReconciliationRun audit。
- R-13 operator authorization/approval；production manual resolution default-deny until implemented。
- R-14 / GAP-DATA-001 market-data completeness/gap detection。
- K520 incremental feature/state provenance remains GAP-09-owned。

Detailed authoritative record：

`docs/adr/ADR-002-RECOVERY-CONSISTENCY-MARKET-OBSERVATION.md`

Runtime Launch Gate：AUTHORIZED_FOR_C23_ONLY。

Runtime Authorization：BOUNDED_AUTHORIZED_C23_ONLY。

Parent GAP cannot close until the frozen correction package is explicitly authorized、implemented、verified and finally accepted；production capability gates remain evidence-dependent。

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

## Decision Checkpoint 5A — Recovery Decision Ledger

- R-01：DECIDED / AMENDED / runtime correction still required where implementation drifts。
- R-02：DECIDED / AMENDED / runtime correction required。
- R-03：DECIDED / UNCHANGED / existing correction expansion remains unweighted。
- R-04：DECIDED / AMENDED / broker capability gates remain。
- R-05：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

New decision status does not change Architecture Acceptance from HOLD。

Original 35 leaves / weight 151 remain IMPLEMENTED CANDIDATE / NOT ACCEPTED。

Post-R-03/R-04/R-05 correction expansion remains RECORDED / NOT YET REWEIGHTED。

Next decision work：R-06 + R-07。

No runtime correction is authorized。

## Decision Checkpoint 5B — R-06 / R-07 Closure

- R-06 Multi-strategy recovery boundary：DECIDED。
- R-07 ReconciliationCase BrokerAccount scope：DECIDED。
- R-08 StrategyInstance instrument vs symbol identity：OPEN / NEXT。
- R-09 strategy_instance_id / config_version / lifecycle authority：OPEN / NEXT。

R-06 intentionally depends on R-09 for exact StrategyInstance/config/policy-version identity and authorized migration authority。

R-07 does not replace R-12 ReconciliationRun audit contract or R-13 manual authorization contract。

Architecture Acceptance remains HOLD。

Original 35 leaves / weight 151 remain IMPLEMENTED CANDIDATE / NOT ACCEPTED。

Correction expansion remains RECORDED / NOT YET REWEIGHTED。

No runtime implementation is authorized。

## Decision Checkpoint 5C — R-08 / R-09 Closure

- R-08 StrategyInstance instrument vs symbol identity：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-09 strategy_instance_id / config_version / implementation revision / lifecycle authority：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- No R-08E / R-09G added。
- Existing E/G Blueprint wording was reconciled to the final authority model。
- Correction expansion remains RECORDED / NOT YET REWEIGHTED。
- Runtime Authorization remains NOT_AUTHORIZED。
- Next：R-10 formal closure，then R-11。

## Decision Checkpoint 5D — R-10 / R-11 Closure

- R-10 initial expected-state provenance：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-11 operational clock/timestamp authority：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- No R-10E / R-11I added。
- Superseded R-01 initialization wording in ADR-002 reconciled。
- Correction expansion remains RECORDED / NOT YET REWEIGHTED。
- Runtime Authorization remains NOT_AUTHORIZED。
- Next：R-12，then R-13 / R-14 boundary classification。

## Decision Checkpoint 5E — R-12 / R-13 / R-14 Closure

- R-12：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-13：DECIDED / BOUNDARY_CLASSIFIED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-14：DECIDED / BOUNDARY_CLASSIFIED / GAP-08_ENFORCEMENT_CORRECTION_REQUIRED / GAP-DATA-001_DEFERRED_PRODUCTION_DEPENDENCY。
- No R-12I / R-13I / R-14I。

R-13 classification：
- GAP-08 correction dependency：core authorization-required enforcement seam、production default deny、durable protected-action attribution、production/non-production authority distinction。
- Production gate/deferred implementation：full N authN/authZ/approval + L/GAP-LIVE workflow。

R-14 classification：
- GAP-08 correction dependency：authoritative completeness-required seam + fail-closed dependent Strategy/Cohort readiness。
- Deferred production dependency：GAP-DATA-001 full session/calendar-aware detector、coverage/failure monitoring、outage classification and production completeness operations。
- GAP-DATA-001 Current Blocking remains No for GAP-08 bounded correction。
- GAP-DATA-001 remains required before production dependent Strategy/Cohort TradingReady where completeness authority is mandatory。

Mandatory anti-misread：
    R-13 production auth runtime not implemented != authorization requirement waived
    R-14 full completeness detector deferred != completeness requirement waived

K520 remains GAP-09-owned。
Correction expansion remains RECORDED / NOT YET REWEIGHTED。
Runtime Authorization remains NOT_AUTHORIZED。

Next：K520 defer confirmation -> broker capability gate classification -> correction scope map/reweight。
