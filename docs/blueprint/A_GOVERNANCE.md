# A — Governance / Engineering

## Status

BUILDING / PROVISIONAL until Blueprint baseline acceptance。

Lifecycle 標示在 Blueprint baseline audit 前皆視為 provisional。

---

## Domain Purpose

建立 architecture governance、Work Package、quality gate、repository safety、automation 與 handoff 的工程治理。

此 Domain 不實作 trading business logic。

---

## Capability Groups

| Group | Name | Responsibility |
|---|---|---|
| A100 | Architecture Governance | source of truth、ADR、ownership、migration policy |
| A200 | Work Package System | design freeze、scope、source、stop conditions |
| A300 | Verification / Quality Gate | tests、diff、scope、Git acceptance |
| A400 | Queue / Automation | mainline selection、Level 3A / 3B |
| A500 | Repository / Environment | branch、data safety、environment |
| A600 | Documentation / Handoff | state、queue、GAP、handoff、blueprint |

---

## Engineering Leaves

| ID | Name | Purpose | Lifecycle | Weight | Maps |
|---|---|---|---|---:|---|
| A110 | Authoritative Document Hierarchy | 定義 current source of truth 與文件責任 | ACCEPTED | 2 | A01 |
| A120 | ADR Lifecycle | material architecture decision 必須留下 ADR / decision record | ACCEPTED | 2 | A01 |
| A130 | Architecture Change Control | architecture material change 不得只存在聊天 | ACCEPTED | 2 | A01 |
| A140 | Ownership / Invariant Governance | canonical owner、dependency、system invariant 有唯一來源 | ACCEPTED | 3 | A01 |
| A150 | Compatibility / Migration Governance | CURRENT → TARGET 採 bounded compatibility-first migration | DESIGN_FROZEN | 3 | A01 |
| A210 | Work Package Template | 每次 runtime work 有完整 bounded contract | ACCEPTED | 2 | A02 |
| A220 | Architect Design Freeze | public semantics 在 Codex implementation 前人工凍結 | ACCEPTED | 3 | A02,A03 |
| A230 | Scope Freeze | 明確定義做／不做／allowed／forbidden | ACCEPTED | 2 | A02 |
| A240 | Source Requirement Gate | broker / exchange / framework semantics 綁定受控來源 | DESIGNED | 2 | A01,A02 |
| A250 | Stop Conditions | ambiguity、money safety、regression 等明確 HARD_BLOCK | ACCEPTED | 3 | A02 |
| A260 | Human / Codex Responsibility Split | deterministic docs 與 runtime implementation 明確分工 | ACCEPTED | 2 | A02,A03 |
| A310 | Baseline Precheck | branch、HEAD ancestor、working tree、known warnings | ACCEPTED | 2 | A02 |
| A320 | Targeted Test Gate | 修改能力先跑最小相關 tests | ACCEPTED | 2 | A02 |
| A330 | Relevant Integration Gate | 跨 module consumer interaction 必須驗證 | ACCEPTED | 2 | A02 |
| A340 | Full Regression Gate | bounded implementation 完成後跑 full regression | ACCEPTED | 3 | A02 |
| A350 | Diff / Scope Validation | git diff --check + scope validation | ACCEPTED | 2 | A02 |
| A360 | Exact Staging / Data Protection | exact files stage；data/ 預設禁止 | ACCEPTED | 2 | A02 |
| A370 | Commit / Push / Verify | accepted slice 可獨立追蹤與 revert | ACCEPTED | 2 | A02 |
| A410 | Executable Mainline Queue | CURRENT_WORK 是工作排序來源 | DESIGN_FROZEN | 2 | A03 |
| A420 | Level 3A Bounded Execution | 每次 autonomous runtime 最多一個 Work Package | DESIGN_FROZEN | 3 | A03 |
| A430 | Queue Runtime Validation Cycles | 累積 2–3 個穩定 Level 3A runtime cycles | NOT_DESIGNED | 2 | A03,A04 |
| A440 | Level 3B Continuous Orchestration | 穩定後才評估 continuous queue execution | NOT_DESIGNED | 4 | A04 |
| A510 | Branch / Remote Synchronization | runtime 前 master 與 origin/master 必須可驗證一致 | ACCEPTED | 2 | A01,A02 |
| A520 | Repository Data Protection | 本機大型資料與 generated assets 不進 Git | ACCEPTED | 3 | A02 |
| A530 | Environment Reproducibility | Python/dependency/environment 可重現與診斷 | IMPLEMENTED | 2 | A02 |
| A540 | Warning / Technical Debt Tracking | non-blocking warnings 進 GAP，不 silent fix | ACCEPTED | 2 | A01,A02 |
| A610 | Current State / Queue / GAP Documents | 現況、工作、問題三種責任分離 | ACCEPTED | 2 | A01 |
| A620 | AI Handoff | 新 session 可恢復重要架構與安全規則 | ACCEPTED | 2 | A01 |
| A630 | Development History | 保留 milestone、decision、test、commit 歷史 | ACCEPTED | 1 | A01 |
| A640 | Engineering Blueprint | 大／中／小施工圖與 traceability | DESIGNED | 4 | A01,A03 |
| A650 | Blueprint Metrics | leaf weight / lifecycle 驅動量化進度 | DESIGNED | 3 | A03 |

---

## Primary Connections

| From | To | Contract |
|---|---|---|
| A100 | All Domains | architecture / ownership rules |
| A200 | Work Package | bounded execution contract |
| A300 | Runtime implementation | acceptance gate |
| A400 | CURRENT_WORK / ACTIVE | work selection |
| A600 | Human / AI sessions | persistent project context |

---

## Invariants

- Architecture 不得只存在聊天。
- ACTIVE 不得自行推翻 Blueprint / ADR。
- READY mainline 存在時不得 opportunistic cleanup。
- runtime executor 不得自行擴張 architecture semantics。
- deterministic documentation 優先人工 / PowerShell。
- test count、LOC、file count 不直接代表完成百分比。

---

## Main Internal Sources

- SRC-ADR-001。
- SRC-ARCH-001。
- SRC-BLUEPRINT-001。

---

## Code Documentation Requirement

所有重要 public contract / module 必須依 Blueprint README 的 Code Documentation Contract。

---

## Domain Acceptance

A Domain baseline accepted 前至少：

- A01～A04 全部有 leaf mapping。
- governance documents 互相一致。
- Work Package template 支援 Blueprint Scope / Source Requirements。
- Phase 3 metrics audit 無 orphan。
