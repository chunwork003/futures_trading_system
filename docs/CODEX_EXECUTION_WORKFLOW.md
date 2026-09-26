# CODEX Execution Workflow

## 1. Purpose

本文件是 repository-native CODEX execution workflow 的唯一 detailed owner。

目標：

在不降低 architecture、authority、safety、test、Git 與 audit 約束的前提下，提高：

    accepted engineering progress
    /
    CODEX context + execution consumption

本文件不建立新的產品或 runtime authority。

Canonical CURRENT authority 仍為：

`docs/CURRENT_STATE.md`

Agent re-entry / routing surface：

`AGENTS.md`

Work Package / authorization schema owner：

`docs/work/WORK_PACKAGE_TEMPLATE.md`

---

## 2. Authority Model

執行順序固定：

    canonical CURRENT authority
        ->
    exact Work Package / Wave authorization
        ->
    exact Planning Baseline
        ->
    current Working HEAD
        ->
    bounded execution

若 handoff、prompt、舊文件或 cached context 與 canonical repository authority 衝突：

canonical repository authority wins。

任何 planning approval：

不得自動推導 Runtime Authorization。

任何 source modification authorization：

不得自動推導 runtime activation / operation authority。

核心 invariant：

    Runtime Source Modification Authorization
    !=
    Runtime Authorization
    !=
    Production Activation

---

## 3. Execution Unit

允許兩種 bounded engineering unit：

1. one explicitly authorized engineering leaf。
2. one explicitly authorized coherent DAG bundle / Wave。

Wave 只能包含 authorization 明確列出的 leaves。

禁止執行期間：

- dynamic leaf insertion。
- silent leaf removal。
- unauthorized reorder。
- scope expansion。
- architecture redesign。
- side-effect escalation。

Leaf-local completion：

不等於 Reviewer final acceptance。

---

## 4. Authority Preflight

任何 CODEX engineering execution 前必須確認：

1. branch。
2. exact Planning Baseline。
3. current Working HEAD。
4. origin / remote expected ancestry。
5. working tree state。
6. known allowed untracked files。
7. exact Authorized Leaves。
8. Runtime Source Modification Authorization。
9. canonical Runtime Authorization。
10. side-effect envelope。
11. read scope。
12. write scope。
13. protected scope。
14. rewrite policy。
15. required tests。
16. Git policy。
17. correction / retry policy。
18. STOP conditions。

任一 mandatory authority 缺失：

STOP。

---

## 5. Minimum Sufficient Context

CODEX 不以「讀越多越安全」為預設。

目標是：

Minimum Sufficient Context。

只取得足以正確完成目前 authorization 的證據。

Context 擴張必須由 evidence need 驅動。

禁止沒有明確原因的：

- whole-repo rescan。
- whole-docs rescan。
- repeated full-file reread。
- unrelated history traversal。

---

## 6. Search Before Read

預設流程：

    filename search
    -> symbol / reference search
    -> relevant tests
    -> bounded source regions
    -> implementation evidence

先搜尋，再讀檔。

優先使用：

- exact filename。
- symbol。
- import / reference。
- test name。
- error message。
- migration/table identifier。
- contract/ADR identifier。

只有 search evidence 證明需要時才擴大閱讀。

---

## 7. Read On Demand

第一次讀取：

只讀與 current leaf / failure / contract 直接相關區域。

若資料不足：

逐層擴張。

不得因「可能有用」一次載入大量 repo context。

---

## 8. Revision-Bound Context

所有 working context 必須綁定：

- Planning Baseline。
- current Working HEAD。

任何 commit 後：

    refresh Working HEAD
    -> invalidate changed READ_SET
    -> preserve unaffected shared context
    -> resolve next leaf delta

外部 unexpected revision：

不得沿用舊 context 繼續修改。

---

## 9. Transient Task Context Packet

Task Context Packet 是 working-memory compression，不是新 authority。

必須是：

- transient。
- derived。
- revision-bound。
- non-authoritative。
- non-persistent by default。

