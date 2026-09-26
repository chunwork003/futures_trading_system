# Current State

## Canonical CURRENT Governance Projection — GOV-01

**CURRENT GOVERNANCE PROJECTION — CANONICAL**

This section is the single canonical CURRENT runtime/planning projection。

Other governance/work documents may summarize or reference this state，but they do not independently establish runtime authorization。

### Baseline Separation

Architecture Decision Baseline：`22ceaa729ab6e9da9c00ae52e09ae7116be5a743`。

This remains the Decision Checkpoint 5E architecture baseline。

Governance Planning Baseline：`f45742d9d16165f87f145f0d2bdc8d530772e5ee`（GOV-01）。

Current Correction-Freeze Baseline：`93fb846a9c9cd61eea44427a86a542fc95f9ac28`。

The exact Correction-Freeze commit hash is reported after commit/push and becomes the execution-planning baseline for any later bounded Runtime Authorization。

Runtime Candidate：`6b62239bca1d11543944f9f078e577e16010bcbf`。

Runtime candidate != authorized runtime baseline。

Planning acceptance != Architecture Decision Checkpoint != Runtime Authorization。

### Current Governance State

- Architecture Acceptance：HOLD。
- Runtime Conformance：NOT ASSERTED。
- Production Readiness：NOT ASSERTED。
- Runtime Authorization：NOT_AUTHORIZED。
- Runtime modification：NOT_AUTHORIZED。
- Broker I/O：NOT_AUTHORIZED。
- DB migration execution：NOT_AUTHORIZED。
- Level 3B：NOT_ENABLED。

### Latest Bounded Runtime Execution Result

Authorization record：

`docs/work/GAP08_AUTHORIZATION_V06_C01.md`

Execution closure：

`docs/work/GAP08_C01_CLOSURE.md`

V06：

- COMPLETE / PASS。
- 14 passed。

C01：

- COMPLETE / VERIFIED。
- runtime commit：`eb8e7bc8df4fc9b4fc6dfc9c62ce593a0b5f4ff9`。
- targeted：13 passed。
- compatibility：58 passed。
- full regression：944 passed / 4 skipped。
- correction cycles：1。
- bounded rewrite：YES。

Completed / verified correction-core weight：

7 / 113。

Remaining correction-core engineering weight：

106。

No additional runtime leaf is authorized。

Next candidate：

C22 — Canonical Time Evidence Correction。

C22 remains NOT_AUTHORIZED until a new explicit bounded authorization checkpoint。

### POST-5E ACCEPTED PLANNING INPUTS

The following post-5E items were ACCEPTED PLANNING INPUTS and are now materialized into the docs-only Correction-Freeze Work Package；they remain planning inputs and are NOT a new Architecture Decision Baseline。

They are NOT a new Architecture Decision Baseline and do NOT grant Runtime Authorization。

K520：

- DEFER CONFIRMED。
- GAP-09 OWNED。
- CONDITIONAL_PRODUCTION_DEPENDENCY。
- GAP-08_FAIL_CLOSED_ENFORCEMENT_REQUIRED。
- K520_NOT_APPLICABLE requires positive proof under the exact governing StrategyInstance recovery contract。

BG-01～BG-07：

- CLASSIFICATION CLOSED FOR CORRECTION-FREEZE PLANNING。
- implementation work、capability verification and production-gate state remain distinct。
- PAPER_VERIFIED != PRODUCTION_VERIFIED。

Expanded Correction-Scope Map：

- ARCHITECTURALLY CLOSED for correction-freeze planning。
- no R-01～R-14 / K520 / BG-01～BG-07 reopen without concrete contradiction or new authoritative evidence。

Delta-to-Contract：

- FROZEN PLANNING RULE。
- architecture scope size != runtime correction size。
- KNOWN_CONFORMANT requires exact positive evidence against the exact Frozen Contract Assertion。
- no defect found != KNOWN_CONFORMANT。
- historical test pass != current frozen-contract conformance。
- insufficient evidence defaults to UNKNOWN_CONFORMANCE。

