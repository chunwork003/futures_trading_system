# Current Work

## GOV-01 Current Work Projection Guard

`docs/CURRENT_STATE.md` is the canonical CURRENT runtime/planning governance projection。

This document records planning/work state only and does NOT independently establish Runtime Authorization。

Runtime Authorization summary：NOT_AUTHORIZED。

Architecture Decision Baseline：`22ceaa729ab6e9da9c00ae52e09ae7116be5a743`。

Governance Planning Baseline：`f45742d9d16165f87f145f0d2bdc8d530772e5ee`；Correction-Freeze Baseline：`93fb846a9c9cd61eea44427a86a542fc95f9ac28`；latest bounded execution closure：`docs/work/GAP08_WAVE1_CLOSURE.md`。

Post-5E accepted planning inputs、materialized leaves、DAG、bounded rewrite policy and reweight are frozen in `docs/work/GAP08_CORRECTION_FREEZE.md`。

Current execution action：W1 is CLOSED / ACCEPTED；build exact W2 execution package and verify execution coherence only。W2 runtime source modification remains NOT_AUTHORIZED。

## Purpose

本文件只保存：

- Current work。
- Mainline queue。
- Dependencies。
- Blocking relation。

完整產品功能：

`V1_CAPABILITY_MAP.md`

完整工程拆解：

`V1_SYSTEM_BLUEPRINT.md`

完整 architecture：

`ARCHITECTURE.md`

Technical issues：

`GAP_REGISTER.md`

完整 Work Package：

`work/ACTIVE.md`

---

# Current Active Candidate

Parent GAP：GAP-08

Work Package：GAP-08EFGHI

Title：Operational Persistence + Recovery

Priority：P1 MAINLINE

Runtime implementation：COMPLETED_CANDIDATE

Runtime commit：`6b62239bca1d11543944f9f078e577e16010bcbf`

Runtime tests：PASS — 934 passed / 4 skipped / 1 warning

Architecture acceptance：HOLD

Current activity：WAVE_2_EXECUTION_COHERENCE_PLANNING
Runtime Authorization：NOT_AUTHORIZED
Launch Gate：NOT_AUTHORIZED
## Latest Completed Correction Leaves

Previously completed / verified：

- V06。
- C01。
- C22。
- C11。
- C23。
- C24。
- C25。

GAP08-W1：

COMPLETE / VERIFIED / REVIEWER_ACCEPTED / CLOSED。

Accepted W1 leaves：

- C02。
- C04。
- C21。
- C03。

Closure：

`docs/work/GAP08_WAVE1_CLOSURE.md`

Final W1 Runtime HEAD：

`6b9db14ff0e6f104f59e418aae2aa8f99f3a2119`

Reviewer-correction verification：

- targeted：39 passed。
- full regression：1119 passed / 4 skipped。
- RF01：PASS。
- RF02：PASS。

Migration 0005：

CREATED / NOT EXECUTED。

Actual PostgreSQL / V07：

NOT EXECUTED / NOT VERIFIED。

Correction-core progress：

    46 / 113 complete / verified
    67 remaining

## Current Execution Gate

Runtime Authorization：

NOT_AUTHORIZED。

W1：

COMPLETE / VERIFIED / ACCEPTED / CLOSED。

W1 source-modification authorization：

CONSUMED / CLOSED。

Next Wave candidate：

    C08
        -> C05
        -> C06

W2 weight：

14。

W2 Execution Coherence：

VERIFIED。

W2 Runtime Source Modification Authorization：

NOT_AUTHORIZED。

Migration execution：

NOT_AUTHORIZED。

Actual PostgreSQL / V07：

NOT_AUTHORIZED。

Broker I/O / Production Activation：

NOT_AUTHORIZED。

Next actual project action：

EXPLICIT BOUNDED W2 RUNTIME SOURCE MODIFICATION AUTHORIZATION DECISION ONLY。

No W2 runtime modification is authorized。

# Completed Work Package — GAP-BROKER-002

Status：

CLOSED / ACCEPTED

Accepted runtime commit：

`7d7fdabcb99da59d3d23ccec62b11c6572ceea82`

Accepted：

- broker-neutral BrokerCapability contract。
- BrokerCapabilitySupport。
- BrokerVerificationMode。
- immutable capability evidence/matrix。
- explicit unsupported/unverified failure。
- Sinopac documentation-only capability matrix。
- no SIMULATION / PRODUCTION claim。
- no live authorization implication。

Verification：

- targeted 22 passed。
- compatibility 45 passed。
- full regression 869 passed。
- correction cycles 0。


# Completed Work Package — GAP-RECON-001B

Status：

COMPLETED / ACCEPTED

Accepted runtime commit：

`4049f982474454556baf8734a5729ecbedc7a438`

Accepted：