建議內容：

    AUTHORITY
    BASELINE
    CURRENT HEAD
    AUTHORIZED LEAF / WAVE
    FROZEN ASSERTIONS
    READ SET
    WRITE SET
    PROTECTED SET
    SIDE-EFFECT ENVELOPE
    TEST SET
    STOP CONDITIONS
    CURRENT EVIDENCE

優先保存 pointer：

- file path。
- symbol。
- test。
- ADR / blueprint ID。
- exact commit。

避免複製大量 canonical prose。

---

## 10. Wave Shared Context + Leaf Delta Context

Wave 不應每個 leaf 重新載入全部 authority。

使用：

    Wave Shared Context
    +
    Leaf Delta Context

### Wave Shared Context

只在 Wave 起點或 authority 變更時重新 resolve：

- Planning Baseline。
- exact Wave authorization。
- frozen architecture assertions。
- Wave DAG。
- side-effect envelope。
- protected surfaces。
- Git policy。
- global STOP barriers。

### Leaf Delta Context

每 leaf 只更新：

- current Working HEAD。
- leaf-specific contract。
- changed READ_SET。
- affected symbols。
- relevant tests。
- new evidence。
- local acceptance criteria。
- local correction count。

---

## 11. Side-Effect Envelope

Work Package / Wave 必須明確寫出允許與禁止的 side effects。

至少區分：

- source modification。
- test execution。
- DB environment access。
- migration creation。
- migration execution。
- broker network access。
- paper broker I/O。
- production broker I/O。
- credential access。
- production activation。

未列為 ALLOW：

預設 DENY。

source modification authority：

不得推導其他 side-effect authority。

---

## 12. Exact Read / Write / Protected Scope

Work Package 優先定義 exact files / symbols。

若 precheck 前無法 exact：

只能指定最小必要 directory / surface，且需附 reason。

Execution 中若證明必須修改 protected / unauthorized scope：

STOP。

不得 silent widen。

Read scope 可以 evidence-driven 擴張。

Write scope 不可自行擴張。

---

## 13. Bounded Rewrite

`patch small`

定義為：

smallest coherent delta satisfying the frozen contract。

不是：

fewest changed LOC at all costs。

Leaf rewrite policy 可使用：

- PREFERRED。
- ALLOWED。
- EXTEND。
- SMALL_FIX。
- NEW_PRIMITIVE。

若 rewrite policy 為 PREFERRED / ALLOWED：

可進行 bounded internal rewrite。

但必須保持：

- frozen external contract。
- authorized scope。
- compatibility contract。
- persistence authority。
- test semantics。

rewrite allowed：

不等於 redesign allowed。

---

## 14. Implementation Loop

每 leaf 預設：

    authority preflight
    -> search
    -> minimum read
    -> plan coherent delta
    -> implement
    -> early diff
    -> targeted tests
    -> failure-only diagnostics
    -> compatibility / integration tests
    -> full regression when required
    -> git diff --check
    -> scope validation
    -> completion evidence
    -> commit
    -> refresh HEAD

Early diff 必須檢查：

- unexpected files。
- unintended public API change。
- schema drift。
- migration/history mutation。
- accidental generated data。
- unrelated formatting churn。

---

## 15. Test Escalation

測試順序由 Work Package 明確定義。

一般順序：

    direct targeted
    -> nearby compatibility
    -> relevant integration
    -> full regression

Failure 發生時：

先讀 failing evidence。

不得立即 whole-repo scan。

不得用修改測試來掩蓋 frozen contract failure。

---

## 16. Failure Classification

所有 failure 必須分類。

### A. TOOLING RETRY

例如：

- shell quoting。
- PowerShell syntax。
- path separator。
- grep/search syntax。
- patch anchor movement。
- local transient tool issue。

不消耗 semantic correction budget。

但：

    non-semantic retry
    !=
    unbounded retry

同類 failure 重複發生：

必須 root-cause inspection。

仍無法解決時重新分類或 STOP。

### B. IMPLEMENTATION CORRECTION

例如：

