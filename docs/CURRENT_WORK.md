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

Parent GAP：

GAP-08

Candidate：

GAP-08EF

Title：

Execution + Account/Reconciliation Persistence

Status：

READY_FOR_ARCHITECTURE_REVIEW

Priority：

P1 MAINLINE

Runtime Authorization：

NOT_YET_AUTHORIZED

Base Blueprint scope：

K310 K320 K330 K340 K350 K410 K420 K430 K440 K450

Architecture review must evaluate direct dependency expansion：

- H170 canonical execution ownership。
- H440 OrderEvent contract。
- H510-H550 OMS identity/state/persistence/recovery seams。
- H830 persisted event idempotency identity。

Reason：

do not persist legacy execution ownership as a new canonical persistence contract merely to keep Work Package small。

GAP-08GHI：

remains blocked pending EF/OMS persistence foundation。

Next action：

freeze the largest coherent execution/account persistence bundle；do not start runtime before design freeze/gate。


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

Current：

2. GAP-08EF — READY_FOR_ARCHITECTURE_REVIEW。

Later：

3. GAP-08GHI — BLOCKED_BY_08EF_ACCEPTANCE。

K520：DEFERRED_TO_GAP_09。

Dynamic sizing evidence after GAP-08ABCD：

- 19 leaves / weight 77。
- 12% user-observed 5HR。
- six-sample 5HR average 12.50%。
- one correction cycle。
- 23 tool operations。
- ~12m09s wall time。

Sizing rule：

continue expanding coherent mainline work when shared context reduces repeated overhead；
do not cross unresolved canonical ownership / recovery safety semantics merely to increase bundle size。

# Mainline Queue

| Order | ID | Work | Status | Dependency |
|---:|---|---|---|---|
| 1 | GAP-ACCOUNT-001 | Broker Account / Position Sync foundation | CLOSED | GAP-07 |
| 2 | GAP-BROKER-001 | Explicit OrderIntent / PositionEffect | CLOSED | GAP-ACCOUNT-001 |
| 3 | GAP-RECON-001 | Reconciliation policy + startup readiness | CLOSED / ACCEPTED | GAP-ACCOUNT-001 + GAP-BROKER-001 |
| 4 | GAP-BROKER-002 | Broker capability matrix | CLOSED / ACCEPTED | Broker mapping + execution semantics |
| 5 | GAP-08 | Trading State Persistence & Recovery | IN_PROGRESS / 08EF_READY_FOR_ARCHITECTURE_REVIEW | GAP-08ABCD accepted |
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
