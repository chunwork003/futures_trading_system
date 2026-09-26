# VIBE V0 / CODEX Workflow Materialization Authorization

## 1. Authorization Status

Authorization Type：

DOCS / WORKFLOW ONLY。

Authorization State：

BOUNDED_AUTHORIZED_VIBE_V0_DOCS_ONLY。

This authorization does NOT grant Runtime Authorization。

This authorization does NOT grant Runtime Source Modification Authorization。

This authorization does NOT authorize CODEX Wave runtime execution。

---

## 2. Authorization Baseline

Input Planning Baseline：

`2c035e998e0242ee9697037978eb642e58fce83b`

Branch：

`master`

Effective execution baseline：

the commit produced by this authorization checkpoint after commit / push。

P3 MUST begin only from that exact effective authorization baseline。

---

## 3. Goal

Materialize the already-reviewed VIBE V0 and Wave governance model into a minimal repository-native CODEX execution workflow。

Primary objective：

increase accepted engineering progress per CODEX/context consumption while preserving frozen authority、scope、safety and revision boundaries。

This task is governance/workflow materialization only。

It MUST NOT implement any GAP-08 runtime correction leaf。

---

## 4. Workflow Ownership Resolution

Repository inspection establishes：

`AGENTS.md`

remains：

short canonical re-entry / routing / guard surface。

`docs/work/WORK_PACKAGE_TEMPLATE.md`

remains：

bounded work-package and authorization schema owner。

`docs/DEVELOPMENT.md`

remains：

supplemental development command reference；it MUST NOT become the new CODEX governance authority。

One NEW detailed workflow owner is authorized：

`docs/CODEX_EXECUTION_WORKFLOW.md`

No second competing VIBE / CODEX / AI workflow document may be created。

---

## 5. Authorized Existing Files

P3 MAY modify exactly these existing governance/workflow files when required：

- `AGENTS.md`
- `docs/work/WORK_PACKAGE_TEMPLATE.md`
- `docs/CURRENT_STATE.md`
- `docs/CURRENT_WORK.md`
- `docs/GAP_REGISTER.md`
- `docs/DEVELOPMENT_LOG.md`
- `docs/work/ACTIVE.md`

---

## 6. Authorized New File

P3 MAY create exactly one new detailed workflow owner：

- `docs/CODEX_EXECUTION_WORKFLOW.md`

No other new workflow/governance document is authorized。

---

## 7. Explicitly Read-Only / Historical Surfaces

P3 MUST NOT modify：

- `docs/work/GAP08_C25_CLOSURE.md`
- `docs/work/GAP08_CORRECTION_FREEZE.md`
- architecture ADRs。
- runtime source。
- tests。
- migrations。
- broker adapters。
- database files。
- `data/`。
- secrets / credentials。
- historical accepted commits。

Supplemental `docs/DEVELOPMENT.md` remains read-only for this task。

---

## 8. VIBE V0 Core To Materialize

The detailed workflow owner MUST preserve these accepted VIBE V0 principles：

### V0-1 — Authority First

Resolve canonical authority and exact baseline before implementation work。

Canonical repository authority wins over stale handoff/context。

### V0-2 — Minimum Sufficient Context

Do not maximize context。

Acquire only the minimum evidence required to complete the authorized engineering unit correctly。

### V0-3 — Search Before Read

Use filename / symbol / reference / test search before broad file reads。

Whole-repository rescan is forbidden unless explicitly authorized by the active Work Package。

### V0-4 — Read On Demand

Read only relevant regions first。

Expand context only when evidence requires it。

### V0-5 — Revision-Bound Context

All working context is bound to an exact Planning Baseline / Working HEAD。

Changed evidence invalidates affected cached context。

### V0-6 — Transient Task Context Packet

Task Context Packet is：

- transient。
- derived。
- revision-bound。
- non-authoritative。
- non-persistent by default。

It MUST NOT become a second knowledge base or repository authority。

### V0-7 — Pointer Over Duplication

Prefer references to canonical files / symbols / tests instead of repeatedly embedding large prose blocks。

### V0-8 — Early Diff

After a meaningful patch：

inspect diff / scope early。

Do not wait until final regression to discover unrelated modifications。

### V0-9 — Failure-First Diagnostics

On failure：

expand only the evidence associated with the failure before reading unrelated repository areas。

### V0-10 — Evidence-Based Completion

