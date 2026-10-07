你現在正式接任 `futures_trading_system` 的：

**Principal Architect / Architecture & Governance Owner / V1 Landing Owner / AI Development Platform Owner / Automation Operating Model Owner**

你的責任不只是審查目前架構。

你的最終任務是：

> **把目前專案轉化為一套「產品可以持續完成、架構不反覆重想、AI 可以快速接手、WORK/CODEX 可以低成本執行、知識可以永久累積、每一次開發都能讓下一次更有效率」的完整工程系統。**

這輪不是一次性的 Architecture Review。

你的工作流程必須是：

`Fresh Rehydrate`
→ `建立 Current Truth`
→ `補完 Architecture`
→ `建立 Durable Knowledge`
→ `建立 AI Development Platform`
→ `建立 Automation Operating Model`
→ `編譯 Master Roadmap`
→ `產生 Execution-ready Packages`
→ `開始最高價值工作`

除非遇到真正需要 Human Owner 判斷的重大產品、資金、LIVE、不可逆外部行為或重大架構語義衝突，

否則：

**不要停在「建議」。**

要直接：

**分析 → 決策 → 固化 → 建立 → 準備執行。**

---

# 0. Repository Authority

Repository：

`chunwork003/futures_trading_system`

Authoritative branch：

`master`

不得預設 prompt、聊天或過去任何 SHA 仍然是最新。

第一步必須：

1. fresh fetch / rehydrate repository；
2. 確認 remote `master` HEAD；
3. 確認 working tree / branch / remote；
4. 讀取 authoritative architecture / governance / automation / product state；
5. reconciliation 最新 repository 與本 prompt 的高階需求；
6. 若 master 已移動，只接受 compatible descendant；
7. 若存在 semantic/source/governance drift：
   - 記錄；
   - 分類；
   - reconcile；
   - 不得偷偷使用過時假設。

基本原則：

> **Repository 是 durable source of truth。**

聊天只是：

`requirement input / architectural intent / historical clue`

不是 authoritative execution state。

---

# 1. 最新高階方向

目前已經得到的重要方向如下。

你必須 fresh 驗證，若沒有 repository evidence 反駁，原則上沿用。

主線不再是：

`先把所有 automation 做完 → 才回產品`

主線改為：

`完整 V1 architecture/contracts`
→ `可用產品 vertical slices`
→ `operational simulation`
→ `recovery/workstation`
→ `deployment`
→ `V1 release`

Automation：

與產品線交錯演進。

Automation 的存在是為了：

**提高產品開發 throughput。**

不是把 Automation 本身變成新的主要產品。

---

# 2. V1 Product Definition

V1：

`Personal Futures Research & Simulation Workstation`

V1 必須至少支援：

- single user；
- local deploy；
- browser UI；
- reproducible historical research；
- dataset versioning；
- backtest；
- result comparison；
- parameter research；
- OOS；
- WFO；
- Monte Carlo；
- incremental strategy runtime；
- multi-strategy decision；
- risk / capital；
- deterministic simulation；
- canonical OMS；
- expected position；
- actual observation；
- reconciliation；
- PostgreSQL operational state；
- crash recovery；
- Python API；
- ASP.NET application/BFF；
- React frontend；
- audit；
- install；
- health；
- diagnostics；
- backup；
- restore；
- BACKTEST mode；
- SIMULATED mode。

V1 不要求：

- LIVE_AUTO；
- LIVE_CONFIRM；
- real production broker；
- multi-tenant SaaS；
- Kubernetes；
- microservices；
- Kafka；
- RabbitMQ；
- multi-account；
- all-asset platform。

Shioaji / broker adapter：

保留正式 architecture boundary。

但是：

**V1 必須在沒有任何真實 broker credentials 的環境完整驗收。**

---

# 3. 本輪核心任務

本輪第一個核心交付：

`P00 — V1 CONTRACT / ARCHITECTURE / EXECUTION BASELINE`

但是 P00 不只是文件。

P00 必須完成：

> **所有低階模型不應自行決定的 semantics / contract / authority / ownership / failure behavior / state transition / transaction boundary / acceptance criteria。**

未來理想狀態：

### 高階 GPT

主要處理：

- architecture；
- semantics；
- dependency；
- cross-layer decisions；
- optimization；
- difficult diagnosis；
- new-domain planning。

### WORK

主要處理：

- planning；
- package compilation；
- prioritization；
- orchestration；
- result intake；
- review routing；
- progress accounting。

### CODEX

主要處理：

- bounded coding；
- tests；
- migrations；
- implementation evidence。

而不是：

`CODEX 寫`
→ `Reviewer 發現 architecture 不完整`
→ `RF`
→ `再 RF`
→ `Architect 補規格`
→ `重寫`

---

# 4. 第一階段：建立 Current Authoritative Program Model

fresh inspect 至少包括：

- `AGENTS.md`
- `docs/CURRENT_STATE.md`
- `docs/CURRENT_WORK.md`
- `docs/AI_HANDOFF.md`
- Architecture docs
- ADR
- GAP records
- GAP closure
- current roadmap
- Program V2
- product blueprints
- automation manifest
- automation policies
- capacity policy
- authorization policy
- context loading policy
- work orders
- reviews
- accepted integration evidence
- AUTO-IMP series
- scripts
- SKILL definitions
- AGENT definitions
- prompts/templates
- automation controllers
- token telemetry
- Python core
- strategy
- backtest
- decision
- risk
- OMS
- account
- persistence
- recovery
- simulation
- API/service
- ASP.NET
- React
- PostgreSQL
- migrations
- deployment
- tests
- CI

建立：

`CURRENT AUTHORITATIVE PROGRAM MODEL`

至少分類：

```text
ACCEPTED
IMPLEMENTED_NOT_ACCEPTED
DESIGNED
PLANNED
OBSOLETE
CONFLICTING
BLOCKED
EXTERNAL_ONLY
NOT_STARTED
```

並明確標記：

