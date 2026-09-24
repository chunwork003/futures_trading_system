# ACTIVE WORK PACKAGE

## 1. Work Package ID

GAP-ACCOUNT-001

---

## 2. Title

Broker Account / Position Sync Foundation

---

## 3. Status

READY_FOR_EXECUTION

Architecture review 已完成。

此 Work Package 已授權一次 Level 3A bounded runtime execution。

---

## 4. Recommended Model

GPT-5.6 Sol

Reason：

涉及：

- broker actual state。
- account identity。
- position semantics。
- expected/actual boundary。
- reconciliation semantics。

---

## 5. Execution Mode

LEVEL_3A_BOUNDED

一次只執行本 Work Package。

完成後必須 STOP，不得自動開始下一個 Work Package。

---

## 6. Goal

建立 broker-neutral、read-only Account / Position Sync foundation。

使系統可以明確表示：

- BrokerAccount。
- internal expected AccountPosition。
- BrokerPositionSnapshot。
- broker actual observation。
- expected vs actual mismatch。

本 Work Package 不執行 corrective broker order。

---

## 7. Why This Is Next

GAP-07 已 CLOSED。

Canonical instrument/contract/broker mapping 已完成。

Persistence、Recovery、Live Safety 前：

系統必須先能表示與比較：

internal expected account state

與

broker actual state。

---

## 8. Baseline

Expected branch：

master

Required architecture baseline ancestor：

771f10f

Execution precheck：

- current branch 必須是 `master`。
- `master` 必須與 `origin/master` 一致。
- actual execution HEAD 由 Codex 啟動時記錄。
- actual execution HEAD 必須包含 `771f10f` architecture baseline。
- tracked working tree 必須 clean。
- 允許既知 untracked `data/`，但不得修改、刪除或 stage。

不再要求 ACTIVE 文件內保存「精確 current HEAD」：

因為 ACTIVE 本身的 documentation commit 會改變 HEAD，精確 SHA 會形成自我參照並立即 stale。

Recorded regression baseline：

745 passed

Known warning：

GAP-ENV-001 / PytestCacheWarning。

Known local untracked：

data/

不得修改、刪除或 stage `data/`。

---

## 9. Dependencies

Completed：

- ADR-001。
- GAP-07。
- Broker port foundation。
- Shioaji adapter foundation。
- BrokerInstrumentReference。

Relevant pending：

- GAP-BROKER-001。
- GAP-RECON-001。
- GAP-08。

---

## 10. Confirmed Architecture

Fixed：

    LogicalAccount != BrokerAccount

Fixed：

    StrategyPosition
    != TargetAccountPosition
    != AccountPosition
    != BrokerPositionSnapshot

BrokerPositionSnapshot：

broker actual observation。

AccountPosition：

internal expected state。

不得 silent overwrite。

---

## 11. Sequencing Safety

本 Work Package 可以：

- 建立 read-only account/position models。
- 建立 broker query seam。
- 建立 mismatch comparison foundation。

本 Work Package 不可以：

- corrective broker order。
- automatic repair。
- force close/open。
- reconciliation action that changes broker state。

Corrective execution 必須等：

GAP-BROKER-001 OrderIntent / PositionEffect。

---

## 12. Scope Freeze

只做：

- BrokerAccount。
- BrokerPositionSnapshot。
- read-only account/position query contract。
- minimal Shioaji mapping seam。
- pure mismatch comparison。
- compatibility tests。
- full regression。

不做：

- persistence。
- database。
- restart recovery。
- LIVE_AUTO。
- capability matrix。
- corrective order。
- full adapter relocation。
- package cleanup。
- strategy changes。
- ASP.NET Core。
- React。

---

## 13. Preferred Ownership

Target：

    trading/account
    trading/reconciliation

但此次只建立 immediate consumer 需要的最小 modules。

禁止建立：

- service locator。
- event bus。
- DDD aggregate framework。
- empty package hierarchy。

Package rule：

只有存在本 Work Package 的立即 implementation / consumer / test 時，才建立新 package/module。

不得預先建立完整 target architecture 空骨架。

如果本 Work Package 首次建立 `trading/` package：

同步更新 `pyproject.toml` package discovery 加入 `trading*`。

只有真的建立 `adapters/` package 時才加入 `adapters*`。

不得預先加入不存在的 future packages。

---

## 14. BrokerAccount Requirements

Broker-neutral。

至少表示：

- broker identifier。
- broker account stable reference。
- optional display metadata。

不得保存：

- password。
- API secret。
- Shioaji account native object。
- any broker SDK object。

---

## 15. BrokerPositionSnapshot Requirements

至少表示：

- broker。
- broker account reference。
- canonical instrument identity。
- canonical/listed contract reference。
- direction。
- quantity。
- observed timestamp。

如果 broker source 有明確已知 average price：

可以 optional observation。

不得將 BrokerPositionSnapshot 當成 internal AccountPosition。

---

## 16. Internal AccountPosition

Existing：

`backtest/account_position.py`

Architecture review decision：

本 Work Package 不搬移、不刪除、不 big-bang rewrite 此 model。

先查 current consumers。

如果新 broker-neutral account layer 需要與 existing AccountPosition 整合：

建立最小 compatibility seam。

