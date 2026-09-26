# WORK PACKAGE TEMPLATE

## 1. Work Package ID

`<ID>`

---

## 2. Title

`<TITLE>`

---

## 3. Recommended Model

One of：

- GPT-5.6 Terra
- GPT-5.6 Sol
- explicit escalation

---

## 4. Execution Mode

One of：

- AUTO_ALLOWED
- REVIEW_REQUIRED
- LEVEL_3A_BOUNDED
- HUMAN_ONLY

---

## 5. Goal

清楚描述此次要完成的 capability。

不得只寫：

`refactor X`

必須能說明：

完成後系統新增或修正什麼能力。

---

## 6. Why This Is Next

說明：

- current mainline。
- dependency。
- previous completed gate。
- why side issues are not taking priority。

---

## 7. Baseline

至少包含：

- branch。
- required architecture/runtime ancestor。
- actual execution HEAD 由 precheck 取得，不用文件自我參照。
- regression。
- known warnings。
- known untracked files。
- expected working tree。

---

## 8. Dependencies

列出：

- architecture dependency。
- runtime dependency。
- previous GAP。
- pending blocker。

---

## 9. Confirmed Architecture Decisions

只放此次真正相關：

- ownership。
- invariants。
- data authority。
- expected vs actual。
- business semantics。
- broker semantics。

---

## 9A. Architect Design Freeze Gate

Work Package 在變成 `READY_FOR_EXECUTION` 前，人工 architect 必須先固定與此次 capability 有關的：

- canonical ownership。
- public model / contract。
- stable identity / key。
- expected vs actual boundary。
- state semantics。
- dependency direction。
- port / I/O boundary。
- time / timezone semantics。
- numeric / precision semantics。
- error / ambiguity behavior。
- broker mapping semantics。
- persistence authority（若適用）。
- compatibility / migration boundary。
- package placement rule。
- acceptance / test semantics。

Codex 可以自行決定：

- private helper。
- local function decomposition。
- fixture organization。
- non-public implementation detail。

Codex 不得自行決定新的：

- business semantics。
- broker semantics。
- canonical ownership。
- public API contract。
- persistence authority。
- security / live-money behavior。

任何未被 Design Freeze 覆蓋、且會影響上述 public semantics 的問題：

`HARD_BLOCK` 或 `REVIEW_AT_CHECKPOINT`。

---

## 9B. Blueprint Scope

Blueprint baseline 啟用後必填：

    Implements:
        <Blueprint IDs>

    Touches:
        <Blueprint IDs>

    Does Not Implement:
        <Blueprint IDs / groups>

不得只寫模糊 module name。

---

## 9C. Source Requirements

若 Work Package 涉及：

- broker。
- exchange。
- external API。
- framework version semantics。
- persistence engine semantics。

必填：

    Source IDs:
    Last Verified:
    Revalidation Required:
    Change Risk:

Source IDs：

使用：

`docs/blueprint/SOURCE_REGISTRY.md`

未有 source：

先人工 verify 並登錄 registry。

不得由 runtime executor 靠未審核二手來源決定 public semantics。

---

## 10. Scope Freeze

明確寫：

此次做什麼。

此次不做什麼。

---

## 11. Allowed Files / Areas

盡量 exact。

若 precheck 前無法知道 exact files：

指定最小 directory + reason。

---

## 12. Forbidden Files / Areas

至少考慮：

- `data/`
- unrelated strategy
- database
- broker live action
- secrets
- unrelated docs

---

## 13. Implementation Requirements

逐項可驗收。

避免：

- improve architecture。
- clean up。
- refactor as needed。

這類無邊界描述。

---

## 13A. Code Documentation Requirements

重要新 module / class / public function / public contract：

繁體中文 comment / docstring 至少描述適用項目：

- 用途。
- 責任。
- upstream / 資料來源。
- downstream / 使用者。
- important invariant。
- non-obvious business rule。
- Source ID。
- 明確不負責的事項。

禁止只做名稱翻譯式低價值註解。

---

## 14. Compatibility Requirements

列出：

- existing runtime behavior。
- legacy imports。
- current tests。
- schema compatibility。
- API compatibility。

---

## 15. Business / Domain Semantics

對：

- trading。
- broker。
- account。
- risk。
- reconciliation。

必須明確。

如不明確：

HARD_BLOCK。

---

## 16. Issue Classification

每個新問題分類：

Priority：

- P0。
- P1。
- P2。
- P3。
- OBS。

Handling：

- AUTO_FIX。
- RECORD_AND_CONTINUE。
- REVIEW_AT_CHECKPOINT。
- HARD_BLOCK。

非 blocker：

不得插隊。

---

## 17. Test Plan

至少：

- targeted tests。
- relevant integration tests。
- deterministic behavior。
- full regression。
- fake/mock external dependency。

---

## 18. Acceptance Criteria

必須可以明確回答：

PASS / FAIL。

---

## 19. Stop Conditions

明確列出：

哪些情況不可猜測。

---

## 20. Git Policy

固定：

    precheck
    → implementation
    → tests
    → git diff --check
    → scope validation
    → exact staging
    → commit
    → push
    → verify

禁止：

- amend historical commits。
- rebase existing public history。
- force push。
- reset --hard as normal workflow。

---