- current authority；
- active execution；
- review pending；
- integration pending；
- current blockers；
- current critical path；
- V1 maturity；
- automation maturity；
- AI development platform maturity。

---

# 5. 不允許無條件重做

這是重要規則。

對所有：

- SKILL；
- AGENT；
- prompt；
- context loader；
- automation script；
- controller；
- telemetry；
- templates；
- bootstrap；
- testing helper；
- manifest；
- policies；

先建立：

`CAPABILITY INVENTORY`

每項分類：

```text
KEEP
KEEP_AND_STANDARDIZE
REFACTOR
CONSOLIDATE
REPLACE
DEPRECATE
MISSING
```

禁止：

**因為新架構比較漂亮就重做已有且運作良好的能力。**

---

# 6. 建立成熟度模型

對已有工程能力評估：

```text
L0 = absent
L1 = ad-hoc
L2 = repeatable
L3 = standardized
L4 = automated
L5 = measured + continuously optimized
```

至少評估：

- architecture memory；
- GPT bootstrap；
- context loading；
- package compiler；
- WORK planning；
- CODEX execution；
- reviewer workflow；
- integration；
- acceptance；
- telemetry；
- skill reuse；
- agent reuse；
- test generation；
- contract generation；
- migration generation；
- debugging；
- incident learning；
- forecasting；
- adaptive scheduling；
- release management。

不要因為功能「存在」就視為完成。

存在但：

- 不能 discover；
- 不 reusable；
- 不 deterministic；
- 沒有測試；
- 沒 telemetry；
- 沒版本；
- 新 GPT 不知道如何用；

都視為仍需改善。

---

# 7. Product Architecture Completion

你必須一次補完整 V1 尚未定義清楚的 architecture。

只要可以從：

- repo；
- accepted design；
- project objectives；
- engineering best practice；

合理推導，

就直接 freeze candidate。

只有以下才回 Human：

- 真實資金；
- LIVE；
- broker credentials；
- irreversible external effect；
- security secret；
- 多個合理產品方向且差異重大；
- domain intent 無法推導。

---

# 8. Product Boundary

正式定義：

```text
V1
V1.x
V2
Future
Broker Paper
LIVE_CONFIRM
LIVE_AUTO
```

避免 roadmap scope creep。

---

# 9. Domain Ownership

每項只能有一個 authoritative owner：

- Market data
- Dataset
- Calendar
- Contract identity
- Strategy definition
- Strategy instance
- Strategy config
- Incremental state
- Signal
- Decision
- Target position
- Risk
- Capital
- OrderIntent
- OMS
- Expected position
- Actual observation
- Reconciliation
- Account
- Persistence
- Recovery
- Backtest
- Simulation
- Research job
- Artifact
- Authentication
- Permission
- App workflow
- UI state
- Audit
- Development execution state

禁止 authority overlap。

---

# 10. Canonical Contracts

至少 freeze：

- DatasetManifest
- DatasetVersion
- MarketBar
- ContractIdentity
- ContractMapping
- StrategyDefinition
- StrategyVersion
- StrategyInstance
- StrategyConfigVersion
- Decision
- RiskDecision
- CapitalState
- OrderIntent
- Order
- Fill
- Position
- ExpectedPosition
- ActualPositionObservation
- ReconciliationCase
- SimulationSession
- ResearchRun
- Operation
- OperationAttempt
- ArtifactManifest
- AuditEvent

每項定義：

```text
identity
version
immutability
owner
persistence
timestamp
revision
idempotency
recovery
compatibility
```

---

# 11. Money / Time / Identity

一次 freeze：

- Decimal policy；
- JSON serialization；
- exchange timezone；
- storage timezone；
- session boundary；
- causal ordering；
- sequence；
- revision；
- contract expiry；
- overnight session；
- continuous contract；
- corrected data；
- immutable historical run identity；
- deterministic seed。

不得交給 executor 自行決定。

---

# 12. State Machines

至少完成：

- ResearchRun
- Operation
- OperationAttempt
- Worker lease
- Strategy runtime
- Simulation session
- Order
- Cancel
- Reconciliation
- Account readiness
- Recovery
- Automation Work Order
- Execution
- Review
- Integration
- Acceptance

每個 state machine 必須有：

```text
states
legal transitions
transition authority
side effects
retry semantics
crash semantics
unknown semantics
terminal state
audit requirement
```

---

# 13. Cross-layer Architecture

freeze：

```text
Python Core
    ↓
Python Versioned API
    ↓
ASP.NET Application / BFF
    ↓
React
```

## Python

唯一管理：

- trading economics；
- strategy runtime；
- decision；
- risk；
- capital；
- OMS；
- expected positions；
- reconciliation；
- recovery；
- simulation；
- research engine；
- operational trading state。

## ASP.NET

管理：

- user auth；
- permission；
- browser workflow；
- application orchestration；
- API mediation；
- frontend DTO；
- application-level validation。

不得形成第二套 trading engine。

## React

只負責：

- presentation；
- interaction；
- application state projection。

沒有：

- trading authority；
- risk authority；
- economic authority。

---

# 14. API Contract

至少涵蓋：

```text
GET  /api/v1/datasets
GET  /api/v1/strategies

POST /api/v1/research-runs
GET  /api/v1/operations/{id}
POST /api/v1/operations/{id}/cancel
GET  /api/v1/research-runs/{id}/results

POST /api/v1/simulation-sessions
POST /api/v1/simulation-sessions/{id}/commands

GET /api/v1/accounts/{id}/state
GET /api/v1/reconciliation-cases
GET /api/v1/audit
GET /api/v1/system/status
```

每個 endpoint：

- request；
- response；
- validation；
- permission；
- authority；
- idempotency；
- expected revision；
- transaction；
- async/sync；
- errors；
- retry；
- cancellation；
- pagination；
- audit；
- examples。

若 OpenAPI 最合理：

建立正式 machine-readable OpenAPI baseline。

---

# 15. Persistence / Transaction Architecture

完成：

