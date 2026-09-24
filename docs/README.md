# Documentation Map

## Purpose

本文件定義 repository 文件的權威層級與責任。

不是所有文件都是 current source of truth。

---

## Authoritative Documents

| File | Responsibility |
|---|---|
| `../AGENTS.md` | Agent 執行規則、scope、issue 分級、Git/test policy |
| `work/ACTIVE.md` | 目前唯一完整 Work Package |
| `CURRENT_STATE.md` | 現在 HEAD、tests、milestone、能力狀態 |
| `CURRENT_WORK.md` | Mainline execution queue |
| `V1_CAPABILITY_MAP.md` | V1 完整功能清單與完成度 |
| `ARCHITECTURE.md` | 全系統 logical/package/dependency architecture |
| `ROADMAP.md` | V1 milestone sequence |
| `GAP_REGISTER.md` | 問題、technical gap、blocker、follow-up |
| `AI_HANDOFF.md` | 已確認 architecture/business decisions |
| `adr/ADR-001-TRADING-CORE-BOUNDARIES.md` | Trading core boundary ADR |

---

## Historical / Supplemental Documents

以下保留歷史與補充用途，但不是 current source of truth：

- `PROJECT_STATE.md`
- `DEVELOPMENT.md`
- `BACKTEST_ENGINE.md`
- `DATA_ARCHITECTURE.md`

若與 authoritative 文件衝突：

authoritative 文件優先。

---

## Responsibility Separation

### ARCHITECTURE.md

回答：

「整個系統有哪些 layer、subsystem、dependency、state boundary？」

### V1_CAPABILITY_MAP.md

回答：

「V1 到底有多少功能？哪些完成？哪些未完成？」

### ROADMAP.md

回答：

「主要 milestone 的完成順序是什麼？」

### CURRENT_STATE.md

回答：

「現在 HEAD、tests、完成度、目前能力是什麼？」

### CURRENT_WORK.md

回答：

「現在做什麼？下一步是什麼？」

### GAP_REGISTER.md

回答：

「開發中發現哪些問題？優先級與處理方式是什麼？」

GAP 不等於 roadmap。

GAP 不等於立即實作。

### work/ACTIVE.md

回答：

「這一次 Codex / developer 可以修改什麼、不能修改什麼、怎樣才算完成？」

### DEVELOPMENT_LOG.md

回答：

「過去做過什麼、為什麼做、當時結果是什麼？」

---

## Default Codex Reading

每次執行預設只讀：

    AGENTS.md
    docs/work/ACTIVE.md

ACTIVE 明確要求時，再讀其他 authoritative 文件。

禁止每次重新掃全部 documentation。

---

## Architecture Change Rule

若 architecture decision 發生 material change：

1. 更新 ADR 或新增 ADR。
2. 更新 ARCHITECTURE。
3. 更新 V1_CAPABILITY_MAP。
4. 必要時更新 CURRENT_WORK / GAP_REGISTER。
5. 不得只改聊天內容。

---

## Progress Rule

Overall V1 completion：

以 `V1_CAPABILITY_MAP.md` weighted capability acceptance 為準。

不得使用：

- LOC。
- file count。
- test count。

直接當作完成百分比。
