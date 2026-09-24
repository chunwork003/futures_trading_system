# V1 System Blueprint

## 1. Status

AUTHORITATIVE
Blueprint baseline 已完成並成為 V1 engineering architecture authority；runtime execution 仍由 `docs/work/ACTIVE.md` 控制。

正式啟用前必須完成：

- A～O Domain Blueprint。
- 既有 92 capability blocks 全部 mapping。
- 0 orphan capability。
- 0 orphan engineering leaf。
- CONNECTION_MATRIX。
- STATE_AUTHORITY。
- SOURCE_REGISTRY。
- TRACEABILITY。
- METRICS。
- dependency consistency audit。
- authority consistency audit。
- Blueprint baseline commit。

---

## 2. Purpose

本文件是 V1 的 Master Engineering Blueprint。

它回答：

- 系統的大架構是什麼。
- 每個 Domain 有哪些中型 capability group。
- 每個 group 有哪些最小 engineering leaf。
- 每個 leaf 的目標與責任。
- upstream / downstream。
- ownership。
- current / target / migration。
- external source。
- acceptance。
- test。
- progress weight。
- Work Package mapping。

本文件不是：

- runtime implementation。
- source code。
- GAP Register。
- Current Work Queue。
- ADR replacement。

---

## 3. Architecture Hierarchy

Level 0：

    Product / V1

Level 1：

    Domain
    A ... O

Level 2：

    Capability Group
    A100 / A200 / ...

Level 3：

    Engineering Leaf
    A110 / A120 / ...

Level 4：

    Work Package implementation slice

Example：

    J — Account / Reconciliation
        J400 Broker Actual Position
            J410 BrokerPositionProvider
            J420 BrokerPositionSnapshot
            J430 Actual Position Identity
            J440 Observation Semantics

        GAP-ACCOUNT-001
            implements selected J / I / D leaves

---

## 4. V1 Domains

| ID | Domain | Blueprint File |
|---|---|---|
| A | Governance / Engineering | `blueprint/A_GOVERNANCE.md` |
| B | Data Pipeline | `blueprint/B_DATA_PIPELINE.md` |
| C | Calendar / Contract | `blueprint/C_CALENDAR_CONTRACT.md` |
| D | Canonical Domain | `blueprint/D_CANONICAL_DOMAIN.md` |
| E | Feature / Strategy | `blueprint/E_FEATURE_STRATEGY.md` |
| F | Backtest / Research | `blueprint/F_BACKTEST_RESEARCH.md` |
| G | Decision / Risk | `blueprint/G_DECISION_RISK.md` |
| H | Execution / OMS | `blueprint/H_EXECUTION_OMS.md` |
| I | Broker Adapter | `blueprint/I_BROKER_ADAPTER.md` |
| J | Account / Reconciliation | `blueprint/J_ACCOUNT_RECONCILIATION.md` |
| K | Persistence / Recovery | `blueprint/K_PERSISTENCE_RECOVERY.md` |
| L | Simulation / Live Safety | `blueprint/L_SIMULATION_LIVE_SAFETY.md` |
| M | Python Service Boundary | `blueprint/M_PYTHON_SERVICE.md` |
| N | ASP.NET Core Application | `blueprint/N_ASPNET_APPLICATION.md` |
| O | React Workspace | `blueprint/O_REACT_WORKSPACE.md` |

---

## 5. Post-V1 Reserved Domains

以下 namespace 保留，不計入 V1 completion：

| ID | Reserved Domain |
|---|---|
| P | Multi-Asset Expansion |
| Q | Multi-Broker Expansion |
| R | AI / ML |
| S | News Intelligence |
| T | GIS / Property |
| U | Mobile |
| V | Advanced Visualization |
| W | Advanced Portfolio Analytics |
| X | Distributed Infrastructure |
| Y | Deployment / Operations |
| Z | Experimental / Future |

不得因 namespace 已保留，就在 V1 自動開始實作。

---

## 6. Blueprint Supporting Documents

`blueprint/README.md`

Blueprint schema 與編號規則。

`blueprint/CONNECTION_MATRIX.md`

跨 Domain / capability 的資料流與 dependency direction。

`blueprint/STATE_AUTHORITY.md`

每一種重要 state 的 authoritative owner / representation / persistence。

`blueprint/SOURCE_REGISTRY.md`

官方手冊、交易所規格、framework documentation 的受控來源清單。

`blueprint/TRACEABILITY.md`

Capability → Blueprint → GAP → Work Package → code → tests → commit。

`blueprint/METRICS.md`

設計、實作、測試、整合、live readiness 的量化規則。

---

## 7. Existing 92 Capability Blocks

`V1_CAPABILITY_MAP.md`

仍是目前 V1 capability-level inventory。

Blueprint baseline 完成前：

92 blocks 的既有 weighted completion 仍為 official provisional progress。

Blueprint baseline 完成後：

每個 capability block 必須 mapping 至一個或多個 engineering leaves。

不得有：

- unmapped capability。
- duplicate semantic owner。
- unknown authority。
- unowned runtime state。

---

## 8. Work Package Rule

Blueprint baseline 啟用後：

每個 ACTIVE Work Package 必須明確列出：

    Implements
    Touches
    Does Not Implement

以及 Blueprint IDs。

Example：

    Implements:
        D630
        I510-I530
        I610-I650
        J210-J240
        J310-J330
        J410-J440
        J510-J590

任何 Blueprint scope 外 implementation：

先 classification。

不得 silent scope expansion。

---

## 9. Design Freeze Rule

Blueprint：

定義全系統工程施工圖。

ACTIVE Design Freeze：

定義當前 Work Package 的 public implementation contract。

兩者關係：

    Architecture
        → Blueprint
            → Work Package Design Freeze
                → Runtime implementation

Codex 不得反向修改上層 architecture semantics。

---

## 10. Current Build State

Architecture baseline：

`305f70c`

Current runtime mainline：

GAP-ACCOUNT-001。

Runtime launch：

暫時 HOLD。

原因：

先完成 V1 Blueprint baseline，再開始 Codex runtime implementation。

此 HOLD：

不是 runtime blocker。

不是 GAP-ACCOUNT-001 failure。

是一次性的人工 architecture baseline gate。