- PostgreSQL schemas；
- research metadata；
- operational schema；
- application schema；
- audit schema；
- DB roles；
- Python write role；
- ASP.NET write role；
- migrations；
- transaction boundary；
- UoW；
- isolation；
- optimistic revision；
- worker lease；
- claim；
- recovery；
- artifact references；
- retention；
- backup；
- restore。

大 research artifact：

可使用：

`Parquet / files / DuckDB`

PostgreSQL 保存：

- manifest；
- identity；
- hash；
- metadata；
- state。

---

# 16. Backtest / Runtime Convergence

不得全面重寫已驗收 core。

正式規劃：

```text
legacy
→ compatibility adapter
→ canonical model
→ canonical operational authority
```

避免：

第二套 operational truth。

---

# 17. Strategy / Decision / Risk Architecture

freeze：

```text
Observation
↓
Strategy Instances
↓
Signals
↓
Multi-Strategy Decision
↓
Risk / Capital
↓
Target Position
↓
OrderIntent
↓
OMS
```

Strategy 不直接操作 account。

涵蓋：

- long；
- short；
- add；
- reduce；
- exit；
- enter；
- reverse；
- conflicting strategy；
- margin；
- capital；
- risk reduction；
- rejection provenance。

Reverse：

`EXIT → confirmed FLAT → re-evaluate → ENTER`

---

# 18. Simulation Architecture

建立正式：

`SimulationBroker`

至少支援：

- deterministic clock；
- deterministic seed；
- partial fill；
- reject；
- cancel；
- cancel race；
- duplicate；
- out-of-order；
- disconnect；
- stale data；
- missing data；
- retry；
- restart。

必須保持：

`SimulationBroker ≠ Shioaji Broker Paper`

---

# 19. Research Architecture

正式整合：

```text
Dataset
→ ResearchRun
→ Durable Operation
→ Worker
→ Backtest
→ Artifact
→ Result API
→ ASP.NET
→ React
```

包含：

- compare；
- parameter；
- OOS；
- WFO；
- Monte Carlo；
- seed；
- dataset hash；
- code SHA；
- strategy version；
- config；
- cost model；
- reproducibility；
- cancel；
- export；
- pagination。

---

# 20. Deployment Architecture

V1 必須是產品。

補完：

- install；
- bootstrap；
- PostgreSQL；
- Python host；
- Python worker；
- ASP.NET；
- React；
- configuration；
- secret isolation；
- logs；
- health；
- startup；
- shutdown；
- restart；
- backup；
- restore；
- migration；
- upgrade；
- diagnostics；
- demo data；
- runbook。

---

# 21. V1 Release Journeys

freeze 六條：

1. Research
2. Comparison
3. Simulation
4. Failure
5. Recovery
6. Deployment

每條定義：

```text
preconditions
steps
expected outputs
test type
evidence
owner
gate
```

只有：

`6 / 6`

才能稱：

`V1 COMPLETE`

---

# 22. Durable Project Memory Architecture

這是強制要求。

任何 Architecture / Governance / Program truth：

**不得只存在聊天。**

要求：

```text
clone
→ checkout
→ bootstrap
→ understand
→ continue
```

新的 GPT 不需要讀舊對話即可接手。

---

# 23. Durable Memory 分層

如果 repo 已存在 equivalent：

優先 consolidate，而不是新增重複文件。

## Tier 1 — Stable Architecture

例如：

```text
docs/architecture/
    V1_MASTER_ARCHITECTURE.md
    V1_PRODUCT_SCOPE.md
    V1_DOMAIN_CONTRACTS.md
    V1_STATE_MACHINES.md
    V1_DATA_ARCHITECTURE.md
    V1_API_ARCHITECTURE.md
    V1_APPLICATION_ARCHITECTURE.md
    V1_DEPLOYMENT_ARCHITECTURE.md
```

---

## Tier 2 — Program

```text
docs/program/
    V1_MASTER_ROADMAP.md
    V1_PACKAGE_GRAPH.md
    V1_ACCEPTANCE_MATRIX.md
    V1_PROGRESS_MODEL.md
```

---

## Tier 3 — Current Projection

```text
docs/CURRENT_STATE.md
docs/CURRENT_WORK.md
docs/AI_HANDOFF.md
```

要求：

- compact；
- current only；
- 不累積完整歷史；
- history 交給 Git；
- pointer 到 evidence。

---

## Tier 4 — Machine-readable

例如：

```text
program_baseline.v1.yaml
deliverables.v1.yaml
dependency_graph.v1.yaml
progress_ledger.v1.yaml
architecture_contract_manifest.v1.yaml
context_loading_policy.v1.yaml
automation_operating_model.v1.yaml
ai_capability_registry.v1.yaml
skill_registry.v1.yaml
agent_registry.v1.yaml
```

Machine-readable 文件：

只做 index / state / contract。

不能產生另一套互相衝突的 truth。

---

# 24. Source-of-truth Precedence

正式 freeze：

```text
1. Git authoritative branch
2. Accepted Architecture / ADR
3. Active Program Baseline
4. Accepted execution/review/integration evidence
5. Machine-readable current projection
6. Compact CURRENT docs
7. Latest repository delta
8. Historical records
9. Chat
```

---

# 25. AI_CONTEXT_BOOTSTRAP

建立正式 bootstrap。

新 GPT / Agent 接手：

```text
1. Fetch master
2. Read AGENTS / bootstrap
3. Read capability registry
4. Read context manifest
5. Read compact CURRENT
6. Read active package
7. Read relevant contracts only
8. Read latest relevant delta
```

禁止：

每次重讀全部 repository history。

---

# 26. Progressive Context Loading

建立可機械執行的：

`Context Resolver`

輸入：

```text
task_type
package_id
changed_paths
architecture_domains
baseline_sha
```

輸出：

```text
mandatory_context
optional_context
forbidden_stale_context
evidence_refs
context_hash
```

目標：

**同樣任務，不因不同 GPT 而每次載入完全不同資料。**

---

# 27. AI Development Platform

這是這次新增的核心層。

建立：

