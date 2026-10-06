# CURRENT — Dynamic rolling capacity successor 1.2.1

Architecture 1.2.1 ACTIVE; capacity policy2.1. Main WO-AUTO-GOV-PROGRAM-1_2-ORCH-01 / AUTH-AUTO-GOV-PROGRAM-1_2-ORCH-01-REV3 AUTHORIZED / NOT_CONSUMED; WAIT_PROVIDER_CAPACITY. No writer/execution/reservation/dispatch/invocation. ProgramV2 revision3 candidate pending cohesive implementation/review. ControlledAuto DISABLED. Capacity campaign/P01/P02/P03 SUPERSEDED_PRE_EXECUTION_BY_DYNAMIC_CAPACITY_POLICY, zero probes. Exact local tokens primary; quota identity provider/account/limit/window only; model/client/workspace/taskclass metadata. No feature-coefficient/bootstrap gate. Same-execution resume and all sideeffect denials preserved. AUTO-IMP-003 NOT_AUTHORIZED; IVF01 Rev1 baseline changed, Rev2 NOT_AUTHORIZED.

Canonical policy: automation/policies/execution_capacity_policy.v2_1.yaml; evidence: automation/work_orders/telemetry/WO-AUTO-GOV-PROGRAM-1_2-ORCH-01.rolling-capacity.json; Owner successor: automation/governance/decisions/EXECUTION-CAPACITY-DYNAMIC-ROLLING.owner.json.

KNOWN_CAPACITY_ARCHITECTURE_DEBT = NONE (complete policy design; main cohesive implementation still required).

## HISTORICAL PROJECTIONS BELOW — superseded current headings are retained audit evidence

## CURRENT — Capacity Calibration Amendment / Same Cohesive Package

Architecture 1.2 ACTIVE; current logical work remains `WO-AUTO-GOV-PROGRAM-1_2-ORCH-01`, package revision2. Owner Amendment01: `automation/governance/decisions/AMEND-AUTO-GOV-PROGRAM-1_2-ORCH-01-CAPACITY-01.json`. Exact source scope is21files: previous19 plus `automation/engine/capacity_calibration.py` and `tests/automation/test_capacity_calibration.py`. `execution_capacity.py` remains protected unchanged. Risk remains HIGH_AUTHORITY_SENSITIVE_CONTROLLER; forecast P90 remains12,000,000. One cohesive implementation and independent review, no split/waiver/floor/fallback.

Authority v1 bytes preserved: `AUTH-AUTO-GOV-PROGRAM-1_2-ORCH-01` current disposition SUPERSEDED_PRE_EXECUTION_NO_CONSUMPTION via separate disposition evidence. Current successor `AUTH-AUTO-GOV-PROGRAM-1_2-ORCH-01-REV2` revision2 AUTHORIZED, not RESERVED/CONSUMED/dispatched/invoked. No writer or execution allocated.

Historical5exacttokenruns inspected. Both PRIMARY_5H and SECONDARY_WEEKLY qualified count0. All token arithmetic PASS; original machine recovery found same-account overlappingpositive-delta sessions and no explicit provider-client-policy version. RF02 recovered model association additionally incompatible/unproven; RF01 lacks canonical pairedprovider capture. Historicalsemanticreview disposition/taskclass never automatically rejects cost/capacity samples; required identity/cleanattribution proof does. Canonical audit/cohort: `automation/telemetry/cohorts/LOCAL_CODEX_CAPACITY_ARCH1_2_V1.qualification.json` and `LOCAL_CODEX_CAPACITY_ARCH1_2_V1.json`; no rejected entries in qualified arrays. No current account ID backfill; CLI version != provider-client-policy version; missing != NOT_EXPOSED.

Canonical method NON_NEGATIVE_ZERO_INTERCEPT_FEATURE_CALIBRATION: cached, uncached, nonreasoning output, reasoning; separate real provider windows; conservative upper=max(point+1pp+2maxresidual,point×1.25,largerrequiredmargin); binding lowest floored conservative lower; CALIBRATED_ESTIMATE only, no billing inference. Productionmodule/tests implement same Owner method; no providerIO/authority/lifecycle sideeffects.