- wrong code。
- failed contract assertion。
- compatibility regression。
- in-scope implementation bug。

消耗 semantic correction budget。

若 Work Package 未指定其他值：

沿用 repository current rule：

每 failing test / bounded implementation issue 最多兩個 scope-internal semantic correction cycles。

超過：

STOP / REVIEW。

### C. EXTERNAL / ENVIRONMENT FAILURE

例如：

- unavailable DB environment。
- broker sandbox failure。
- network/service unavailable。
- external credential channel unavailable。

不得因 external failure 盲改 runtime。

依 authorization：

VERIFY / DEFER / STOP。

### D. AUTHORITY / REVISION CONTRADICTION

例如：

- canonical authority conflict。
- unauthorized file required。
- frozen contract ambiguity。
- external HEAD divergence。
- side-effect class expansion。
- protected migration/history required。

STOP。

---

## 17. Leaf-Local Completion Gate

Wave 內只有 leaf-local completion 全部成立才可自動前進。

至少要求：

- exact scope PASS。
- implementation acceptance PASS。
- required negative assertions PASS。
- targeted tests PASS。
- required compatibility/integration PASS。
- required regression PASS。
- `git diff --check` PASS。
- semantic correction budget未超限。
- no unresolved authority contradiction。
- leaf commit complete。
- Working HEAD refreshed。
- next dependency still valid。

Leaf-local completion：

不得描述為 Reviewer final acceptance。

---

## 18. Automatic Wave Progression

Wave 可自動前進只有在：

- remaining leaves 已預先 explicit authorized。
- dependency satisfied。
- canonical authority unchanged。
- side-effect envelope unchanged。
- write/protected scope compatible。
- completion criteria objective。
- no human business/architecture decision required。
- no reviewer barrier triggered。

否則：

STOP。

---

## 19. Git Policy

Work Package / Wave 必須明確定義：

    git_commit
    git_push
    force_push

推薦第一個 runtime Wave candidate：

    git_commit:
        ALLOW
        per_leaf

    git_push:
        ALLOW
        wave_end

長期 invariant：

    force_push:
        DENY by default

禁止：

- amend historical public commit。
- reset --hard as normal workflow。
- arbitrary rebase through unknown remote work。
- unrelated remote merge。
- force push。

Wave-end push 前：

確認 expected remote ancestry。

若：

- non-fast-forward。
- unexpected remote commit。
- remote ancestry differs。

分類：

REVISION / EXTERNAL DIVERGENCE。

STOP / re-resolve。

---

## 20. Reviewer / Reauthorization Barrier

Reviewer 不需每 leaf 固定介入。

Reviewer barrier 改為 exception-driven。

中途必須 STOP / reauthorize：

- canonical semantics changed。
- next-leaf assumption invalid。
- new leaf required。
- write scope expansion required。
- side-effect expansion required。
- unauthorized migration execution required。
- unauthorized broker/network I/O required。
- credential/security boundary changed。
- semantic correction budget exceeded。
- architecture/business ambiguity。
- unexpected external revision divergence。
- protected history must change。

Wave final acceptance：

仍由後續 governance/reviewer checkpoint 決定。

---

## 21. Wave Final Evidence

Wave 結束至少回報：

- Planning Baseline。
- initial HEAD。
- final HEAD。
- executed leaves。
- per-leaf commits。
- skipped/deferred leaves。
- files changed。
- tests。
- integration verification。
- full regression。
- correction cycles。
- tooling retries。
- external failures。
- authority/revision stops。
- Git push result。
- remote ancestry result。
- new GAPs。
- unresolved reviewer items。
- accepted engineering weight candidate。
- CODEX efficiency evidence when available。

---

## 22. CODEX Efficiency Evidence

若平台可取得，紀錄：

- CODEX / model consumption %。
- accepted engineering weight。
- accepted leaves。
- accepted weight per 1% consumption。
- files read。
- files changed。
- tool operations。
- tooling retries。
- semantic correction cycles。
- human intervention count。
- targeted tests。
- compatibility tests。
- integration tests。
- full regression。
- scope violation count。
- stale-context incidents。
- elapsed time。