Completion requires objective acceptance evidence：

scope、tests、diff、Git state、authorization boundary and required negative assertions。

### V0-11 — Single-Agent Default

Default execution model：

one CODEX agent + native search + shell + Git + tests。

Do NOT add planner/researcher/reviewer/tester multi-agent orchestration by default。

### V0-12 — No Premature VIBE Infrastructure

V0 MUST NOT build：

- Vector DB。
- RAG service。
- packet generator subsystem。
- Redis/cache workflow platform。
- separate agent orchestrator。
- workflow database。

Native repository/search/test/Git capability remains the default。

---

## 9. Wave Governance To Materialize

### W1 — Explicit Coherent Bundle

One explicitly authorized coherent DAG bundle MAY contain multiple enumerated engineering leaves。

Automatic progression is allowed only inside the exact authorized bundle。

Leaf-local completion does NOT equal Reviewer acceptance。

### W2 — Preserve Canonical Runtime Authorization Semantics

Existing canonical：

`Runtime Authorization`

MUST NOT be redefined by Wave governance。

Source-modification permission is orthogonal。

Future exact Wave packages MAY use：

`Runtime Source Modification Authorization`

Example：

    Runtime Source Modification Authorization:
        BOUNDED_AUTHORIZED_FOR_WAVE_<ID>

    Authorized Leaves:
        <exact leaves>

Canonical invariant：

    source modification authorization
    !=
    runtime activation / operation authorization

### W3 — Fixed Planning Baseline + Advancing Working HEAD

Wave Planning Baseline：

fixed。

Working HEAD：

may advance only through expected authorized leaf commits。

After each leaf commit：

    refresh HEAD
    -> invalidate changed READ_SET
    -> verify expected clean state
    -> verify next dependency
    -> continue

Unexpected external revision change requires STOP / re-resolution。

### W4 — Four Failure Classes

Failures MUST be classified as：

A. TOOLING RETRY

B. IMPLEMENTATION CORRECTION

C. EXTERNAL / ENVIRONMENT FAILURE

D. AUTHORITY / REVISION CONTRADICTION

Tooling retry does NOT consume semantic correction budget。

Implementation correction DOES consume semantic correction budget。

Authority/revision contradiction requires STOP。

### W5 — Bounded Rewrite

`patch small`

means：

smallest coherent delta satisfying the frozen contract。

It does NOT mean：

fewest changed LOC at all costs。

Leaf rewrite metadata such as PREFERRED / ALLOWED / EXTEND / SMALL_FIX / NEW_PRIMITIVE must be respected。

Rewrite permission never grants architecture redesign permission。

### W6 — Context Amortization

Use：

    Wave Shared Context
    +
    Leaf Delta Context

Do not reread full authority/context for every leaf。

Wave shared context includes：

- Planning Baseline。
- exact Wave authorization。
- shared frozen assertions。
- DAG。
- side-effect envelope。
- protected surfaces。

Leaf delta includes：

- current Working HEAD。
- changed READ_SET。
- leaf contract。
- symbols。
- relevant tests。
- new evidence。

### W7 — Git Policy

Wave package must explicitly define：

    git_commit
    git_push
    force_push

First Wave candidate policy may be：

    git_commit:
        ALLOW
        per_leaf

    git_push:
        ALLOW
        wave_end

Long-term invariant：

    force_push:
        DENY by default

Wave-end non-fast-forward or unexpected remote divergence：

STOP。

CODEX MUST NOT automatically：

- force push。
- arbitrary rebase through unknown remote changes。
- merge unrelated remote work。

### W8 — Candidate Wave Status Precision

Current W1-W5 planning status is only：

`DEPENDENCY-COHERENT CANDIDATE WAVE PLAN`

Dependency DAG：

VERIFIED。

Execution Coherence：

TO BE VERIFIED DURING EXACT WAVE AUTHORIZATION。

Execution Authorization：

NOT_AUTHORIZED。

Do NOT describe current candidates as fully validated Wave plans。

Execution coherence must later verify：

- exact file/symbol write scope。
- side-effect envelope compatibility。
- rewrite-policy compatibility。
- protected-history compatibility。
- acceptance/test compatibility。
- hidden human decision barriers。
- commit/push policy。
- STOP conditions。

C19 / C20 remain sibling semantics。

Single-agent serialization MUST NOT create a fake architecture dependency。