Planning materialization：

    Frozen Contract Assertion Inventory
        -> Evidence / Delta Classification
        -> Derived Disposition
        -> materialize only required
           Engineering / Correction / Conformance / Verification leaves

Disposition is planning metadata only；it is not an independent authority state。

Production Gate is evidence-dependent status metadata and has no coding weight；evidence-producing verification work may have engineering weight。

DB-CONF-01：

- DB-CONF-01A = Repository Persistence Baseline Verification。
- DB-CONF-01B = Actual Environment Conformance Verification。
- unavailable actual DB != correction code cannot be written。
- unknown actual DB => no environment-conformance claim and no blind migration。

Correction-Freeze Decision Checkpoint：COMPLETE / DOCS-ONLY。

Authoritative execution-planning detail：

`docs/work/GAP08_CORRECTION_FREEZE.md`

Reweighted bounded correction core：

- C01～C25：weight 110。
- V06 repository persistence verification：weight 3。
- bounded correction core：weight 113。
- original candidate 151 + bounded correction core 113 = 264。
- separate V01～V05 broker capability verification：weight 19。
- mapped envelope excluding actual DB environment verification：283。
- V07 actual PostgreSQL environment conformance：weight 4 conditional。
- maximum mapped envelope when V07 is explicitly scoped：287。

The Correction-Freeze checkpoint itself granted no runtime authority；the later bounded authorization is limited to V06 + C01 as recorded in `docs/work/GAP08_AUTHORIZATION_V06_C01.md`。

The existing 47.92% remains the recorded architecture-freeze lifecycle baseline；this docs-only planning checkpoint does not claim new acceptance percentage。

### Current Planning / Execution Sequence

1. V06 + C01 closure is recorded in `docs/work/GAP08_C01_CLOSURE.md`。
2. No runtime leaf is currently authorized。
3. Next candidate leaf is C22 — Canonical Time Evidence Correction。
4. Review and create a new explicit bounded authorization envelope before C22。
5. C11、C02 and all other leaves remain NOT_AUTHORIZED。
6. No migration execution、actual PostgreSQL access or broker I/O is authorized。
A future authorization decision must identify at least：Authorization Baseline、Authorized Leaf Set、Runtime Modification Scope、Excluded/Deferred Scope、Environment Scope、DB/Broker side-effect permissions、Capability Verification modes、Required Tests and Stop Boundary。

A bare `AUTHORIZED` value is insufficient。

---

All older runtime-launch/current-work snapshots below are historical evidence unless explicitly identified as part of this canonical CURRENT projection。

## Repository Baseline

Repository：

`futures_trading_system`

Branch：

`master`

Architecture baseline：

`771f10f`

GAP-ACCOUNT-001 execution authorization baseline：

`5e24960`

Actual runtime execution HEAD：

由每次 Work Package precheck 取得。

本文件不保存「精確 current HEAD」，避免 documentation commit 造成自我參照與立即 stale。

Recorded full regression：

934 passed / 4 skipped

Known warning：

1 PytestCacheWarning / GAP-ENV-001。

Known local untracked：

`data/`

`data/` 不得自動 stage。

---

## Blueprint Baseline

Status：

AUTHORITATIVE。

Baseline commit：

`432c48fb63c3d8d2760c0f2f5338e205ded63d30`

Engineering inventory：

- A～O V1 Domains。
- 603 engineering leaves。
- total weight 2137。
- Blueprint IDs / source / authority / traceability / metrics 已啟用。

GAP-ACCOUNT-001：

COMPLETED / ACCEPTED。

Accepted runtime commit：

`50813b679f818f3837a9f50fdcda9921495ab507`

Blueprint launch gate 已完成使命，不再阻塞 runtime。

## Historical Phase Snapshot — SUPERSEDED BY GOV-01 CURRENT PROJECTION

Current milestone：M6 — Persistence / Recovery / Provenance。

GAP-08ABCD：COMPLETED / ACCEPTED。

Current Work Package：GAP-08EFGHI — Operational Persistence + Recovery。

Original blueprint runtime scope：35 leaves / weight 151。

Runtime implementation：COMPLETED_CANDIDATE。