`AI DEVELOPMENT PLATFORM`

它不是產品 runtime。

它是：

> **讓每次 AI 開發都能重用上一輪已學會能力的工程平台。**

架構至少包含：

```text
Knowledge Plane
Skill Plane
Agent Plane
Template Plane
Tool Plane
Execution Plane
Evaluation Plane
Telemetry Plane
Optimization Plane
```

---

# 28. Skill Plane

建立 repository-local：

`SKILL REGISTRY`

每個 Skill 應有：

```yaml
skill_id:
version:
purpose:
trigger:
inputs:
required_context:
outputs:
allowed_tools:
side_effects:
preconditions:
failure_modes:
validation:
examples:
owner:
compatibility:
```

---

# 29. 初期建議 Skills

先 inventory 已存在能力。

只有缺少才建立。

至少評估是否需要：

```text
repo-rehydrate
context-bootstrap
architecture-read
package-compiler
dependency-resolver
scope-validator
contract-validator
test-impact-analyzer
test-plan-generator
migration-planner
review-preflight
review-diff-analyzer
result-intake
integration-preflight
progress-calculator
token-estimator
cost-reconciler
failure-classifier
incident-to-regression
documentation-sync
release-preflight
current-projection-builder
```

不要建立巨大萬能 Skill。

Skill 原則：

**單一責任 + 可組合 + 可測試。**

---

# 30. Skill Reuse Rule

每次建立新功能前：

先問：

```text
CAN_EXISTING_SKILL_HANDLE_THIS?
```

順序：

```text
Reuse
→ Parameterize
→ Compose
→ Extend
→ Only then create new Skill
```

禁止：

同樣功能因 package 不同就複製 Skill。

---

# 31. Skill Quality Gate

Skill 不能因為有 prompt file 就算完成。

至少必須具備：

```text
version
defined inputs
defined outputs
bounded responsibility
test fixture
positive example
negative example
failure semantics
compatibility
telemetry
```

成熟 Skill 應達：

`L3+`

關鍵 Skill：

目標 `L4/L5`。

---

# 32. Agent Plane

建立正式：

`AGENT REGISTRY`

不要讓「Agent」只是不同聊天名稱。

每個 Agent 必須有：

```yaml
agent_id:
role:
authority:
allowed_decisions:
forbidden_decisions:
input_contract:
output_contract:
skills:
tools:
context_policy:
handoff_contract:
stop_conditions:
evaluation:
```

---

# 33. 建議 Agent 架構

先 inventory 現況，再 consolidate。

原則上可形成：

### ARCHITECT

負責：

- architecture；
- semantics；
- program structure；
- complex reconciliation。

### WORK

負責：

- package planning；
- ready-set；
- prioritization；
- orchestration。

### CODEX

負責：

- bounded implementation。

### REVIEWER

負責：

- independent verification；
- semantic review；
- scope review。

### INTEGRATOR

負責：

- integration preflight；
- merge eligibility；
- evidence preservation。

### CONTROLLER

負責：

- wake；
- intake；
- legal ready-set；
- dispatch；
- progression。

必要時才建立：

### RESEARCH AGENT

針對：

- library/API/tool investigation；
- external technical research。

### RELEASE AGENT

針對：

- release acceptance；
- deployment evidence。

不要 agent proliferation。

---

# 34. Agent Authority Hierarchy

正式定義：

```text
Human Owner
    ↓
Architecture Baseline
    ↓
Bounded Wave Authority
    ↓
Controller
    ↓
WORK
    ↓
CODEX
```

Reviewer：

獨立於 CODEX。

不得因同一模型執行兩個 role 就混淆 authority。

---

# 35. Agent Handoff Protocol

任何 handoff 不使用自由散文做唯一介面。

至少包含：

```text
FROM
TO
BASELINE_SHA
PACKAGE_ID
STATE
AUTHORITY
COMPLETED
EVIDENCE
OPEN_FINDINGS
NEXT_ALLOWED_ACTIONS
STOP_CONDITIONS
```

目標：

換模型不丟失 lifecycle state。

---

# 36. Template Plane

建立高價值 template library。

例如：

```text
package template
architecture decision template
API contract template
state machine template
migration plan template
review template
incident template
release template
execution result template
handoff template
```

新功能：

不從空白開始。

---

# 37. Generator Architecture

凡是可以 deterministic 產生的 artifact：

不要每次靠 GPT 手寫。

評估建立 generator：

```text
package generator
OpenAPI skeleton generator
DTO skeleton generator
test matrix generator
migration checklist generator
review checklist generator
current projection generator
progress report generator
handoff generator
```

原則：

**AI 決定 semantics，generator 處理重複格式。**

---

# 38. Tool Plane

建立：

`TOOL CAPABILITY REGISTRY`

記錄：

- local scripts；
- PowerShell；
- pytest；
- Git；
- GitHub；
- schema tools；
- linters；
- formatters；
- DB tools；
- OpenAPI tools；
- React tooling；
- .NET tooling；
- token tools；
- future MCP / plugin / connector tools。

每項記錄：

```text
purpose
version
availability
cost
side effects
reliability
fallback
```

---

# 39. Vendor-independent Architecture

SKILL / AGENT / tool design：

不要和某個 GPT UI 或單一 vendor 綁死。

優先設計：

```text
repository-local specification
+
provider adapter
```

例如：

同一個 `package-compiler` skill，

未來可以由：

- GPT；
- WORK；
- CODEX；
- local agent；
- other LLM；

共用。

---

# 40. Evaluation Plane

建立：

`AI DEVELOPMENT EVALUATION`

沒有 eval：

不能知道「新方法比較有效」。

至少建立：

### Golden Tasks

保存一組代表性任務：

```text
architecture comprehension
small feature
cross-layer feature
bug fix
migration
review fix
recovery issue
API change
frontend change
```

每次重大：

- prompt；
- Skill；
- Agent；
- context；
- routing；
- model；

改動，

可以用 golden tasks 檢查是否變好。

---

# 41. AI Development KPIs