核心效率觀察：

    accepted engineering weight
    /
    model consumption %

此 metric 是觀察值。

禁止把固定 consumption % 當工程 quota。

---

## 23. Single-Agent Default

預設：

    one CODEX executor
    + repository search
    + shell
    + Git
    + tests

不預設建立：

- Planner agent。
- Researcher agent。
- Reviewer agent。
- Tester agent。
- multi-agent orchestrator。

只有 evidence 證明 single-agent 成為 blocker 才另開治理決策。

---

## 24. Explicit V0 Exclusions

V0 不建立：

- RAG service。
- Vector DB。
- workflow database。
- Redis execution cache。
- persistent Task Context Packet store。
- packet generator subsystem。
- custom agent orchestration platform。

優先使用 native repository primitives。

---

## 25. Current Candidate Wave Plan

狀態：

`DEPENDENCY-COHERENT CANDIDATE WAVE PLAN`

Dependency DAG：

VERIFIED。

Execution Coherence：

TO BE VERIFIED DURING EXACT WAVE AUTHORIZATION。

Execution Authorization：

NOT_AUTHORIZED。

### W1 — Account Authority

    C02 -> C04 -> C21 -> C03

weight 19。

### W2 — Execution Safety

    C08 -> C05 -> C06

weight 14。

### W3 — Broker Recovery

    C07 -> C09 -> C10

weight 15。

### W4 — Recovery Authority

    C13 -> C12 -> C14 -> C15

weight 18。

### W5 — Strategy Readiness

Architecture dependency：

    C16 -> C17
    C16 -> C19

    C20
    # sibling / independent dependency path

    C15 + C16 + C17 + C19 + C20 + C25
        -> C18

C19 / C20：

sibling semantics。

Single-agent serialization：

可以 deterministic serialize。

但 serialization order 不得升格成 architecture dependency。

---

## 26. Exact Wave Authorization Requirements

Dependency coherence alone：

不足以執行。

正式 Wave authorization 必須另外驗證：

- exact leaf set。
- exact file/symbol scope。
- side-effect envelope compatibility。
- rewrite policy compatibility。
- protected history compatibility。
- acceptance criteria compatibility。
- test compatibility。
- human decision barriers。
- correction/retry policy。
- Git commit policy。
- Git push policy。
- remote divergence guard。
- reviewer/reauthorization barrier。
- STOP conditions。

完成後才可考慮：

`Runtime Source Modification Authorization`。

---

## 27. STOP Conditions

立即停止受影響 work unit：

- missing canonical authority。
- baseline mismatch。
- external revision divergence。
- unexpected dirty tree。
- unauthorized write required。
- protected file/history required。
- architecture semantics missing。
- business semantics ambiguous。
- broker/live-money ambiguity。
- migration execution not authorized。
- DB/broker side effect not authorized。
- credential/security issue。
- semantic correction budget exceeded。
- current leaf invalidates future Wave dependency。
- same-class tooling retry remains unresolved after root-cause inspection。
- unrelated core regression。

STOP：

不代表整個 project blocked。

只阻止受影響的 authorization unit。

---

## 28. Minimal CODEX Handoff

理想 runtime handoff 只需提供：

1. exact authorization file。
2. exact Planning Baseline。
3. authorized Wave / leaf IDs。
4. pointers to frozen contract。
5. read/write/protected scope。
6. side-effect envelope。
7. tests。
8. Git policy。
9. STOP conditions。
10. this workflow pointer。

不應把完整歷史聊天重新塞入 CODEX context。

---

## 29. Current Governance Boundary

本文件本身：

不授權任何 runtime modification。

目前：

    Runtime Authorization:
        NOT_AUTHORIZED

    Runtime Source Modification Authorization:
        NOT_AUTHORIZED

    CODEX Wave execution:
        NOT_AUTHORIZED

下一個 runtime candidate：

C02。

C02：

NOT_AUTHORIZED。
