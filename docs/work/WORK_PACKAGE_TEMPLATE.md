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
- HEAD。
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

完成 current ACTIVE 後停止。

允許更新 queue。

不得自動開始下一個 mainline。