Runtime commit：`6b62239bca1d11543944f9f078e577e16010bcbf`。

Runtime verification：934 passed / 4 skipped / 1 warning。

Architecture acceptance：HOLD。

Runtime Authorization：NOT_AUTHORIZED_FOR_FURTHER_EXECUTION。

Decision Checkpoint 4 baseline：

`11ead24d4f09ead611243c19aab982f09756f172`

Architecture decisions：

- R-01：DECIDED / CORRECTION_REQUIRED。
- R-02：DECIDED / CORRECTION_REQUIRED。
- R-03A/B/C/D：DECIDED / CORRECTION_REQUIRED。
- R-03 overall：DECIDED。
- R-04A/B/C/D/E/F/G/H：DECIDED / CORRECTION_REQUIRED。
- R-04 overall：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

R-04 broker capability gates remain implementation/production authorization requirements and do not reopen architecture。

Linked dependencies：

- R-12 ReconciliationRun audit contract。
- R-13 Operator Authorization / Approval Runtime Contract。
- R-14 / GAP-DATA-001 operational market-data completeness / gap detection。
- K520 incremental feature/state provenance remains GAP-09-owned。

Expanded correction scope from R-03/R-04 is outside the original 35 / 151 implementation candidate and is not yet lifecycle-weighted。

Correction freeze must explicitly map at least：

- MarketObservation revision/value-object and operational evidence persistence。
- broker_client_order_ref exact correlation contract。
- BrokerOrderStateProvider restart discovery。
- BrokerActionAttempt / BrokerActionResolution / BrokerActionHead。
- BrokerDiscoveryObservation / ExecutionContinuityEpoch。
- broker report durable inbox/application semantics。
- restart-stable BrokerDealIdentity / Fill reconstruction capability。
- AccountRecoveryControl / recovery cut / race-free handoff。
- shared AccountAuthorityCommit primitive。
- SideEffectSafetyGate。
- BrokerAccount READY / REVIEW / HALT aggregation。

Launch Gate：HOLD_FOR_BOUNDED_CORRECTION_FREEZE。

35 / 151 remains IMPLEMENTED CANDIDATE / NOT ACCEPTED。

Official lifecycle metric remains the 47.92% architecture-freeze baseline until correction scope is reweighted and final acceptance is rebased。

Level 3B：NOT_ENABLED。

## Existing Major Foundation

已完成或高度成熟：

- historical ingestion。
- validation / cleaning。
- bar aggregation。
- Parquet / DuckDB analytical layer。
- trading calendar foundation。
- batch features。
- strategy framework。
- deterministic backtest。
- LONG / SHORT。
- SL / TP。
- commission / slippage。
- analysis / optimization。
- OOS / WFO。
- Monte Carlo。
- paper trading。
- async order lifecycle。
- partial entry / exit。
- strategy virtual positions。
- conflict resolution。
- TargetAccountPosition。
- attribution / netting。
- direction-change wait-for-flat。
- portfolio risk。
- position sizing。
- capital management。
- Shioaji adapter foundation。
- InstrumentSpec。
- ContractSpec。
- TradingSessionRef。
- MarginSchedule。
- BrokerInstrumentReference。
- actual canonical multiplier consumer。
- actual canonical margin consumer。
- BrokerAccount。
- canonical internal AccountPosition foundation。
- BrokerPositionSnapshot。
- read-only broker account / position query ports。
- Sinopac pure account / position mapping。
- broker contract reverse resolution。
- pure expected / actual pairwise reconciliation foundation。
- ReconciliationResult / policy / case lifecycle。
- deterministic multi-position collection reconciliation。
- startup reconciliation readiness gate。
- broker-neutral OrderIntent。
- PositionEffect OPEN / REDUCE / CLOSE。
- pure PositionEffect validation。
- explicit Shioaji Buy / Sell + New / Cover mapping。
- order-ID New/Cover inference removed。

---

## Critical Missing V1

主要剩餘：

- AccountPosition fill/event projection。