Main work BLOCKED / QUALIFIED_CAPACITY_REQUIRED. Campaign CAPACITY_QUALIFICATION_CAMPAIGN_V1 prepared: at most3usefulLOW_RISK_MANUAL_READ_ONLY probes, minimumonly; allrules/WO/authorityidentities precompiled, no executionIDs. Existing ALLOW_WITH_WATCH is applicable to an otherwise fullyeligible exactauthorized lowriskmanual probe, not a waiver for mainHIGH work. Current campaign preflight blocker PROVIDER_CLIENT_POLICY_IDENTITY_UNRESOLVED. Probe count used0; campaign NOT_EXHAUSTED. Do not invoke a probe with known missing required identity merely to manufacture sample count. WO-specific typed CapacityEstimate is PROVISIONAL_ESTIMATE with NULL bounds, no fabricated calibrated interval.

Only next action: mechanically establish explicit durable target provider-client-policy identity and fresh all8identity/runtime/provider/measurement-isolation/lifecycle gates before P01 manual handoff. No automatic CODEX invocation. After eachprobe intake/release/exacttokens/providerbinding/qualification, stop at3qualified perwindow; ifmax3used andinsufficient, CAPACITY_EVIDENCE_INSUFFICIENT. No additionalOwnerarchitecturediscussion or package design needed betweenprobes.

MANUAL active; CONTROLLED_AUTO DISABLED; IVF01Rev1 stale, Rev2 NOT_AUTHORIZED; AUTO-IMP-003–009 NOT_AUTHORIZED; runtime/broker/DB/migration/LIVE/production/credentials DENIED. OriginalDAG and002→003→004→005→006→007→008→009 operationallane unchanged. KNOWN_AUTOMATION_ARCHITECTURE_DEBT=NONE means allcalibration/orchestrationdesign and tests included, not implementationalreadyoperational. Current machine pointers supersede historicalcheckpoint text below.

## HISTORICAL CHECKPOINT — Program 1.2 / Orchestration Compilation

Architecture 1.2 remains ACTIVE with its accepted provider/cost/resume/lifecycle semantics unchanged. Current work, queue route and authority are canonical in `automation/work_orders/CURRENT_CODEX.yaml` and `docs/CURRENT_STATE.md`. Owner has DECIDED explicit Program V2 successor and CLOSE_AUTO_IMP_002_IVF01_FIRST; prior compatibility/sequencing discussion is resolved. Complete queue/event/route/dedupe/dispatch/promotion/forecast design is authoritative in `automation/governance/decisions/AUTO-GOV-PROGRAM-1_2-ORCHESTRATION.owner.json`. Program V2/controller remain implementation candidates pending one cohesive independent review and WORK acceptance.

Current work `WO-AUTO-GOV-PROGRAM-1_2-ORCH-01`: BLOCKED / QUALIFIED_CAPACITY_REQUIRED / WORK_CAPACITY_REVIEW; handoff_ready=false. Implementation authority is AUTHORIZED, not consumed; no writer/execution/reservation/dispatch. MANUAL is the active mode; CONTROLLED_AUTO DISABLED. IVF01 Rev1 stale, Rev2 preparation only NOT_AUTHORIZED; AUTO-IMP-003–009 NOT_AUTHORIZED; runtime/broker/DB/migration/LIVE/production DENIED. No automatic CODEX or next package. Design complete; qualified capacity evidence remains an external admission dependency, not a future architecture TODO.

## Historical checkpoints — no current route or execution authority

The following preserved checkpoint text is audit history. Its former unresolved Program discussion/current routing is superseded by the Owner decision and canonical CURRENT above. Historical quota text is evidence only; Architecture1.2 active policies are the admission authority.

### Historical Architecture 1.2 Accepted Materialization checkpoint

Architecture 1.2 = ACTIVE; Execution Capacity V2 = ACCEPTED_MATERIALIZED; V2 RF01 = CLOSED; V2-CAL-01 = CLOSED; V2-SER-01 = CLOSED; serializer warning assessment RESOLVED. Independent narrow PASS: `automation/work_orders/reviews/WO-AUTO-GOV-EXEC-CAPACITY-V2-RF01-01.verdict.json`; exact reviewed source integrated at `14ff081757fe4205ab78c85b82f7ef6ca9c1e76f`. Original candidate e414c108e075c8aa2307d607ffe77013b40c5391; RF01 implementation ffbf46f67740f5a314b2bcc6fd125dcbcfb23d9a; evidence606d8273cc7ead110547d3fa232b7c5e41c0e78e; effective source bundle f5a1fea9c2a8f4084348bbe6e8912d6020c9ea9ecfb80ac128eda33a5aaffa9d.

