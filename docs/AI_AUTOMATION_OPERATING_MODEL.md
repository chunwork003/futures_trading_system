# AI / CODEX Automation Operating Model

## 1. Purpose
本文件固定本專案的 AI 角色分工、架構升級原則、GPT-6 審計資料使用方式，以及朝 CODEX 自動排程化演進的目標。

Canonical current governance 仍由 `docs/CURRENT_STATE.md` 決定。本文件不授權 runtime、migration、broker、PostgreSQL 或 production side effect。

## 2. Fixed Role Model

### VIBE / Architecture Coordinator / Continuous Reviewer
負責日常：
- 持續檢核 GitHub / repository 實際狀態。
- 對照 Architecture Baseline、Blueprint、GAP、Work Package。
- 對照 GPT-6 已完成的高階審計與 Playbook。
- 把高階原則轉成 CODEX 可執行 bounded task contract。
- 定義 dependency、scope、read/write/protected set、counterexample、test/Git gate、STOP condition。
- 審核 CODEX runtime candidate。
- 區分 tooling / implementation / task-contract / architecture defect。
- 在既有 architecture boundary 內直接 replan / refine。
- 將重複成本制度化成 workflow/template/guard/script。
- 推動 repository-native CODEX scheduling automation。

不得把日常 replan、scope 拆解、test gate、task manifest 重複丟回高階架構模型。

### CODEX Executor
只負責已 materialized / authorized Work Package：
- counterexample first
- search before read
- minimum sufficient context
- smallest coherent delta
- targeted/integration/regression gates
- exact scope/protected/migration guards
- commit/push policy
- STOP

CODEX 不具有：
- 新 architecture semantics authority
- 自行擴 write scope
- 自行增加 leaf/Wave
- 自行改 weight/roadmap
- 自行開 RF03
- 隱含 migration execution / broker / production 權限

### Architect GPT-6
GPT-6 是稀有、昂貴的 architecture escalation resource。

預設不參與日常：
- Work Package 規劃
- routine review
- task manifest
- test command
- Git 操作
- bounded correction
- queue selection

僅在以下情況升級：
1. 需要修改 accepted Architecture Decision Baseline。
2. accepted authority owners 發生不可調和矛盾。
3. domain boundary 本身需要重切。
4. 跨 Recovery/Execution/Risk/Strategy/Broker 的新 semantics 無既有 owner。
5. production/money/runtime authorization authority 要重定義。
6. correction-core denominator、Wave、roadmap 需重大重算。
7. 存在多個合理 architecture 方案且既有證據不足以決定。
8. bounded correction 反覆出現同類 false READY / authority leakage，證明不是 implementation defect。

## 3. Architect GPT-6 Audit Source Registry

### 01_AUDIT_AND_TARGET_DESIGN.md
External provenance:
`C:/Users/CHUNs/.codex/visualizations/2026/09/27/01a0e1c9-6322-7622-9e2f-f7f9069b3c81/audit/01_AUDIT_AND_TARGET_DESIGN.md`

用途：
- 全面開發流程審計
- current vs target design
- authority/workflow/evidence 問題
- 效率瓶頸與目標 operating model

### 02_EXECUTION_PLAYBOOK.md
External provenance:
`C:/Users/CHUNs/.codex/visualizations/2026/09/27/01a0e1c9-6322-7622-9e2f-f7f9069b3c81/audit/02_EXECUTION_PLAYBOOK.md`

用途：
- high-risk assertion counterexample-first
- bounded execution
- failure classification
- correction budget
- STOP / architect decision
- evidence-driven review

### 03_NEW_PROJECT_BOOTSTRAP.md
External provenance:
`C:/Users/CHUNs/.codex/visualizations/2026/09/27/01a0e1c9-6322-7622-9e2f-f7f9069b3c81/audit/03_NEW_PROJECT_BOOTSTRAP.md`

用途：
- Day-0 authority/task-contract/queue/test/Git/review boundary
- 避免後期用大量聊天補治理

### README.md
External provenance:
`C:/Users/CHUNs/.codex/visualizations/2026/09/27/01a0e1c9-6322-7622-9e2f-f7f9069b3c81/audit/README.md`

用途：
- audit 入口
- templates
- reproduction/test records
- artifact navigation

Repository 只記錄 pointer + 已接受 operating principles，不複製整份外部審計內容。

## 4. Recorded Audit Principles
1. Authority before execution。
2. High-risk assertion counterexample before positive implementation。
3. Pointer > duplicated prose。
4. Search first / minimum sufficient read。
5. Wave shared context + leaf delta。
6. Typed != trusted；authority 需 producer/provenance/currentness/same-world revalidation。
7. Tooling failure != semantic correction。
8. Reviewer 先看 manifest/scope/tests/high-risk diff，不預設全 repo 重讀。
9. Single-agent default；不先建 RAG/vector DB/workflow DB/multi-agent orchestrator。
10. Automation KPI 是 accepted engineering progress / model consumption，不是跑得多。