- operational PostgreSQL。
- trading persistence。
- restart recovery。
- decision/risk provenance。
- incremental feature state。
- SimulationBroker。
- LIVE authorization / safety。
- Python service API。
- ASP.NET Core Application。
- React Workspace。
- operational review / audit。

## Progress

Total V1 capability blocks：

92。

Engineering leaves：

603。

+

47.92%。

Architecture Design Coverage：87.60%。
Design Freeze Coverage：52.22%。
Runtime Implementation：39.59%。
Unit Verification：36.36%。
Integration Verification：36.27%。
Accepted Capability：36.27%。

Capability status：

COMPLETE 12 / PARTIAL 49 / NOT_STARTED 31。

Readiness：

- Operational：NOT_READY。
- Production Live：BLOCKED。
- LIVE_AUTO：NOT_AUTHORIZED。

Latest accepted runtime：

`98dc38ce39bdab191ce0bc6d71e37ef69059ec9c`

## Automation Status

### Level 1

Manual Work Package relay。

Validated。

### Level 2

Bounded autonomous bundle。

Validated by GAP-07-CLOSE。

### Level 3A

Repository queue + ACTIVE full Work Package。

Formal runtime calibration samples：7。

Completed runtime samples：

- GAP-ACCOUNT-001：12%。
- GAP-BROKER-001：14%。
- GAP-RECON-001A：11%。
- GAP-RECON-001B：16%。
- GAP-BROKER-002：10%。
- GAP-08ABCD：12%。
- GAP-08EFGHI：28%。

Observed average 5HR usage：14.71%。

Total implementation correction cycles：4。

GAP-08EFGHI runtime test result is PASS but architecture acceptance is HOLD；this sample is retained for sizing calibration。

### Level 3B

Continuous autonomous queue execution。

ELIGIBLE_FOR_EVALUATION。

NOT_ENABLED。

Persistence/recovery mainline 不因 Level 3A 樣本數自動升級 Level 3B。

---

## Automation Efficiency Observation

Formal Level 3A runtime samples：

| Sample | Work Package | 5HR | Files Read | Files Changed | Tool Ops | Corrections | Regression |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | GAP-ACCOUNT-001 | 12% | 8 | 12 | 18 | 0 | 776 |
| 2 | GAP-BROKER-001 | 14% | ~22 | 20 | 24 | 0 | 800 |
| 3 | GAP-RECON-001A | 11% | 8 | 2 | 19 | 0 | 821 |
| 4 | GAP-RECON-001B | 16% | 8 | 2 | 22 | 1 | 847 |
| 5 | GAP-BROKER-002 | 10% | 12 | 3 | 17 | 0 | 869 |
| 6 | GAP-08ABCD | 12% | 8 | 15 | 23 | 1 | 897 |

Six-sample average：

12.50%。

Total implementation correction cycles：

2。

Sample 6：

- expanded bundle：19 leaves / weight 77。
- wall time：約 12m09s。
- retries：1。
- PG17 / PG18 integration：PENDING。
- token/context：UNAVAILABLE。

Observation：

larger coherent scope did not increase observed 5HR usage；however wall time / tool operations / correction behavior remain part of sizing evaluation。

Policy：

- do not target a fixed quota percentage。
- merge same-context work when semantics permit。
- split only at genuine public-semantics / authority / safety / external-verification seams。

## Live State

Real-money LIVE_AUTO：

NOT AUTHORIZED。

原因：

Persistence、Recovery、Live Safety 尚未完成。

---

## Historical Runtime Launch Snapshot — SUPERSEDED

Work Package：

GAP-08EFGHI Operational Persistence + Recovery。

Status：READY_FOR_EXECUTION。

Blueprint：35 leaves / weight 151。

Runtime Gate：RELEASED_ARCHITECTURE_FREEZE。

Runtime authorization：AUTHORIZED_FOR_LEVEL_3A_RUNTIME。

Execution Mode：LEVEL_3A_BOUNDED。

Recommended model：GPT-5.6 Sol / 中度。

Reason for 中度：

single bundle now crosses execution state machine、multi-table transaction、account reconciliation、strategy state reconstruction and recovery safety。

No runtime until freeze commit/push is verified。

