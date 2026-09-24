# Current Work

## Purpose

本文件只保存：

- Current work。
- Mainline queue。
- Dependencies。
- Blocking relation。

完整產品功能：

`V1_CAPABILITY_MAP.md`

完整 architecture：

`ARCHITECTURE.md`

Technical issues：

`GAP_REGISTER.md`

完整 Work Package：

`work/ACTIVE.md`

---

# Current Active Candidate

ID：

GAP-ACCOUNT-001

Title：

Broker Account / Position Sync Foundation

Status：

READY_FOR_ARCHITECT_REVIEW

Priority：

P1 MAINLINE

Execution Mode：

REVIEW_REQUIRED

Recommended Model：

GPT-5.6 Sol

Why Next：

GAP-07 已 CLOSED。

在 persistence / live 之前：

系統必須明確區分 internal expected AccountPosition 與 broker actual BrokerPositionSnapshot。

---

# Sequencing Rule

Read-only Broker Account / Position Sync 可以先做：

- BrokerAccount。
- BrokerPositionSnapshot。
- account/position query contract。
- snapshot mapping。
- pure mismatch detection。

任何 corrective broker execution：

必須先完成：

GAP-BROKER-001 OrderIntent / PositionEffect。

---

# Mainline Queue

| Order | ID | Work | Status | Dependency |
|---:|---|---|---|---|
| 1 | GAP-ACCOUNT-001 | Broker Account / Position Sync foundation | READY_FOR_REVIEW | GAP-07 |
| 2 | GAP-BROKER-001 | Explicit OrderIntent / PositionEffect | READY_AFTER_ACCOUNT_FOUNDATION | GAP-07 |
| 3 | GAP-RECON-001 | Reconciliation policy + startup readiness | BLOCKED | Account foundation + execution semantics |
| 4 | GAP-BROKER-002 | Broker capability matrix | PENDING | Broker mapping + execution semantics |
| 5 | GAP-08 | Trading State Persistence & Recovery | BLOCKED | Reconciliation foundation |
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

完成後：

- 更新 state。
- 更新 queue。
- 停止。

不得自動開始下一個 mainline。

至少 2–3 個 queue-driven runtime Work Package 穩定後，再評估 Level 3B。