Authoritative active successor pointers are in `automation/governance/master_manifest.v1.yaml`: execution_capacity_policy.v2, authorization_lifecycle.v1_1, development_state_machine.v2, development_entry_protocol.v2, execution_cost_contract.v2, work_cost_accounting.v2 and negative_assertions.v2. Historical Architecture1.0/1.1 artifacts remain immutable, superseded for current admission; old80% remaining floor/40k fallback are not active operational authority. Provider denial remains authoritative. Activation does not grant CODEX execution or automatic dispatch/progression.

CODEX = NOT_RUNNING / NONE_AUTHORIZED_BY_THIS_MATERIALIZATION; handoff_ready=false; no writer held; no new authorization/execution/reservation/dispatch. Runtime/broker/DB/migration/LIVE/production DENIED. AUTO-IMP-003 NOT_AUTHORIZED. IVF01 Rev1 AUTH-AUTO-IMP-002-IVF01-01 = ARCHITECTURE_BASELINE_CHANGED_RECOMPILE_REQUIRED; historical authority unchanged, not reusable as1.2authority. IVF01Rev2 NOT_CREATED / NOT_AUTHORIZED; no waiver.

Program AUTO-IMP-PROGRAM-V1 remains exact immutable reviewed1.1 binding. PROGRAM_V1_1_BINDING != AUTOMATIC_PROGRAM_1_2_REBIND. Compatibility/recompile is UNRESOLVED_OWNER_DECISION_REQUIRED; no existing exact accepted authority determines1.2rebind. Program DAG AUTO-IMP-003 depends_on AUTO-IMP-001 is preserved; no inferred new dependency on002, execution permission or queue reorder. Owner must decide1.1->1.2Program compatibility/recompile, close002/IVF01first vs separately authorized independent003planning, and orchestration/trigger/queue/auto-progression boundaries.

RF01 cost CRITICAL/FRESH_CONTEXT_GROWTH is non-blocking forecast feedback: total2229994, uncached241023, actor328s, targeted3.29s, full13.36s. Future feedback TIGHTEN_POINTER_FIRST_CONTEXT, REMOVE_UNRELATED_HISTORY, RECALIBRATE_UNCACHED_INPUT_FORECAST. Metric variance does not authorize source correction or SPLIT_OVERSIZED_WORK_ORDER; preserve cohesive engineering value.

Only next route: `AUTOMATION_PROGRAM_1_1_TO_1_2_COMPATIBILITY_AND_NEXT_FLOW_SEQUENCING_DISCUSSION`. STOP; no next package.

<!-- HISTORICAL_1_0_1_1_OPERATING_MODEL_BEGIN; immutable prior prose retained, superseded for current architecture authority -->
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


### W1 Authorization Candidate RF01 Rebind

```text
OLD_W1_WAVE_CANDIDATE = AUTH-AUTO-IMP-W1-01
OLD_DISPOSITION = SUPERSEDED_CANDIDATE_NON_AUTHORITY
CURRENT_PACKAGE = AUTO-IMP-001
CURRENT_AUTHORIZATION_CANDIDATE = AUTH-AUTO-IMP-001-01
CURRENT_AUTHORIZATION_STATE = NOT_AUTHORIZED
PLANNING_BASELINE = e96876de83da3282fb2a5a63b76b9d73c14937ad
NEXT_ROUTE = AUTOMATION_IMPLEMENTATION_AUTO_IMP_001_AUTHORIZATION_DECISION
```

The W1 wave candidate was not transitioned to AUTHORIZED because its Program hash no longer matched the current Program artifact after review materialization and it did not expose the frozen package-level exact-binding field set. The replacement candidate binds one work package exactly and keeps automatic progression denied.


### AUTO-IMP-001 Explicit Authorization Decision