GAP-ARCH-001 / GAP-ARCH-002 ownership migration 不得混入本 Work Package。

---

## 17. Broker Query Port

Architecture review decision：

固定採用：

B. separate read-only account/position capability interface。

不得擴充目前：

`backtest.broker.Broker`

原因：

目前 Broker port 是 execution capability：

- submit_order。
- get_order。
- get_fills。
- cancel_order。

Account / Position observation 是不同 capability。

不得迫使：

- PaperBroker。
- historical backtest broker。
- unrelated execution implementations。

實作 live-only account query methods。

Preferred direction：

- account snapshot/query capability。
- position snapshot/query capability。

具體 class/protocol 命名可由 implementation 在 scope 內決定，但 responsibility 不得重新合併回 execution Broker ABC。

---

## 18. Shioaji Boundary

只允許：

- fake objects。
- mocks。
- deterministic unit tests。

禁止：

- real broker login。
- real account query。
- real order。
- network-dependent tests。
- credentials。

如果 Shioaji native position semantics 無法從 existing implementation 或 approved source 確認：

HARD_BLOCK。

不得猜：

- side semantics。
- quantity semantics。
- today/yesterday position meaning。
- account selection semantics。
- contract identity semantics。

---

## 19. Reconciliation Foundation

本 Work Package 只建立 pure comparison foundation。

至少能表示：

- MATCH。
- INTERNAL_ONLY。
- BROKER_ONLY。
- DIRECTION_MISMATCH。
- QUANTITY_MISMATCH。
- CONTRACT_MISMATCH。

禁止 corrective action。

---

## 20. Preferred Runtime Areas

Precheck / possible changes：

    trading/**
    domain/**
    backtest/broker.py
    backtest/account_position.py
    backtest/shioaji_*

Tests：

    tests/unit/**

只修改真正必要 files。

---

## 21. Forbidden Areas

不得修改：

    data/**
    database/**
    strategy/**
    strategies/**
    features/**

禁止：

- real credentials。
- live order execution。
- persistence implementation。
- full backtest model migration。
- unrelated cleanup。
- Git history rewrite。

---

## 22. Compatibility

必須保持：

- PaperBroker。
- PaperTradingEngine。
- PaperTradingRunner。
- ShioajiBroker existing order lifecycle。
- BacktestEngine。
- current 745-test baseline behavior。

---

## 23. Required Tests

至少覆蓋：

1. BrokerAccount validation。
2. BrokerPositionSnapshot validation。
3. Core model 禁止 native broker object。
4. internal expected 與 broker actual 明確分離。
5. account identity mapping。
6. MATCH。
7. INTERNAL_ONLY。
8. BROKER_ONLY。
9. DIRECTION_MISMATCH。
10. QUANTITY_MISMATCH。
11. CONTRACT_MISMATCH。
12. no corrective execution。
13. fake Shioaji mapping only。
14. current PaperBroker compatibility。
15. full regression。

---

## 24. Acceptance Criteria

PASS 必須：

- broker-neutral BrokerAccount。
- BrokerPositionSnapshot。
- expected/actual separation。
- read-only query seam。
- pure mismatch comparison。
- no corrective execution。
- no secrets。
- no native object leaked into core。
- no DB dependency。
- no network test。
- targeted tests PASS。
- full regression PASS。
- no scope creep。

---

## 25. Stop Conditions

HARD_BLOCK if：

- Shioaji account/position semantics 需要猜。
- 需要 real broker login 才能定義 model。
- 必須先做 corrective order。
- existing Broker ABC compatibility 無法安全維持。
- expected/actual architecture 發生 conflict。
- unrelated regression。
- `data/` modified。
- secret exposed。
- business semantics unclear。

---

## 26. Git

正式批准後才執行。

流程：

    precheck
    → implementation
    → targeted tests
    → relevant tests
    → full regression
    → git diff --check
    → scope validation
    → exact staging
    → commit
    → push
    → verify

禁止：

- amend historical commit。
- force push。
- reset --hard。

---

## 27. Documentation

Runtime Codex 本次主要責任：

- implementation。
- tests。
- debugging。
- integration。
- scope validation。
- runtime commit / push。
- final report。

Deterministic documentation closure 預設由人工 / PowerShell 處理：

- CURRENT_STATE。
- CURRENT_WORK。
- GAP_REGISTER。
- DEVELOPMENT_LOG。

只有 runtime implementation 發現真正 architecture decision change 時：

回報 LEVEL 2 / LEVEL 3。

不要自行大規模重寫：

- ARCHITECTURE。
- AI_HANDOFF。

Runtime 完成後：

STOP。

不得因 documentation closure 自動開始下一個 Work Package。

---

## 28. Final Report

回報：

1. Precheck findings。
2. Chosen account-query port design。
3. Account models。
4. Broker snapshot semantics。
5. Expected/actual separation。
6. Reconciliation comparison。
7. Shioaji fake mapping。
8. Files created。
9. Files modified。
10. Targeted tests。
11. Relevant integration tests。
12. Full regression。
13. Warnings。
14. git diff --check。
15. git status。
16. New LEVEL 2 items。
17. LEVEL 3 blockers。
18. Recommendation。

不要自動開始下一個 Work Package。