## Historical Decision Checkpoint 5A State — SUPERSEDED AS CURRENT PROJECTION

Architecture Decision Status：

- R-01：DECIDED / AMENDED。
- R-02：DECIDED / AMENDED。
- R-03：DECIDED / UNCHANGED。
- R-04：DECIDED / AMENDED。
- R-05：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

R-05 final contract：Read + Validate + Explicit Result；Coherent Complete RecoveryCut；validated transitive recovery dependency closure；positive baseline proof；deterministic projection validation anchors；staged RecoveryExecutionContext。

Runtime candidate remains：`6b62239bca1d11543944f9f078e577e16010bcbf`。

Runtime conformance to these decisions is NOT asserted。

Runtime Authorization：NOT_AUTHORIZED。

Architecture Acceptance：HOLD。

Next architecture work：R-06 + R-07 Recovery Boundary Cluster。

## Historical Decision Checkpoint 5B State — SUPERSEDED AS CURRENT PROJECTION

Architecture Decision Status：

- R-01：DECIDED / AMENDED。
- R-02：DECIDED / AMENDED。
- R-03：DECIDED / UNCHANGED。
- R-04：DECIDED / AMENDED。
- R-05：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-06：DECIDED。
- R-07：DECIDED。

R-06 freezes StrategyInstance-scoped recovery、multi-frontier recovery evidence、positive fresh/stateless authority、exact governing policy continuity、decision-cohort readiness and startup catch-up isolation。

R-07 freezes BrokerAccount-scoped ReconciliationCase ownership、V1 BrokerAccount isolation floor、account-scoped readiness evaluation and non-economic case authority。

Runtime candidate remains：`6b62239bca1d11543944f9f078e577e16010bcbf`。

Runtime conformance is NOT asserted。

Runtime Authorization：NOT_AUTHORIZED。

Architecture Acceptance：HOLD。

Next architecture work：R-08 + R-09 identity/config authority cluster。

## Historical Decision Checkpoint 5C State — SUPERSEDED AS CURRENT PROJECTION

- R-08：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-09：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-01 through R-09 architecture decision sequence is now closed except R-10/R-11 and linked later follow-ups。
- Runtime candidate remains：`6b62239bca1d11543944f9f078e577e16010bcbf`。
- Runtime conformance：NOT ASSERTED。
- Production readiness：NOT ASSERTED。
- Runtime Authorization：NOT_AUTHORIZED。
- Architecture Acceptance：HOLD。
- Next：R-10 formal closure -> R-11 clock authority。

## Historical Decision Checkpoint 5D State — SUPERSEDED AS CURRENT PROJECTION

- R-10：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-11：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-01 through R-11 architecture decisions are closed；R-12 and later linked boundaries remain。
- Runtime candidate remains：`6b62239bca1d11543944f9f078e577e16010bcbf`。
- Runtime conformance：NOT ASSERTED。
- Production readiness：NOT ASSERTED。
- Runtime Authorization：NOT_AUTHORIZED。
- Architecture Acceptance：HOLD。
- Next：R-12 ReconciliationRun audit contract。

## Historical Decision Checkpoint 5E State — ARCHITECTURE RECORD

- R-12：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-13：DECIDED / BOUNDARY_CLASSIFIED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-14：DECIDED / BOUNDARY_CLASSIFIED / GAP-08_ENFORCEMENT_CORRECTION_REQUIRED / GAP-DATA-001_DEFERRED_PRODUCTION_DEPENDENCY。
- No R-12I / R-13I / R-14I。
- Recovery decisions R-01 through R-14 are now closed/classified for the current correction-freeze preparation phase。
- Runtime candidate remains：`6b62239bca1d11543944f9f078e577e16010bcbf`。
- Candidate commit is not an authorized runtime baseline。
- Runtime conformance：NOT ASSERTED。
- Production readiness：NOT ASSERTED。
- Runtime Authorization：NOT_AUTHORIZED。
- Architecture Acceptance：HOLD。
- Correction Expansion：RECORDED / NOT YET REWEIGHTED。
- Next：K520 defer confirmation，then broker capability gate classification。