```text
AUTHORIZATION_ID = AUTH-AUTO-IMP-001-01
WORK_PACKAGE_ID = AUTO-IMP-001
DECISION = APPROVE
AUTHORIZATION_STATE = AUTHORIZED
EXECUTOR_PROFILE = CODEX_SINGLE_EXECUTOR_MANUAL_TRIGGER_ONLY
AUTOMATIC_DISPATCH = DENIED
AUTOMATIC_NEXT_PACKAGE_PROGRESSION = DENIED
EXECUTION_ELIGIBILITY = NOT_RESOLVED
NEXT_ROUTE = AUTOMATION_IMPLEMENTATION_AUTO_IMP_001_EXECUTION_ELIGIBILITY
```

Authorization uses package-level exact binding as canonical execution authority. The Program full-file hash is planning provenance only because the trailing `authorization_compilation` routing section changes as governance progresses; authorization validates the immutable Program semantic core plus exact package binding instead of recursively binding mutable routing metadata.

`AUTHORIZED != EXECUTABLE`.

### Deferred Skill Integration

```text
STATUS = DEFERRED_PLANNING_ONLY
CANDIDATE = AUTO-IMP-SKILL-001
TARGET = AUTOMATION_SKILL_ADAPTER_LAYER
ACTIVATE_ONLY_AFTER = FOUNDATION_STABILITY
```

Future Skills are execution playbooks below the Automation Control Plane, not authority owners. Canonical governance remains in repository policies/state. Skills may read authority and execute permitted workflows, but MUST NOT grant authorization, mutate quota/authorization policy, infer Runtime Authorization, expand write scope, or auto-advance packages.


### Provider-Native Quota Compatibility RF

```text
RF_ID = AUTO-IMP-001-QRF01
ISSUE = PROVIDER_QUOTA_UNIT_MISMATCH
ACTIVE_QUOTA_POLICY = 1.1 FROZEN
CANDIDATE_QUOTA_POLICY = 1.1-candidate / ACCEPTED_SOURCE_EVIDENCE / INACTIVE
AUTO-IMP-001_AUTHORIZATION = AUTHORIZED
EXECUTION_ELIGIBILITY = NOT_RESOLVED_FRESH_RECHECK_REQUIRED
NEXT_ROUTE = AUTOMATION_IMPLEMENTATION_AUTO_IMP_001_EXECUTION_ELIGIBILITY
```

OpenAI's ChatGPT Work/Codex plan allowance is provider-native usage allowance and does not define a fixed token equivalence. API token usage and API billing are separate evidence channels. Therefore the control plane must not convert plan percentage remaining into tokens.

The candidate preserves P50/P75/P90 token forecasts as task-complexity and telemetry forecasts, while adding a conservative provider-percentage bootstrap path for LOW-risk, manual-trigger-only, no-external-side-effect packages. The proposed percentage thresholds are internal governance values and require independent review before activation.


### QRF01 Bounded Review Fix

```text
REVIEW_RESULT = REVIEW_FIX_REQUIRED
MASTER_ARCHITECTURE_CONTRADICTION = NO
ARCHITECTURE_ESCALATION = NO
FIX_01 = RESERVE_ARITHMETIC_SINGLE_80_PERCENT_FLOOR
FIX_02 = APPLICABLE_WINDOW_POSITIVE_FAIL_CLOSED
FIX_03 = RESERVATION_BOUND_FRESHNESS
CANDIDATE_ACTIVE = false
AUTO_IMP_001_AUTHORIZATION = AUTHORIZED
AUTO_IMP_001_EXECUTABLE = false
```

The normalized fallback now uses one 80% remaining floor with no second reserve subtraction; resolves window applicability explicitly and fail-closed; and binds freshness to the current eligibility/reservation attempt, with 10 minutes only as an outer TTL.


### QuotaAdmissionPolicy v1.1 Materialization

```text
QRF01_RE_REVIEW = PASS
SOURCE_REVIEW_HEAD = 54a316cf816b8f1bb57da5b778d2a7e43ce92748
ACTIVE_QUOTA_POLICY = 1.1 FROZEN
PREVIOUS_QUOTA_POLICY = 1.0 FROZEN_SUPERSEDED_READ_ONLY
AUTO_IMP_001_AUTHORIZATION = AUTHORIZED
EXECUTION_ELIGIBILITY = NOT_RESOLVED_FRESH_RECHECK_REQUIRED
CODEX_EXECUTION = NOT_STARTED
NEXT_ROUTE = AUTOMATION_IMPLEMENTATION_AUTO_IMP_001_EXECUTION_ELIGIBILITY
```

