# Current Work

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

Current activity：POST_RUNTIME_ARCHITECTURE_DECISION_REVIEW

Runtime Authorization：NOT_AUTHORIZED_FOR_FURTHER_EXECUTION

Launch Gate：HOLD_FOR_POST_RUNTIME_ARCHITECTURE_DECISIONS

Accepted decision checkpoint：R-01 / R-02 / R-03A / R-03B。

Open decisions：R-03C / R-03D / R-04。

Detailed decision record：

`docs/adr/ADR-002-RECOVERY-CONSISTENCY-MARKET-OBSERVATION.md`

Blueprint scope remains：35 leaves / weight 151。

The 35 / 151 runtime candidate must not be promoted to ACCEPTED until bounded correction + verification completes。

K520 remains GAP-09-owned。

Next action：finish R-03C / R-03D / R-04 architecture decisions，then freeze a bounded correction Work Package。

No Codex runtime execution is authorized during this decision hold。

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
| 5 | GAP-08 | Trading State Persistence & Recovery | IN_PROGRESS / 08EFGHI_READY_FOR_EXECUTION | GAP-08ABCD accepted |
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