## 5. Continuous Optimization Loop
固定：
`OBSERVE -> CLASSIFY -> GENERALIZE -> MATERIALIZE -> VERIFY`

可 materialize 為：
- workflow rule
- reusable task template
- PowerShell preflight/guard
- test gate
- scope/hash checker
- retry policy
- reviewer checklist
- queue field

只有可重複問題才升級 tooling；一次性問題不增加 framework。

## 6. CODEX Scheduling Maturity

### Level 3A-0 — current bounded execution
人/VIBE 選一個 authorized Work Package；CODEX 執行一次；STOP reviewer。

### Level 3A-1 — machine preflight
自動檢查：
- fetch / HEAD / origin
- dirty tree
- CURRENT
- ACTIVE
- source authorization
- queue/dependency
- side-effect envelope

輸出 `DISPATCHABLE` / `NOT_DISPATCHABLE`，不執行 CODEX。

### Level 3A-2 — one-click dispatch
只在 DISPATCHABLE：
- 產生 transient task packet
- exact CODEX handoff
- 可選擇性呼叫 local CODEX CLI
- 一次只跑一個 package
- 不自動進下一 package

### Level 3A-3 — automated result intake
收集：
- HEAD
- changed files
- tests
- diff-check
- scope
- push state
- efficiency evidence
- reviewer packet

Acceptance 仍由 reviewer 決定。

### Level 3B — queue-driven scheduling
至少 2–3 個 3A-1～3A-3 package 穩定，且：
- zero unauthorized scope expansion
- STOP 正確
- remote divergence 正確
- reviewer packet 足夠
- human intervention 主要剩 architecture

才允許 scheduler 自動選 highest-priority READY mainline。

### Level 3C — pre-authorized Wave progression
只有同一已授權 Wave，且 leaf gate、dependency、authority、side-effect 都未變，才可自動前進。

Architecture/business/protected/migration-exec/broker-I/O barrier 仍 STOP。

## 7. Scheduler State Sources
只使用 repository-native：
1. `docs/CURRENT_STATE.md`
2. `docs/CURRENT_WORK.md`
3. `docs/work/ACTIVE.md`
4. exact authorization
5. `docs/CODEX_EXECUTION_WORKFLOW.md`
6. 本文件

V0 不建立 workflow DB。

## 8. Queue / ACTIVE Hygiene
自動排程前：
- CURRENT_WORK current section 必須與 CURRENT_STATE 一致。
- ACTIVE 只能有一個 current package 或 `NONE_AUTHORIZED`。
- 舊內容標 HISTORICAL / SUPERSEDED。
- machine fields 唯一可解析。

建議 machine fields：
`WORK_PACKAGE_ID, STATUS, PRIORITY, PLANNING_BASELINE, EXPECTED_HEAD, AUTHORIZATION, RUNTIME_SOURCE_AUTH, SIDE_EFFECT_CLASS, DEPENDENCIES, WRITE_SCOPE, TEST_GATE, GIT_POLICY, REVIEW_BARRIER`

## 9. GPT-6 Escalation Budget Rule
升級 GPT-6 前，VIBE 必須能明確提出：
1. exact blocking question
2. current accepted authority
3. counterexample
4. why existing owner cannot decide
5. alternatives already considered
6. exact required decision output

否則留在 VIBE / CODEX workflow。

## 10. Current GAP-08 W4 Application
目前：
`HOLD / RESCOPE_C15_AND_REPLAN_W4`

GPT-6 已完成 AD-01～AD-04 決策。

因此：
- W4 replan 屬於 VIBE 日常工作。
- 不需要再把 routine decomposition 丟回 GPT-6。
- CODEX 在 bounded authorization materialize 前仍 NOT_AUTHORIZED。
- automation tooling 不得繞過 CURRENT/ACTIVE authorization gate。

<!-- AUTOMATION_MASTER_V1_1_BEGIN -->
## Development Automation Master Architecture v1.1 — RF01/RF02 Governance Materialization

### Status

```text
MASTER_ARCHITECTURE_VERSION = 1.1
STATUS = FROZEN
FREEZE_SOURCE_REVIEW_HEAD = 0eb899794a8af4d4e0ad2f3e0b3be709c93bed3e
TARGETED_AUTOMATION_RF01_RF02_RE_REVIEW = PASS
MANIFEST_HASH_INTEGRITY_ONLY_RE_REVIEW = PASS
AUTO_RF01 = CLOSED
AUTO_RF02 = CLOSED
AUTO_MANIFEST_RF01 = CLOSED
IMPLEMENTATION = NOT_STARTED
LEVEL_3B = NOT_ENABLED
LEVEL_3C = NOT_ENABLED
LEVEL_4_AUTONOMY = NOT_ENABLED
LEVEL_5_CONTINUOUS_DEVELOPMENT = NOT_ENABLED
NEXT_MAINLINE_GAP = NOT_AUTHORIZED
```