### W9 — Sequencing

GOV-01 already exists。

C25 closure updated the existing GOV-01 canonical projection。

The fixed sequencing is：

    C25 closure
    -> post-C25 CURRENT consistency
    -> bounded VIBE docs/workflow authorization
    -> VIBE/Wave materialization
    -> post-VIBE Planning Baseline
    -> exact Wave authorization
    -> explicit bounded source-modification authorization
    -> CODEX START

No stage implicitly authorizes the next。

### W10 — Reviewer / Reauthorization Barrier

Reviewer intervention becomes exception-driven rather than mandatory after every leaf。

Wave may continue automatically only while：

- all remaining leaves were explicitly pre-authorized。
- canonical authority is unchanged。
- side-effect class does not expand。
- completion criteria remain objective。
- commits remain clean and expected。
- required tests pass。
- no new architecture/business decision is required。

Intermediate STOP / reauthorization is mandatory when：

- canonical semantics change。
- next-leaf assumptions become invalid。
- a new leaf is required。
- write scope must expand。
- side-effect class must expand。
- migration execution becomes necessary but unauthorized。
- broker/network I/O becomes necessary but unauthorized。
- credential/security boundary changes。
- semantic correction budget is exceeded。
- architecture ambiguity appears。
- unexpected external revision divergence occurs。

---

## 10. Final Amendments A1-A4

### A1 — Runtime Authorization Terminology Guard

Preserve canonical `Runtime Authorization` meaning。

Use orthogonal `Runtime Source Modification Authorization` for bounded source modification。

Do not infer activation/operation authority from source modification authority。

### A2 — Candidate Wave Precision

W1-W5 are dependency-coherent candidates only。

Execution coherence remains unresolved until exact Wave authorization。

### A3 — Remote Divergence Guard

`force_push = DENY` by default。

Unexpected remote divergence requires STOP / re-resolution。

### A4 — Finite Tooling Retry

Non-semantic tooling retry does not consume semantic correction budget。

However：

    non-semantic retry
    !=
    unbounded retry

Repeated same-class tooling failure requires root-cause inspection and reclassification as appropriate：

- EXTERNAL / ENVIRONMENT FAILURE。
- AUTHORITY / REVISION CONTRADICTION。
- STOP。

No fixed retry count is frozen by this task unless existing repository governance already defines one。

---

## 11. Current Dependency-Coherent Candidate Waves

These groupings are planning inputs only。

They are NOT execution authorization。

### Candidate W1 — Account Authority

    C02
        -> C04
        -> C21
        -> C03

Weight：

19。

### Candidate W2 — Execution Safety

    C08
        -> C05
        -> C06

Weight：

14。

### Candidate W3 — Broker Recovery

    C07
        -> C09
        -> C10

Weight：

15。

### Candidate W4 — Recovery Authority

    C13
        -> C12
        -> C14
        -> C15

Weight：

18。

### Candidate W5 — Strategy Readiness

Architecture dependency semantics：

    C16
        -> C17

    C16
        -> C19

    C20
        # sibling / independently satisfied dependency path

    C15 + C16 + C17 + C19 + C20 + C25
        -> C18

For a single executor，C19 / C20 may be deterministically serialized for execution convenience only。

Serialization order MUST NOT become architecture dependency。

Weight：

20。

---

## 12. P3 Materialization Requirements

P3 MUST create one concise but complete detailed workflow owner：

`docs/CODEX_EXECUTION_WORKFLOW.md`

The workflow owner MUST cover at least：

1. authority preflight。
2. minimum sufficient context。
3. search-first / read-on-demand。
4. revision-bound transient task context。
5. shared Wave context + leaf delta。
6. side-effect envelope。
7. exact write scope。
8. bounded rewrite behavior。
9. early diff。
10. test escalation。
11. failure classification。
12. finite tooling retry。
13. semantic correction budget。
14. per-leaf completion evidence。
15. Git commit/push/remote-divergence guard。
16. reviewer/reauthorization barrier。
17. Wave final evidence。
18. STOP conditions。
19. CODEX efficiency evidence fields。
20. explicit exclusions / no premature VIBE infrastructure。

`AGENTS.md` MUST remain concise and route agents to the detailed owner rather than duplicate the full workflow。

`docs/work/WORK_PACKAGE_TEMPLATE.md` MUST be extended only as needed to express：