The reviewed v1.1 provider-native quota semantics are now materialized as the canonical active policy. The original v1.0 bytes and the reviewed v1.1 candidate remain immutable historical/source evidence. Policy activation does not itself make AUTO-IMP-001 executable; a new reservation-bound quota snapshot and full single-use eligibility/reservation sequence are still required.

<!-- AUTOMATION_MASTER_V1_1_END -->

<!-- HISTORICAL_1_0_1_1_OPERATING_MODEL_END -->



## Development Automation Master 1.2 — ACTIVE / ACCEPTED_MATERIALIZED

Architecture1.2 ACTIVE on authoritative master after accepted independent narrow PASS and WORK materialization. Architecture1.1 is historical/superseded. V2 policy/spec pointers and deterministic evaluator are reviewed accepted successor semantics. CODEX grants no activation/acceptance authority. Historical1.1 policy sections remain immutable source evidence; their admission floor/fallback is superseded, never retroactively rewritten.


## Execution Capacity / Resume V2 — ACTIVE procedure

Successor policy pointers (ACTIVE after accepted independent review and WORK activation):
- automation/policies/execution_capacity_policy.v2.yaml
- automation/policies/authorization_lifecycle.v1_1.yaml
- automation/policies/development_state_machine.v2.yaml
- automation/policies/development_entry_protocol.v2.yaml
- automation/telemetry/execution_cost_contract.v2.yaml
- automation/specs/work_cost_accounting.v2.yaml
- automation/specs/negative_assertions.v2.yaml

Active master architecture is1.2 after reviewed materialization; presence of these files grants no execution authority. V2 evaluation surface: automation.engine.execution_capacity. Control plane assembles exact fresh evidence; evaluator performs no IO/invocation or authority mutation.

EXECUTION_COST_GATE != PROVIDER_AVAILABILITY_GATE. Per-WO P50/P75/P90 demand is primary; legacy static package forecasts are historical planning inputs. V2 has no fixed remaining-percent floor or normalized token fallback. Preserve cached/uncached/input/output/reasoning features. Exact task-bound local usage remains EXACT actual usage, not billing. Provider percentages are immutable shared-account proxy and may inform qualified capacity calibration. Derived capacity/token values are PROVISIONAL_ESTIMATE or CALIBRATED_ESTIMATE, never EXACT; no unsupported constant linear conversion or identical feature weights. Require minimum comparable samples plus identity, attribution, reset and uncertainty qualification; count alone never upgrades confidence.

Actual provider denial wins. Running denial checkpoints SAME execution as PAUSED_PROVIDER_LIMIT with WO/authorization/reservation/dispatch/branch/delta/budget/tests/telemetry/writer lineage. Pause is not source failure or correction-budget consumption. Recovery wakes only: RESUME_PENDING_REVALIDATION -> fresh head, scope, policy, authority, invocation, reservation, dispatch and writer/provider checks -> RESUME_SAME_EXECUTION or STOP_TO_WORK. Safe lock reacquisition needs verified ownership lineage and no competing owner. No new WO/execution/authorization/reservation/dispatch/budget for resume. CONSUMED redispatch remains DENIED; already-invoked same-execution continuation is distinct.

HISTORICAL_PHASE_SNAPSHOT != CURRENT_LIFECYCLE_PROJECTION. Never reinterpret pre-reservation snapshot flags as current truth. Current projection must agree with all durable lifecycle fields; contradiction -> FAIL_CLOSED_RECONCILIATION_REQUIRED; no event fabrication or historical rewriting.

Safety/governance -> unfinished resumable execution -> pending result/review/integration -> exact authorized new work. Unfinished execution blocks new dispatch. Every provider interruption triggers WORK_FORECAST_CAPACITY_REVIEW; this feedback grants no authority, does not block legal resume, and must be materialized before new work after interrupted completion. Review PASS != Integration PASS != materialized acceptance. IVF01 Rev1 stays BLOCKED_NO_EXECUTION_NO_WAIVER; after reviewed Architecture1.2 activation its projection is ARCHITECTURE_BASELINE_CHANGED_RECOMPILE_REQUIRED; never rewrite/reuse Rev1. AUTO-IMP-003 remains NOT_AUTHORIZED. All runtime/broker/DB/migration/LIVE/production effects DENIED.