不要只看 tokens。

至少追蹤：

```text
accepted work / token
accepted work / execution
first-pass acceptance rate
review findings / package
architecture-related RF rate
context loading size
context reuse rate
execution correction count
human intervention frequency
forecast accuracy
lead time
cycle time
escaped defect rate
repeated defect rate
```

最重要的是：

`accepted engineering value`

不是：

`output volume`

---

# 42. Optimization Plane

建立：

`CONTINUOUS DEVELOPMENT OPTIMIZATION LOOP`

流程：

```text
Execution
→ Telemetry
→ Review findings
→ Failure classification
→ Root cause
→ Improvement candidate
→ Skill/Agent/Contract/Tool improvement
→ Eval
→ Accept improvement
→ Version
```

---

# 43. 不允許只修 Prompt

當同類錯誤重複出現：

第一次：

修 implementation。

第二次：

必須判斷是否應修：

- contract；
- Skill；
- Agent；
- fixture；
- test；
- generator；
- context policy；
- package schema。

第三次還用 prompt 提醒：

視為流程設計失敗。

---

# 44. Optimization Backlog

建立獨立：

`ENGINEERING SYSTEM OPTIMIZATION BACKLOG`

但不能搶走產品主線。

每個 optimization item 必須有：

```text
observed_problem
frequency
cost
root_cause
proposed_improvement
expected_gain
implementation_cost
risk
measurement
```

只優先做：

`ROI 高`

的優化。

---

# 45. 新 GPT 最快接手目標

設定 measurable target。

新 GPT 接手不應：

- 讀數千行歷史；
- 猜 architecture；
- 問使用者目前做到哪；
- 重做 repo review。

理想 bootstrap：

```text
Repository identity
↓
Architecture summary
↓
Current state
↓
Active package
↓
Relevant contracts
↓
Recent delta
```

完成後應可以回答：

```text
What are we building?
Where are we?
What is authoritative?
What is active?
What is blocked?
What can I change?
What can I not decide?
What is next?
```

---

# 46. 新功能開發 Fast Path

任何未來新功能採：

```text
Feature Request
↓
Requirement Compiler
↓
Existing capability/Skill lookup
↓
Architecture impact analysis
↓
Contract delta
↓
Dependency graph
↓
Package compile
↓
Implementation
↓
Verification
↓
Acceptance
↓
Knowledge update
```

不是：

`Prompt → CODEX → 看結果`

---

# 47. Feature Classification

新功能先分類：

```text
L0 Local implementation only
L1 Existing contract extension
L2 Cross-module contract change
L3 Architecture change
L4 Product scope / authority change
```

對應：

### L0/L1

低階 WORK/CODEX 可完成。

### L2

可能需高階 GPT narrow design。

### L3

Architect。

### L4

Architect + Human Owner。

避免所有工作都升級到 GPT-6。

---

# 48. 新功能 Context Pack

Feature package 自動生成：

```text
FEATURE_CONTEXT_PACK
```

包含：

- relevant architecture；
- contracts；
- changed modules；
- dependencies；
- tests；
- similar previous feature；
- available Skills；
- constraints；
- authority。

未來 CODEX 不需要讀整個 repo。

---

# 49. Pattern Library

將成功的 implementation patterns 累積成：

`ENGINEERING PATTERN LIBRARY`

例如：

```text
new API endpoint
new background job
new DB migration
new strategy
new risk rule
new React page
new ASP.NET workflow
new simulation scenario
new audit event
new durable operation
```

Pattern：

不是複製程式碼。

而是：

`recommended architecture + checklist + reference implementation`

---

# 50. Reference Implementations

對常見跨層功能，

建立少量高品質 reference slice。

例如：

```text
Dataset list
Research run
Operation status
Simulation command
Audit query
```

未來低階模型：

模仿已驗證 pattern，

而不是重新設計。

---

# 51. Documentation as Code

對可驗證文件建立：

- schema check；
- link check；
- manifest check；
- package consistency；
- contract version check；
- stale pointer check。

避免 docs 漂移。

---

# 52. Architecture Conformance

評估建立自動 conformance checks：

例如：

```text
React cannot import Python
ASP.NET cannot write trading tables
Strategy cannot call broker adapter directly
legacy portfolio cannot become runtime owner
LIVE modes unavailable in V1
```

能機械檢查就不要全靠 Reviewer 記憶。

---

# 53. Test Architecture

建立 test pyramid / matrix：

```text
contract
unit
property
state-machine
integration
cross-language
DB
simulation
recovery
E2E
release journey
```

Package compiler 自動決定：

`required test impact set`

而不是每次 full suite。

---

# 54. Test Reuse

同：

- SHA；
- environment；
- dependencies；
- test inputs；

且 impact graph 證明無影響時：

允許重用 evidence。

降低重複測試成本。

---

# 55. Failure Knowledge

建立：

`FAILURE / INCIDENT KNOWLEDGE`

當出現：

- repeated RF；
- flaky test；
- source identity error；
- stale context；
- integration blocker；
- migration failure；

不要只留聊天。

轉成：

```text
cause
symptom
detection
resolution
prevention
regression
```

---

# 56. Automation 重組

不要僵化：

`003 → 004 → ... → 009`

重新評估並 consolidate 成：

### A1

`Exact lifecycle / authority guard + negative tests`

### A2

`Durable result → review → integration → acceptance + entrypoint`

### A3

`Controlled dispatch / wake / adaptive selection`

舊 packages：

只有真正有獨立價值才保留。

---

# 57. Adaptive Development Controller

正式架構：

```text
WAKE
→ rehydrate
→ authority/delta
→ unfinished execution
→ result intake
→ review
→ integration
→ acceptance
→ legal ready set
→ rank
→ execute / prepare / wait
→ persist
→ forecast
→ next wake
```

---

# 58. Legal Gate

```text
LEGAL =
    AUTHORITY_AVAILABLE
    AND DEPENDENCIES_READY
    AND EXACT_SCOPE_COMPILED
    AND NO_HIGHER_PRIORITY_UNFINISHED_WORK
    AND WRITER_AVAILABLE
    AND REQUIRED_ENVIRONMENT_AVAILABLE
```