## 21. Documentation Updates

只更新真正受到此次 capability 影響的 current truth。

避免每包都重寫所有 docs。

---

## 22. Final Report

至少：

1. implementation summary。
2. actual runtime path。
3. files created。
4. files modified。
5. targeted tests。
6. integration tests。
7. full regression。
8. warnings。
9. git diff --check。
10. git status。
11. new LEVEL 2 items。
12. LEVEL 3 blockers。
13. commit SHA。
14. push result。
15. result / recommendation。

---

## 23. Next-Work Behavior

Level 3A：

完成 current ACTIVE runtime 後停止。

是否更新 docs / queue：

依 ACTIVE 的 responsibility split。

若 ACTIVE 指定人工 closure：

runtime executor 不更新下一個 ACTIVE，不開始下一個 mainline。

不得自動開始下一個 mainline。
---

## 24. Wave / Autonomous Execution Extension

若此次不是 single leaf，而是 authorized Wave，必填。

### 24A. Wave Identity

    Wave ID:
        <WAVE_ID>

    Wave Planning Baseline:
        <EXACT_SHA>

    Dependency Status:
        <VERIFIED / NOT_VERIFIED>

    Execution Coherence:
        <VERIFIED / NOT_VERIFIED>

不得把 dependency coherence 寫成完整 execution coherence。

---

## 25. Authorized Leaves

明確列出 exact leaves：

    Authorized Leaves:
        - <LEAF_1>
        - <LEAF_2>

禁止：

- dynamic leaf insertion。
- silent scope expansion。
- unauthorized next-leaf execution。

---

## 26. Authorization Separation

必填：

    Runtime Source Modification Authorization:
        <NOT_AUTHORIZED / BOUNDED_AUTHORIZED_FOR_WAVE_ID>

    Runtime Authorization:
        <CANONICAL CURRENT VALUE>

    Production Activation:
        <ALLOW / DENY>

核心：

    source modification authorization
    !=
    runtime activation / operation authorization

不得因 Wave 重新定義 canonical `Runtime Authorization`。

---

## 27. Side-Effect Envelope

至少列：

    Source Modification:
    Test Execution:
    DB Environment Access:
    Migration Creation:
    Migration Execution:
    Broker Network:
    Paper Broker I/O:
    Production Broker I/O:
    Credential Material:
    Production Activation:

未明列 ALLOW：

預設 DENY。

---

## 28. Context / Scope Contract

必填：

    Shared Authority Context:
        <pointers>

    Read Scope:
        <files / symbols / bounded areas>

    Write Scope:
        <exact files / symbols>

    Protected Scope:
        <exact files / areas>

    Task Context Packet:
        transient / derived / revision-bound / non-authoritative

Wave 使用：

    Wave Shared Context
    +
    Leaf Delta Context

Write scope 不得自行 evidence-expand。

需要擴大 write scope：

STOP / reauthorization。

---

## 29. Rewrite Policy

每 leaf 或 surface 指定：

    PREFERRED
    ALLOWED
    EXTEND
    SMALL_FIX
    NEW_PRIMITIVE

`patch small`：

smallest coherent delta satisfying contract。

不是：

minimum LOC at all costs。

Rewrite permission 不授權 architecture redesign。

---

## 30. Test / Correction / Retry Policy

明確列：

    Targeted Tests:
    Compatibility Tests:
    Integration Tests:
    Full Regression:

    Semantic Correction Budget:
        <VALUE / repository current rule>

Failures 分類：

    TOOLING RETRY
    IMPLEMENTATION CORRECTION
    EXTERNAL / ENVIRONMENT FAILURE
    AUTHORITY / REVISION CONTRADICTION

Tooling retry：

不計 semantic correction budget。

但不得 unbounded retry。

同類 tooling failure 重複：

root-cause inspection -> reclassify / STOP。

---

## 31. Wave Git Policy

必填：

    git_commit:
        <ALLOW / DENY>
        <per_leaf / wave_end / explicit>

    git_push:
        <ALLOW / DENY>
        <per_leaf / wave_end / explicit>

    force_push:
        DENY by default

若 remote divergence / non-fast-forward：

STOP。

禁止自動 force-push、未知 remote rebase、unrelated merge。

---

## 32. Reviewer / Reauthorization Barrier

自動前進僅限：

- remaining leaves pre-authorized。
- canonical authority unchanged。
- next dependency valid。
- side-effect envelope unchanged。
- tests PASS。
- semantic correction budget within limit。
- no new architecture/business decision。

以下立即 STOP：

- authority change。
- write scope expansion。
- side-effect expansion。
- new leaf required。
- migration/broker action not authorized。
- security/credential boundary change。
- correction budget exceeded。
- remote divergence。
- architecture/business ambiguity。

---

## 33. Wave Completion Evidence

至少：

1. Planning Baseline。
2. initial / final HEAD。
3. executed leaves。
4. per-leaf commits。
5. files read。
6. files changed。
7. tests。
8. tooling retries。
9. semantic corrections。
10. external failures。
11. reviewer barriers。
12. Git push / ancestry result。
13. accepted engineering weight candidate。
14. CODEX/model consumption if available。
15. accepted weight per 1% consumption if available。
16. elapsed time。
17. final STOP / next authorization state。