- Planning Baseline。
- Wave ID。
- Authorized Leaves。
- Runtime Source Modification Authorization。
- Runtime Authorization。
- side-effect envelope。
- exact read/write/protected scope。
- rewrite policy。
- test policy。
- Git policy。
- correction/retry policy。
- reviewer barrier。
- STOP conditions。

---

## 13. CODEX Efficiency Evidence

The workflow should support recording，when available：

- CODEX / model consumption percentage。
- accepted engineering weight。
- accepted leaves。
- accepted weight per 1% consumption。
- files read。
- files changed。
- tool operations。
- tooling retries。
- semantic correction cycles。
- human intervention count。
- targeted / compatibility / regression results。
- scope violations。
- stale-context incidents。
- elapsed time。

These metrics are observational evidence only。

No target percentage or productivity quota is frozen by P3。

---

## 14. P3 Acceptance Criteria

P3 passes only if：

1. exactly one detailed CODEX workflow owner exists。
2. AGENTS remains short routing/re-entry authority。
3. WORK_PACKAGE_TEMPLATE expresses Wave/source-modification authorization fields。
4. canonical Runtime Authorization terminology is preserved。
5. current candidate Waves are labeled dependency-coherent only。
6. no Wave runtime/source modification is authorized。
7. C02 remains NOT_AUTHORIZED。
8. force-push default DENY is explicit。
9. remote divergence STOP is explicit。
10. tooling retry is finite by classification，without inventing an unsupported fixed retry count。
11. Task Context Packet remains transient / derived / revision-bound / non-authoritative。
12. no RAG / Vector DB / packet generator / agent orchestrator is introduced。
13. no runtime/test/migration file changes。
14. `git diff --check` passes。
15. exact docs scope passes。
16. commit / push succeeds。
17. resulting commit becomes the post-VIBE Planning Baseline。
18. executor STOPS after P3；it MUST NOT build Wave-1 authorization in the same commit。

---

## 15. P3 Git Policy

P3：

docs-only single checkpoint。

Required：

    precheck
    -> bounded docs/workflow materialization
    -> early diff
    -> scope validation
    -> git diff --check
    -> exact staging
    -> commit
    -> push
    -> verify
    -> STOP

Runtime tests：

NOT REQUIRED because P3 is deterministic docs/workflow-only and runtime/test/migration bytes are protected。

Force push：

DENY。

Amend / reset-hard / history rewrite：

DENY。

---

## 16. P3 STOP Conditions

STOP immediately if：

- an existing detailed CODEX workflow owner is discovered that makes the new file duplicative。
- canonical authority conflicts with this authorization。
- Runtime Authorization semantics would need redefinition。
- runtime/test/migration modification appears necessary。
- C02 implementation appears necessary。
- Wave execution appears necessary。
- a second new workflow/governance document appears necessary。
- architecture/business semantics need to be reopened。
- unexpected remote divergence exists。
- authorized docs scope must expand beyond this package。

---

## 17. Explicit Non-Authorization

This package does NOT authorize：

- C02。
- C04。
- C21。
- C03。
- any other correction leaf。
- Wave-1 execution。
- Runtime Source Modification Authorization for any Wave。
- runtime activation。
- migration execution。
- V07。
- PostgreSQL environment access。
- broker network。
- paper broker I/O。
- production broker I/O。
- credential material exposure。
- live trading。
- RAG / Vector DB / packet generator implementation。

---

## 18. Next Stage After P3

After successful P3 commit / push：

1. establish post-VIBE Planning Baseline。
2. verify canonical CURRENT projection。
3. build exact Wave-1 authorization package。
4. verify W1 execution coherence：
   - file/symbol scope。
   - side effects。
   - rewrite policies。
   - protected surfaces。
   - tests。
   - Git policy。
   - STOP / reviewer barriers。
5. only then decide explicit `Runtime Source Modification Authorization`。
6. CODEX runtime execution remains prohibited until that later authorization。

---

## 19. Current Runtime State

Runtime Authorization：

NOT_AUTHORIZED。

Runtime Source Modification Authorization：

NOT_AUTHORIZED。

Next runtime candidate：

C02 — BrokerAccount Revision Head + Exact Checkpoint。

C02：

NOT_AUTHORIZED。

Correction core：

27 / 113 complete / verified。

Remaining：

86。

CODEX runtime execution：

NOT_STARTED / NOT_AUTHORIZED。