- deterministic collection reconciliation。
- ExpectedPositionLoader seam。
- BrokerPositionProvider startup orchestration。
- StartupReadinessState。
- StartupReconciliationResult。
- explicit UNKNOWN external-state conversion。
- strategy_state_ready dependency。
- no silent startup repair。

Verification：

- targeted 58 passed。
- compatibility 22 passed。
- full regression 847 passed。
- implementation correction cycles 1。

Parent GAP-RECON-001：CLOSED / ACCEPTED。


# Completed Work Package — GAP-RECON-001A

Status：

COMPLETED / ACCEPTED

Accepted runtime commit：

`d7dbd884f09e72d7737726409e11e0679206ed8d`

Accepted：

- ReconciliationResult evidence semantics。
- UNKNOWN_EXTERNAL_STATE。
- ReconciliationPolicy。
- ReconciliationCase lifecycle。
- pure create / resolve。
- no corrective action boundary。

Verification：

- targeted 32 passed。
- compatibility 22 passed。
- full regression 821 passed。
- correction cycles 0。

Parent GAP remains IN_PROGRESS until 001B acceptance。


# Completed Work Package — GAP-BROKER-001

Status：

CLOSED / ACCEPTED

Accepted runtime commit：

`b5d309cc91c6dbdf539c17a46662cdde46716224`

Accepted：

- OrderIntent。
- PositionEffect OPEN / REDUCE / CLOSE。
- pure PositionEffect validation。
- Broker optional-intent compatibility seam。
- PaperBroker compatibility。
- Shioaji explicit intent requirement。
- explicit Buy/Sell + New/Cover mapping。
- order-ID prefix inference removal。

Verification：

- targeted 49 passed。
- compatibility 80 passed。
- full regression 800 passed。
- correction cycles 0。

Corrective reconciliation remains outside this completed Work Package。


# Completed Work Package — GAP-ACCOUNT-001

Status：

CLOSED / ACCEPTED

Accepted runtime commit：

`50813b679f818f3837a9f50fdcda9921495ab507`

Accepted：

- BrokerAccount。
- canonical AccountPosition foundation。
- BrokerPositionSnapshot。
- separate read-only query ports。
- exact reverse broker contract resolution。
- pure Sinopac account / position mapping。
- pure pairwise expected / actual comparison。

Verification：

- targeted 50 passed。
- compatibility 48 passed。
- full regression 776 passed。
- correction cycles 0。

Corrective execution 仍未授權。

# Sequencing Rule

Accepted：

1. GAP-08ABCD — CLOSED / ACCEPTED。

Current expanded bundle：

2. GAP-08EFGHI — Operational Persistence + Recovery。

Former EF and GHI boundaries are merged only after explicit architecture freeze of canonical OMS、snapshot、StrategyInstance and recovery semantics。

K520 remains GAP-09。

Sizing experiment：

- current scope 35 leaves / weight 151。
- projected accepted lifecycle gain approximately +6.27pp。
- target is improved accepted work/resource，not forced quota consumption。
- if correction/debug cost becomes nonlinear，next bundle must shrink。

# Mainline Queue

| Order | ID | Work | Status | Dependency |
|---:|---|---|---|---|
| 1 | GAP-ACCOUNT-001 | Broker Account / Position Sync foundation | CLOSED | GAP-07 |
| 2 | GAP-BROKER-001 | Explicit OrderIntent / PositionEffect | CLOSED | GAP-ACCOUNT-001 |
| 3 | GAP-RECON-001 | Reconciliation policy + startup readiness | CLOSED / ACCEPTED | GAP-ACCOUNT-001 + GAP-BROKER-001 |
| 4 | GAP-BROKER-002 | Broker capability matrix | CLOSED / ACCEPTED | Broker mapping + execution semantics |
| 5 | GAP-08 | Trading State Persistence & Recovery | IN_PROGRESS / C01_C22_C11_C23_C24_COMPLETE / HOLD_FOR_NEXT_BOUNDED_AUTHORIZATION | GAP-08ABCD accepted |
| 6 | GAP-PERSIST-001 | Decision / Risk Provenance | BLOCKED | GAP-08 persistence foundation |
| 7 | GAP-09 | Incremental Feature / Market State | PENDING | Trading core stable |
| 8 | GAP-SIM-001 | SimulationBroker / fault injection | PENDING | Execution port stable |
| 9 | GAP-LIVE-001 | LIVE authorization / runtime safety | BLOCKED | Reconciliation + persistence + OMS |
| 10 | M9 | Python Service Boundary | BLOCKED | Operational core |
| 11 | GAP-APP-001 | ASP.NET Core Application/API | BLOCKED | Python service boundary |
| 12 | GAP-WEB-001 | React Workspace | BLOCKED | Application API |
| 13 | V1-INTEGRATION | Full V1 integration/readiness | BLOCKED | V1 capability completion |