本節 materialize Automation Master v1.1 的治理修正與 unified re-entry 規則，不授權 runtime、migration execution、PostgreSQL、Broker/Shioaji、LIVE 或下一 trading mainline GAP。

### Canonical machine policies

- `automation/policies/authorization_lifecycle.v1.yaml`：single-use authorization lifecycle、exact revision/hash/baseline/scope binding、restart/reconciliation fail-closed。
- `automation/policies/quota_admission_policy.v1.yaml`：versioned quota/admission governance、P90、5H+weekly、reserve、post-WAIT fresh re-resolution。
- `automation/policies/development_state_machine.v1.yaml`：authorization/execution/quota/review 分軸；不存在 `QUOTA_WAIT -> EXECUTING`。
- `automation/policies/development_entry_protocol.v1.yaml`：所有 Agent 共用 bootstrap/routing；continue/resume/status-uncertain 先 rehydrate，再決定自動續做、討論、WAIT 或 status-only。
- `automation/specs/negative_assertions.v1.yaml`：CE-01/02/03/06/14/17/21 與 re-entry negative assertions。

### Hard invariants

```text
READY != AUTHORIZED
AUTHORIZED != EXECUTABLE
Historical authorization != current executability
Queue/ACTIVE != authorization authority
Metrics may recommend policy but may not become policy
Quota WAIT invalidates previous dispatch eligibility
No timer/quota reset/reviewer event directly invokes CODEX
Memory/chat/Library are navigation context only when repository authority is available
```

### Persistence model

```text
Git repository = canonical persistent governance / normalized evidence
Local checkout = synchronized execution workspace
.automation/ = local transient locks/raw/session-cache/tmp
automation/runs/ = normalized durable run/checkpoint/delta/handoff/telemetry artifacts
```

### Activation

```text
MASTER_V1_1_FROZEN
-> Automation Implementation Program compilation

NOT
-> CODEX execution
-> immediate Level 3B/3C/4/5 activation
-> next trading mainline GAP authorization
```


### Freeze Materialization

```text
FREEZE_STATUS = FROZEN
FREEZE_SOURCE_REVIEW_HEAD = 0eb899794a8af4d4e0ad2f3e0b3be709c93bed3e
NEXT_ROUTE = AUTOMATION_IMPLEMENTATION_PROGRAM_COMPILATION
```

Freeze is governance materialization only. It does not grant Runtime Authorization, broker I/O, migration execution, LIVE, production activation, next-mainline-GAP authority, or unattended CODEX execution.

### Compiled Implementation Program

```text
PROGRAM_ID = AUTO-IMP-PROGRAM-V1
SOURCE_FREEZE_HEAD = 52921ae3f205ef2eec4306e84ff92d4cd9cdeab3
PROGRAM_STATUS = COMPILED_CANDIDATE_NOT_AUTHORIZED
IMPLEMENTATION_AUTHORIZATION = NOT_AUTHORIZED
CODEX_EXECUTION = NOT_AUTHORIZED
NEXT_ROUTE = AUTOMATION_IMPLEMENTATION_PROGRAM_REVIEW
```

The compiler materializes a strangler / dual-run implementation program. Near-horizon packages are exact, but all remain PLANNED_NOT_AUTHORIZED. Existing PowerShell scheduler/result-intake scripts remain reference/regression fixtures until explicit acceptance of canonical replacements. Automated CODEX dispatch remains denied until a measurable execution channel, exact authorization lifecycle, quota admission, single-writer reservation and telemetry binding are implemented and accepted.


### Implementation Program Review / W1 Authorization Compilation

```text
PROGRAM_REVIEW = PASS
PROGRAM_ID = AUTO-IMP-PROGRAM-V1
PROGRAM_STATUS = ACCEPTED_FOR_IMPLEMENTATION_PLANNING
W1 = W1_FOUNDATION_SHADOW
AUTHORIZATION_ID = AUTH-AUTO-IMP-W1-01
AUTHORIZATION_REVISION = 1
AUTHORIZATION_STATE = NOT_AUTHORIZED
AUTOMATIC_DISPATCH = DENIED
AUTOMATIC_NEXT_PACKAGE_PROGRESSION = DENIED
NEXT_ROUTE = AUTOMATION_IMPLEMENTATION_W1_AUTHORIZATION_DECISION
```

Program acceptance does not authorize any implementation package. The W1 authorization artifact is a compiled governance candidate only. Any effective transition to AUTHORIZED requires an explicit Automation Governance Authority decision against the exact revision/hash/scope binding and does not grant Runtime Authorization, broker I/O, migration execution, LIVE, production activation, Level 3B/3C/4/5 activation or next-mainline-GAP authority.

<!-- AUTOMATION_MASTER_V1_1_END -->