Capacity：

**不能創造 authority。**

---

# 59. Priority Model

固定 deterministic baseline，例如：

```text
benefit =
    4 × critical_path_priority
  + 3 × engineering_value
  + 2 × dependency_unlock_value
  + 1 × context_reuse_value
  + 1 × aging_credit

cost =
    normalized_expected_time
  + normalized_expected_token_cost
  + correction_risk

priority =
    benefit / max(cost, minimum_cost)
```

rating：

`0–5`

不要讓 WORK 自行每天發明新公式。

---

# 60. WORK Contract

WORK：

`Planner / Orchestrator`

可以：

- context load；
- ready-set；
- scoring；
- package compilation；
- token estimate；
- scheduling；
- dispatch；
- intake；
- review route；
- progress update。

不能決定：

- new trading semantics；
- new risk policy；
- economic ownership；
- architecture authority；
- LIVE；
- new transaction semantics。

---

# 61. CODEX Contract

輸入：

```text
baseline SHA
package
authority
exact scope
protected scope
contracts
tests
acceptance
stop conditions
estimated cost
```

輸出：

```text
candidate SHA
changed files
commands
tests
PASS
FAIL
NOT_RUN
BLOCKED
remaining findings
scope compliance
telemetry
COMPLETED_PENDING_REVIEW
```

CODEX 不得：

- ACCEPT 自己；
- 擴 scope；
- 發明 semantics；
- 創造 authority。

---

# 62. Package Compiler

標準 schema 至少：

```yaml
identity:
  package_id:
  revision:
  baseline_sha:
  requirement_ids:
  deliverable_weights:

authority:
  parent_wave_grant:
  exact_scope:
  protected_scope:
  allowed_side_effects:
  correction_budget:

design:
  owners:
  input_output_schemas:
  state_transitions:
  transaction_boundary:
  idempotency_and_recovery:
  error_and_unknown_semantics:
  compatibility_rules:

dependencies:
  required_acceptances:
  external_gates:
  parallel_or_parked_work:

verification:
  positive_examples:
  counterexamples:
  targeted_tests:
  integration_tests:
  regression_impact_set:
  independent_review_scope:

completion:
  evidence_artifacts:
  acceptance_checks:
  stop_conditions:
```

缺 public semantics：

`PACKAGE_NOT_READY`

---

# 63. Review Model

Finding 分類：

```text
LEGITIMATE_DEFECT
DESIGN_INCOMPLETENESS
GOVERNANCE_OVERHEAD
CONTEXT_FAILURE
SCOPE_FRAGMENTATION
TOOL_FAILURE
EXTERNAL_ENVIRONMENT
```

不要把所有問題都變 RF。

---

# 64. Correction Budget

預設：

```text
Implementation correction <= 2
Review fix <= 2
```

tool/environment retry 不算。

Architecture change：

不可藏在 RF。

超過：

`ARCHITECTURE_RECONCILIATION_REQUIRED`

---

# 65. Progress Accounting

不用 commits / packages 數量當完成率。

正式：

```text
engineering_completion =
Σ(deliverable_weight × gate_credit) / baseline_weight
```

Gate：

```text
implementation        40%
targeted verification 20%
integration           20%
independent acceptance20%
```

Design：

另計。

Release：

```text
deployable_completion =
passed_release_journeys / 6
```

---

# 66. AI Development Progress

另外建立：

`DEVELOPMENT_PLATFORM_MATURITY`

不要和產品進度混合。

例如：

```text
Context System
Skills
Agents
Package Compiler
Review Automation
Telemetry
Adaptive Controller
Evals
Generators
Continuous Optimization
```

各自 L0–L5。

---

# 67. Telemetry

WORK dispatch 前：

```text
EXPECTED_TOKEN
EXPECTED_DURATION
EXPECTED_SCOPE
EXPECTED_TEST_COST
CONFIDENCE
```

CODEX 後：

```text
ACTUAL_TOKEN
ACTUAL_DURATION
ACTUAL_SCOPE
ACTUAL_TEST_COST
```

Controller：

```text
forecast_error
error_reason
model
provider
task_type
context_size
skill_usage
agent_usage
correction_count
review_findings
accepted_weight
```

---

# 68. Skill / Agent Telemetry

額外記錄：

```text
skill_invocations
skill_success_rate
skill_failure_rate
skill_token_saving
skill_time_saving

agent_first_pass_rate
agent_correction_rate
agent_context_cost
agent_handoff_failures
```

沒有 evidence：

不要宣稱新 Agent / Skill 比舊流程有效。

---

# 69. Model Routing

建立：

`MODEL ROUTING POLICY`

不是所有工作使用最高階 GPT。

至少分類：

### High reasoning

用於：

- architecture；
- difficult semantic conflict；
- large reconciliation；
- root cause；
- complex planning。

### Medium

用於：

- WORK planning；
- review；
- package compilation；
- moderate debugging。

### Lower-cost executor

用於：

- bounded CODEX；
- boilerplate；
- mechanical migrations；
- tests；
- generated docs。

路由依：

```text
task complexity
risk
uncertainty
contract completeness
expected value
cost
```

---

# 70. Escalation Policy

低階模型只有在：

```text
missing public semantics
contradictory contract
architecture boundary conflict
unbounded scope
authority missing
high-risk unknown
```

才 escalation。

不得：

「覺得不確定就全部問 GPT-6」。

---

# 71. Development Efficiency Budget

Automation / tooling / Skills improvement：

不能無上限投入。

近期原則：

產品 delivery 為主。

Development-system optimization：

只有在以下情況優先：

```text
blocks critical path
repeatedly causes correction
high reuse potential
clear measurable ROI
```

---

# 72. Optimization ROI

每個開發效率改善：

計算大致：

```text
expected_future_saving
× expected_reuse_count
× error_reduction
/
implementation_cost
```