---

# Follow-Up Queue

以下不得在 mainline READY 時自行插隊：

- GAP-07-TIME-001。
- GAP-07-SESSION-001。
- GAP-07-SESSION-EXPIRY。
- GAP-07-MARGIN-001 remaining database/live work。
- Continuous roll engine。
- GAP-ARCH-001。
- GAP-ARCH-002。
- GAP-ARCH-003。
- GAP-REPO-001。
- GAP-REPO-002。
- GAP-ENV-001。
- GAP-DOC-001。

其中：

GAP-07-TIME-001 與 GAP-07-SESSION-EXPIRY 必須在 production live 前完成。

---

# Queue Selection Rules

順序：

1. P0 current correctness/safety blocker。
2. READY P1 mainline。
3. Required mainline dependency。
4. Approved milestone-required work。
5. P2 follow-up only when explicitly scheduled。
6. P3 / OBS 不自行執行。

若 mainline 有 READY 工作：

禁止自行選 cleanup。

---

# Automation Rule

Level 3A：

每次 autonomous run 只執行一個 ACTIVE Work Package。

Runtime Codex 完成後：

- 完成 runtime implementation / tests。
- runtime commit / push。
- final report。
- STOP。

若 ACTIVE 指定 deterministic docs closure 由人工負責：

人工再更新：

- CURRENT_STATE。
- CURRENT_WORK。
- GAP_REGISTER。
- DEVELOPMENT_LOG。

不得由 runtime executor 自動開始下一個 mainline。

至少 2–3 個 queue-driven runtime Work Package 穩定後，再評估 Level 3B。

## Historical Decision Checkpoint 5A Work Boundary

Completed architecture work：

- R-01 amendments A1-A4。
- R-02 amendments A5-A6。
- R-03 unchanged confirmation。
- R-04 unmanaged-external-execution + complete-RecoveryCut handoff clarification。
- R-05A-F final contract。

Current runtime work：NONE AUTHORIZED。

Next decision cluster：

    R-06 — Multi-strategy recovery boundary
    R-07 — ReconciliationCase / BrokerAccount recovery scope formal closure

Do not start runtime correction from this checkpoint。

## Historical Decision Checkpoint 5B Work Boundary

Completed architecture work：

- R-06 Multi-strategy recovery boundary：DECIDED。
- R-07 ReconciliationCase BrokerAccount scope：DECIDED。

Runtime work：NONE AUTHORIZED。

Next decision cluster：

    R-08 — StrategyInstance instrument vs symbol identity
    R-09 — strategy_instance_id / config_version / lifecycle authority

R-09 remains the owner of exact StrategyInstance/config identity、policy-version transition and lifecycle/provisioning authority。

Do not begin runtime correction from this checkpoint。

## Historical Decision Checkpoint 5C Work Boundary

Completed architecture work：

- R-08 StrategyInstance instrument vs symbol identity：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-09 StrategyInstance / config / implementation / lifecycle authority：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

Runtime work：NONE AUTHORIZED。

Next：

    R-10 — Initial explicit FLAT snapshot provenance formal closure
    R-11 — occurred_at / received_at clock authority

Do not begin runtime correction from this checkpoint。

## Historical Decision Checkpoint 5D Work Boundary

Completed architecture work：

- R-10 Initial explicit expected-state provenance：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-11 operational clock/timestamp authority：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。

Runtime work：NONE AUTHORIZED。

Next：

    R-12 — ReconciliationRun audit contract
    then R-13 / R-14 boundary classification

Do not begin runtime correction from this checkpoint。

## Historical Decision Checkpoint 5E Work Boundary — ARCHITECTURE RECORD

Completed architecture/classification work：

- R-12 ReconciliationRun audit contract：DECIDED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-13 Operator Authorization：DECIDED / BOUNDARY_CLASSIFIED / IMPLEMENTATION_CORRECTION_REQUIRED。
- R-14 Operational Market-Data Completeness：DECIDED / BOUNDARY_CLASSIFIED / GAP-08_ENFORCEMENT_CORRECTION_REQUIRED / GAP-DATA-001_DEFERRED_PRODUCTION_DEPENDENCY。

Runtime work：NONE AUTHORIZED。

Mandatory anti-misread：

    R-13 production auth runtime not implemented != authorization requirement waived

    R-14 full completeness detector deferred != completeness requirement waived

Candidate runtime commit is not an authorized runtime baseline。

Next authoritative sequence：

    1. K520 defer confirmation
    2. Broker capability gate classification
    3. Complete expanded correction-scope map
    4. Reweight expanded correction Work Package
    5. Explicit bounded runtime authorization decision

Do not begin runtime correction before step 5 explicitly authorizes a bounded Work Package。