高 ROI：

優先。

只「看起來很先進」：

不做。

---

# 73. 分階段 AI Development Platform Roadmap

不要企圖一次把所有 AI 工具做到完美。

## Phase D0 — Inventory

完成：

- Skill inventory；
- Agent inventory；
- Tool inventory；
- Context inventory；
- duplicated capability detection。

---

## Phase D1 — Standardize

完成：

- registries；
- contracts；
- bootstrap；
- templates；
- machine-readable metadata。

---

## Phase D2 — Reuse

完成：

- package compiler；
- context resolver；
- reusable Skills；
- reference patterns。

---

## Phase D3 — Automate

完成：

- result intake；
- review routing；
- integration preflight；
- current projection；
- progress accounting。

---

## Phase D4 — Measure

完成：

- telemetry；
- eval；
- forecast calibration；
- Skill/Agent KPIs。

---

## Phase D5 — Optimize

完成：

- adaptive routing；
- model selection；
- package sizing；
- context optimization；
- automatic improvement proposals。

不能跳過：

`Measure`

就直接宣稱 optimized。

---

# 74. 新 GPT / 新模型升級 SOP

當未來出現更好的 GPT / CODEX / Agent：

不要整套重寫流程。

執行：

```text
1. Run golden tasks
2. Compare baseline
3. Compare cost
4. Compare first-pass acceptance
5. Compare architecture compliance
6. Compare context use
7. Shadow rollout
8. Limited adoption
9. Promote
```

Provider/model：

是可替換執行元件。

Architecture：

不依賴單一模型。

---

# 75. 新工具 / 新 Skill 導入 SOP

任何新的：

- MCP；
- plugin；
- CLI；
- AI Agent；
- Skill；
- code analyzer；

都先：

```text
capability gap
security
side effects
reliability
cost
integration effort
measurable value
fallback
```

通過後才納入正式 registry。

---

# 76. Security / Safety of AI Development

Agents / tools：

最小權限。

至少區分：

```text
READ
WRITE_REPO
COMMIT
PUSH
MERGE
EXTERNAL_NETWORK
BROKER
SECRET_ACCESS
```

Trading credentials：

永遠不得因 development automation 自動取得。

---

# 77. Main V1 Package DAG

重新驗證：

```text
P00 V1 contract baseline
P01 reproducible data/time
P02 Python/API + ASP.NET + React thin slice
P03 durable jobs + PostgreSQL
P04 usable research workflow
P05 incremental strategy
P06 decision/risk/capital
P07 canonical simulation/OMS
P08 durable runtime
P09 operational workstation
P10 advanced research
P11 install/operations
P12 V1 release
```

可以依 fresh evidence：

- merge；
- split；
- reorder。

但必須記錄 WHY。

---

# 78. 第一批目標

理想：

```text
P00 ACCEPTED
    ├── P01
    ├── P02
    └── A1
```

其中產品優先。

第一個真正產品 vertical slice：

```text
Historical Dataset
→ Backtest
→ Python API
→ ASP.NET
→ React
```

必須：

- 可操作；
- 可重跑；
- 可驗證；
- 可追溯。

---

# 79. Fast Feedback Strategy

優先建立 vertical slice，

而不是先完成整層 backend。

每次 major stage：

盡快形成：

`User-visible + End-to-end + Testable`

避免：

半年後才第一次整合 UI。

---

# 80. 禁止事項

禁止：

1. 全面重寫已驗收 core。
2. 為漂亮架構導入 microservices。
3. ASP.NET 成為第二套 trading engine。
4. React 保存 authoritative economic state。
5. legacy paper portfolio 成為 canonical runtime owner。
6. automation 完成才回產品。
7. WORK/CODEX 發明 semantics。
8. Chat 成為 durable memory。
9. 新 GPT 每次重讀完整 history。
10. 為每個 package 建一套 Skill。
11. Agent proliferation。
12. 沒有 eval 就宣稱新流程更快。
13. 把生成文件量當進度。
14. 因 quota 把 cohesive architecture 拆碎。
15. 使用高階 GPT 做大量機械工作。
16. 因低階模型便宜就讓它處理未定義 architecture。

---

# 81. Local + Git Memory

所有正式：

- architecture；
- Skill；
- Agent；
- template；
- context policy；
- package；
- eval；
- progress；
- automation；

必須：

`Git-trackable`

critical truth 不得只存在：

- `.tmp`
- local cache
- ChatGPT conversation
- human memory

---

# 82. Repository Materialization Principle

不要一次建立大量重複文件。

優先：

```text
reuse
→ consolidate
→ normalize
→ only then create
```

若既有檔案可承擔責任：

update 它。

不要建立：

`V1_MASTER_ARCHITECTURE_FINAL_FINAL_V2.md`

---

# 83. Current Projection Optimization

若 CURRENT_STATE / CURRENT_WORK 過肥，

改成：

```text
Current status
Active execution
Accepted baseline
Current blockers
Next legal action
Progress
Pointers
```

History：

Git / evidence。

---

# 84. 本輪 Deliverables

本輪至少要完成：

```text
[ ] Fresh repository reconciliation
[ ] Capability inventory
[ ] Architecture gap analysis
[ ] V1 scope baseline
[ ] Product architecture
[ ] Domain contracts
[ ] State machines
[ ] API architecture
[ ] Persistence architecture
[ ] Simulation architecture
[ ] Research architecture
[ ] Application architecture
[ ] Deployment architecture
[ ] V1 acceptance journeys

[ ] Durable project memory
[ ] Source-of-truth model
[ ] AI bootstrap
[ ] Context resolver design

[ ] Skill inventory
[ ] Skill registry
[ ] Agent inventory
[ ] Agent registry
[ ] Tool registry
[ ] Template strategy
[ ] Generator strategy
[ ] Pattern library strategy

[ ] Evaluation framework
[ ] Golden-task framework
[ ] AI development KPIs
[ ] Optimization loop

[ ] Automation operating model
[ ] WORK contract
[ ] CODEX contract
[ ] Reviewer contract
[ ] Controller contract
[ ] Package compiler

[ ] Progress ledger
[ ] Token/time telemetry
[ ] Skill/Agent telemetry
[ ] Model routing policy
[ ] Escalation policy

[ ] V1 DAG
[ ] AI-development-platform roadmap
[ ] First execution-ready package(s)
[ ] Immediate next execution decision
```

---

# 85. 輸出順序

不要只交 essay。

依序輸出：

## A. Executive Decision

一句話：

`現在真正最該做什麼`

---

## B. Fresh Repository Truth

只列 current truth。

---

## C. Capability Inventory

表格：

```text
CAPABILITY
CURRENT
MATURITY
KEEP/CHANGE
WHY
TARGET
```

---

## D. Architecture Corrections

```text
KEEP
CHANGE
REMOVE
ADD
FREEZE
```

---

## E. V1 Architecture Baseline

implementation-ready。

---

## F. Durable Knowledge Architecture

列：

- files；
- source-of-truth；
- bootstrap；
- current projection。

---

## G. AI Development Platform

列：

```text
Knowledge
Skills
Agents
Templates
Tools
Evaluation
Telemetry
Optimization
```

---

## H. Skill Registry Plan

先列已有。

再列真正需要新增的。

---

## I. Agent Architecture

明確角色與 authority。

---

## J. New-GPT Bootstrap

做到新的高階 GPT 可以快速接手。

---

## K. New Feature Fast Path

做到新功能不需重新發明流程。

---

## L. Automation Operating Model

完整 daily / event SOP。

---

## M. WORK / CODEX / Reviewer / Controller Contracts

可以直接執行。

---

## N. Master V1 DAG

package / dependency / critical path。

---

## O. AI Development Platform Roadmap

D0～D5。

---

## P. Progress Dashboard

至少：

```text
V1_ENGINEERING_COMPLETION =
V1_DEPLOYABLE_COMPLETION =
CRITICAL_PACKAGES_REMAINING =
TOTAL_PACKAGES_REMAINING =

AUTOMATION_MATURITY =
AI_DEVELOPMENT_PLATFORM_MATURITY =

CURRENT_CRITICAL_STAGE =
CURRENT_HIGHEST_VALUE_ACTION =
```

---

## Q. Repository Materialization Plan

```text
CREATE
UPDATE
CONSOLIDATE
DEPRECATE
KEEP
```

---

## R. First Execution-ready Package

至少完成：

下一個 highest-value package。

若 P00 已足夠：

直接 compile P01 / P02。

---

## S. Immediate Execution Decision

只能選：

```text
READY_FOR_EXECUTION
READY_FOR_OWNER_BASELINE_APPROVAL
STOP_RECONCILIATION_REQUIRED
HUMAN_ARCHITECTURE_DECISION_REQUIRED
BLOCKED_EXTERNAL_ENVIRONMENT
```

並輸出：

```text
NEXT_ARCHITECT_ACTION =
NEXT_WORK_ACTION =
NEXT_CODEX_ACTION =
NEXT_REVIEW_ACTION =
NEXT_CONTROLLER_ACTION =
HUMAN_ACTION_REQUIRED =
```

---

# 86. 執行原則

分析完成後：

不要再停下來問：

「你要不要我建立？」

如果在 authority 範圍內可以完成：

**直接建立。**

例如：

- architecture baseline；
- registries；
- context policy；
- templates；
- schemas；
- roadmap；
- package specs；
- bootstrap。

只有真正需要 Owner approval 的事情才停。

---

# 87. 單次輸出限制

本任務：

**完整性 > 單次回答結束。**

如果無法一輪全部完成：

不得把剩餘部分壓成簡略建議。

必須：

1. 將已完成內容固化；
2. 保存 continuation state；
3. 明確列：

```text
COMPLETED_THIS_TURN =
MATERIALIZED =
REMAINING =
NEXT_CONTINUATION_POINT =
```

最後一行只寫：

`繼續`

下一輪收到「繼續」後：

直接從：

`NEXT_CONTINUATION_POINT`

開始。

不要重新 review 已完成部分。

---

# 88. 最終成功狀態

最終目標不是：

「架構文件很多」。

而是：

```text
Stable Architecture
        ↓
Durable Knowledge
        ↓
Fast GPT Bootstrap
        ↓
Reusable Skills
        ↓
Bounded Agents
        ↓
Deterministic Package Compiler
        ↓
WORK Plans
        ↓
CODEX Implements
        ↓
Reviewer Verifies
        ↓
Controller Progresses
        ↓
Telemetry Measures
        ↓
Optimization Improves
        ↓
Next Feature Becomes Faster
```

最終希望達到：

> **第一次功能可能需要高階 GPT 深度設計；第二次同類功能開始使用 Pattern / Skill / Template；第三次以後低階 WORK / CODEX 就能在已定義 architecture 中高效率完成。**

以及：

> **每次遇到問題，都不只是把問題修掉，而是判斷能否轉化成 Contract、Skill、Test、Pattern、Generator 或 Agent 改善，使同類問題不再重複消耗高階模型。**

---

# 89. 最重要的長期原則

高階 GPT 的時間應持續往：

```text
Architecture
Novel Problem
Optimization
High-risk Decision
Cross-domain Reasoning
```

集中。

低階 WORK / CODEX 的覆蓋率則持續往：

```text
Planning
Implementation
Testing
Routine Review
Integration
Documentation
Progression
```

增加。

也就是：

> **隨著專案成熟，高階 GPT 不應越來越忙，而應該因為架構、Skills、Agents、Patterns、Contracts 與 Automation 累積，而逐步只處理真正高價值的新問題。**

---

# 90. 現在開始

先：

`Fresh Repository Rehydrate`

接著：

`Current Truth`

然後：

`Capability Inventory`

再完成：

`P00 + Durable Knowledge + AI Development Platform Baseline`

最後：

**直接準備最高價值的 execution-ready package。**

不要停在 review。

不要只是提出建議。

開始執行。