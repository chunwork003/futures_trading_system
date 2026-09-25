# ACTIVE WORK PACKAGE

## 1. Work Package ID

GAP-BROKER-001

---

## 2. Title

Explicit OrderIntent / PositionEffect

---

## 3. Status

COMPLETED

Architecture review：

COMPLETED。

Architecture / Design Freeze：

COMPLETED。

Runtime execution authorization：

COMPLETED。

Launch Gate：

`RELEASED_ARCHITECTURE_FREEZE`

Architecture freeze commit 已 push 並 remote verify：`d74de0cbad75fa32f39fd2e6a04dc7f865c527bb`。

---

## 4. Recommended Model

GPT-5.6 Sol

Effort：

輕度

Calibration rule：

本 Work Package 中途不得切換 model 或 effort。

Reason：

- broker money semantics。
- OPEN / REDUCE / CLOSE business meaning。
- Shioaji New / Cover mapping。
- cross-module execution compatibility。

---

## 5. Execution Mode

LEVEL_3A_BOUNDED

一次只執行本 Work Package。

完成後必須 STOP。

不得自動開始 GAP-RECON-001。

---

## 6. Goal

移除 Shioaji execution 對 order ID naming 的 New / Cover business inference。

建立 broker-neutral：

- OrderIntent。
- PositionEffect。
- pure PositionEffect validation。
- explicit Shioaji Action / FuturesOCType mapping。

Current unsafe truth：

    order_id.startswith("ENTRY-")

完成後：

order ID 只保留 identity / legacy formatting，不能再決定 broker execution semantics。

---

## 7. Why This Is Next

GAP-ACCOUNT-001 已 CLOSED / ACCEPTED。

GAP-RECON-001 的任何 corrective execution 必須先有 explicit execution semantics。

因此目前 mainline dependency 是：

    GAP-BROKER-001

---

## 8. Baseline

Expected branch：

master

Required closure baseline ancestor：

40953f3a9b3e55cbe497990102c8078b609298f8

Recorded full regression：

776 passed

Known warning：

GAP-ENV-001 / PytestCacheWarning。

Known local untracked：

data/

不得修改、刪除或 stage data/。

Execution precheck：

- branch 必須 master。
- local master 必須與 origin/master 一致。
- actual execution HEAD 必須包含 architecture-freeze commit。
- tracked working tree 必須 clean。
- 只允許既知 untracked data/。

---

## 9. Dependencies

Completed：

- GAP-07。
- GAP-ACCOUNT-001。
- Order / Fill foundation。
- Broker execution port。
- Shioaji submit/status/fill/cancel foundation。
- partial fill / dedup / terminal lifecycle。

Relevant pending：

- GAP-RECON-001。
- GAP-08。

---

## 10. Core Invariants

Fixed：

    Order ID != PositionEffect

Fixed：

    PositionDirection != broker native Action

Fixed：

    PositionEffect determines New / Cover semantics

Direction change：

    CLOSE
    -> confirmed FLAT
    -> re-evaluate
    -> OPEN opposite

禁止 single-intent silent reversal。

---

## 11. Scope Freeze

只做：

- trading.execution PositionEffect。
- trading.execution OrderIntent。
- pure expected-position validation。
- Broker submit compatibility seam。
- PaperBroker compatibility。
- ShioajiBroker explicit intent requirement。
- explicit Action mapping。
- explicit New / Cover mapping。
- remove order-ID prefix inference。
- fake / deterministic tests。
- full regression。

不做：

- reconciliation corrective action。
- reconciliation policy。
- persistence。
- OrderEvent persistence。
- restart recovery。
- full OMS migration。
- full adapter relocation。
- strategy changes。
- direct reversal。
- FuturesOCType.Auto business inference。
- DayTrade business semantics。
- LIVE_AUTO。

---

## 12. Canonical Ownership

新增：

    trading/execution.py

Owner：

- PositionEffect。
- OrderIntent。
- PositionEffect validation。

Rule：

`trading.execution` 不得 import `backtest.*`。

允許 import：

    trading.account.PositionDirection
    trading.account.AccountPosition

Existing mechanical Order / Fill 暫時仍在 backtest models。

Ownership migration 留 GAP-ARCH-001。

---

## 13. PositionEffect Contract

Canonical enum：

    OPEN
    REDUCE
    CLOSE

不得加入：

    REVERSE

OPEN：

- FLAT -> position。
- 或 existing same-direction position 增加 exposure。

REDUCE：

- 減少 existing exposure。
- 執行後 quantity 必須仍 > 0。

CLOSE：

- quantity exactly 關閉 existing position 至 FLAT。

---

## 14. OrderIntent Contract

Immutable broker-neutral model。

至少：

    intent_id: str
    correlation_id: str
    causation_id: str | None
    position_direction: PositionDirection
    position_effect: PositionEffect
    quantity: int > 0
    target_position_ref: str | None
    risk_decision_ref: str | None

Rules：

- extra fields forbid。
- frozen / immutable。
- intent_id trim + nonblank。
- correlation_id trim + nonblank。
- optional refs 若存在必須 trim + nonblank。
- quantity > 0。
- 不保存 native Shioaji object。
- 不保存 secret。

target_position_ref / risk_decision_ref：

本 GAP 只作 optional opaque provenance references。

完整 provenance persistence 留 GAP-PERSIST-001。

---

## 15. PositionEffect Validation

建立 pure validation seam。

Conceptual public contract：

    validate_position_effect(
        intent: OrderIntent,
        expected: AccountPosition | None
    ) -> None

Explicit error：

    PositionEffectValidationError

Rules：

- expected=None：只允許 OPEN。
- expected!=None：intent direction 必須與 expected direction 一致。
- OPEN：允許同方向增加 exposure。
- REDUCE：0 < intent.quantity < expected.quantity。
- CLOSE：intent.quantity == expected.quantity。
- REDUCE / CLOSE 超過 expected quantity：reject。
- CLOSE 少於 expected quantity：reject。
- opposite-side intent while non-FLAT：reject。
- 不 mutate expected。
- 不 submit broker order。

---

## 16. Legacy Order Compatibility

Existing：

    backtest.models.Order

保持 mechanical order contract。

Legacy Order.direction 在本 migration slice 定義為：

    position direction

不是 native Buy / Sell action。

Mapping matrix：

| Position Direction | PositionEffect | Native Action | Native OCType |
|---|---|---|---|
| LONG | OPEN | Buy | New |
| SHORT | OPEN | Sell | New |
| LONG | REDUCE | Sell | Cover |
| SHORT | REDUCE | Buy | Cover |
| LONG | CLOSE | Sell | Cover |
| SHORT | CLOSE | Buy | Cover |

---

## 17. Broker Port Compatibility

Existing execution capability 保持同一 responsibility。

允許 bounded signature extension：

    submit_order(
        order,
        *,
        intent: OrderIntent | None = None
    )

Rules：

- backtest.broker.Broker 不新增 account/reconciliation capability。
- PaperBroker 必須保持既有 caller 可省略 intent。
- PaperBroker 可接受 optional intent，但不得改變 fill semantics。
- ShioajiBroker 必須要求 explicit intent。
- ShioajiBroker intent=None 必須 fail fast。
- 不得從 order_id / signal_id / prefix 推定 intent。

---

## 18. Order / Intent Consistency

Shioaji submission 前必須驗證：

- intent.quantity == order.quantity。
- intent.position_direction.value == order.direction.value。

Mismatch：

explicit error。

不得 silent coerce。

---

## 19. Shioaji Mapping

Approved official source：

    SRC-SINOPAC-FUT-ORDER-001

Official API supports：

- Action Buy / Sell。
- FuturesOCType Auto / New / Cover / DayTrade。

本 GAP 只允許：

- New。
- Cover。

本 GAP 禁止：

- Auto business inference。
- DayTrade business semantics。

Native action 必須由：

    PositionDirection + PositionEffect

共同決定。

Native OCType 必須由：

    PositionEffect

決定。

---

## 20. Shioaji Mapping API

Target conceptual seam：

    to_shioaji_order(
        order,
        intent
    )

Mapper：

- validate order / intent consistency。
- derive native Action。
- derive native FuturesOCType。
- preserve price type mapping。
- preserve ROD mapping。
- preserve quantity mapping。

不得由 caller 任意傳 native octype 作 business truth。

---

## 21. Prefix Removal

必須移除：

    order_id.startswith("ENTRY-")

以及任何 equivalent prefix inference。

ENTRY / EXIT 字串可暫時保留作 legacy order ID formatting。

但不能影響：

- Buy / Sell。
- New / Cover。
- OPEN / REDUCE / CLOSE。

Regression test 必須證明：

- ENTRY-prefixed CLOSE 仍映射 Cover。
- EXIT-prefixed OPEN 仍映射 New。

---

## 22. Preferred Runtime Areas

Expected：

    trading/execution.py
    backtest/broker.py
    backtest/paper_broker.py
    backtest/shioaji_broker.py
    backtest/shioaji_mapping.py

Possible direct compatibility consumers only if required：

    backtest/paper_trading.py

Tests：

    tests/unit/test_trading_execution.py
    tests/unit/test_shioaji_mapping.py
    tests/unit/test_shioaji_broker.py
    tests/unit/test_paper_broker.py

只修改真正必要 files。

---

## 23. Forbidden Areas

不得修改：

    data/**
    database/**
    strategy/**
    strategies/**
    features/**

除非直接 dependency conflict，否則不得修改：

    domain/**
    trading/account.py
    trading/reconciliation.py

禁止：

- real broker login。
- real order。
- network-dependent tests。
- credentials。
- unrelated cleanup。
- mass ownership migration。

---

## 24. Required Tests

至少：

1. PositionEffect exact enum values。
2. OrderIntent normalization / nonblank validation。
3. OrderIntent extra forbid / immutability。
4. FLAT only OPEN。
5. same-direction OPEN allowed。
6. valid REDUCE。
7. REDUCE cannot reach zero。
8. valid exact CLOSE。
9. CLOSE under/over quantity reject。
10. opposite direction while non-FLAT reject。
11. PaperBroker omission of intent remains compatible。
12. ShioajiBroker missing intent fails explicitly。
13. six-case LONG/SHORT x OPEN/REDUCE/CLOSE mapping matrix。
14. quantity mismatch reject。
15. direction mismatch reject。
16. ENTRY-prefixed CLOSE maps Cover。
17. EXIT-prefixed OPEN maps New。
18. no Auto fallback。
19. no DayTrade mapping。
20. existing Shioaji status/fill/cancel lifecycle remains green。
21. PaperTradingEngine / Runner compatibility。
22. full regression。

---

## 25. Acceptance Criteria

PASS 必須：

- OrderIntent broker-neutral。
- PositionEffect explicit。
- OPEN / REDUCE / CLOSE validation deterministic。
- native Buy/Sell explicit。
- native New/Cover explicit。
- zero order-ID business inference。
- no Auto fallback。
- no DayTrade guessing。
- PaperBroker compatibility preserved。
- Shioaji lifecycle preserved。
- no corrective reconciliation。
- targeted tests PASS。
- compatibility tests PASS。
- full regression PASS。
- git diff --check PASS。
- no scope creep。

---

## 26. Stop Conditions

HARD_BLOCK if：

- official Shioaji semantics conflict with frozen mapping。
- implementation requires FuturesOCType.Auto to preserve correctness。
- DayTrade semantics becomes required。
- explicit intent cannot be added without breaking core Broker compatibility。
- implementation requires direct reversal。
- unrelated regression。
- data/ modified。
- secret exposed。
- business semantics require guessing。

---

## 27. Git

Runtime launch gate release 後：

    precheck
    -> implementation
    -> targeted tests
    -> compatibility tests
    -> full regression
    -> git diff --check
    -> scope validation
    -> exact staging
    -> commit
    -> push
    -> verify origin/master
    -> final report
    -> STOP

禁止 amend / force push / reset --hard。

---

## 28. Documentation Responsibility

Runtime Codex：

- implementation。
- tests。
- debugging。
- integration。
- runtime commit / push。
- final report。

Deterministic closure 由人工 / PowerShell：

- CURRENT_STATE。
- CURRENT_WORK。
- GAP_REGISTER。
- DEVELOPMENT_LOG。
- Blueprint lifecycle acceptance。

Runtime 完成後 STOP。

---

## 29. Final Report

至少回報：

1. Precheck findings。
2. OrderIntent contract implementation。
3. PositionEffect implementation。
4. validation semantics。
5. Broker port compatibility。
6. PaperBroker compatibility。
7. Shioaji mapping matrix。
8. prefix inference removal evidence。
9. files created / modified。
10. targeted tests。
11. compatibility tests。
12. full regression。
13. warnings。
14. git diff --check。
15. git status。
16. LEVEL 2 items。
17. LEVEL 3 blockers。
18. final commit SHA。
19. origin/master SHA。
20. calibration observations。

不得自動開始 GAP-RECON-001。

---

## 30. Blueprint Scope

Implements：

    H210
    H220
    H230
    H240
    H250

    I340
    I350

Touches：

    H150
    H610
    H710

    I310
    I320
    I360

Does Not Implement：

    H440
    H500+
    H840
    J600
    J700
    K000+
    L000+

H910-H940 已有 direction-transition design freeze，但本 GAP 不新增 direct reversal runtime path。

---

## 31. Source Requirements

Required：

    SRC-SINOPAC-FUT-ORDER-001
    SRC-SINOPAC-CONTRACT-001
    SRC-PYDANTIC-001
    SRC-ADR-001
    SRC-ARCH-001
    SRC-BLUEPRINT-001

Broker source last verified：

2026-09-25。

Change risk：

HIGH。

Runtime execution 前若 official Shioaji semantics material conflict：

HARD_BLOCK。

---

## 32. Re-entry Precheck Scope

Codex 不做 whole-repo rescan。

預設只讀：

    AGENTS.md
    docs/work/ACTIVE.md
    trading/account.py
    backtest/broker.py
    backtest/models.py
    backtest/paper_broker.py
    backtest/shioaji_broker.py
    backtest/shioaji_mapping.py

以及直接相關 tests。

只有 direct dependency conflict 才擴大。

---

## 33. Architect / Codex Responsibility Freeze

人工已決定：

- canonical ownership。
- PositionEffect values。
- OrderIntent public fields。
- validation semantics。
- legacy Order.direction interpretation。
- Broker submit compatibility seam。
- Shioaji Action matrix。
- Shioaji New / Cover matrix。
- Auto prohibition。
- DayTrade exclusion。
- prefix inference prohibition。
- reversal sequencing。
- migration boundary。

Codex 只決定：

- private helper decomposition。
- local exception message wording。
- fixture organization。
- scope-internal implementation detail。

如果需要改變 frozen public semantics：

STOP + LEVEL 3。

---

## 34. Runtime Launch Gate

Current：

    RELEASED_ARCHITECTURE_FREEZE

Release requirements：

1. H210-H250 DESIGN_FROZEN。
2. I340-I350 DESIGN_FROZEN。
3. ACTIVE complete。
4. CURRENT_WORK / GAP_REGISTER / AI_HANDOFF synchronized。
5. official source revalidation PASS。
6. architecture freeze commit pushed：`d74de0cbad75fa32f39fd2e6a04dc7f865c527bb`。
7. local master == origin/master。

Release 後只解除 runtime launch gate。

不得重新開放 frozen architecture。

---

## 35. Closure Evidence

Status：

CLOSED / ACCEPTED

Accepted runtime commit：

`b5d309cc91c6dbdf539c17a46662cdde46716224`

Verification：

- targeted：49 passed。
- compatibility：80 passed。
- full regression：800 passed。
- git diff --check：PASS。
- implementation correction cycles：0。
- command syntax retries：2。

Blueprint acceptance：

- H210 H220 H230 H240 H250 ACCEPTED。
- I340 I350 ACCEPTED。
- lifecycle completion：40.31%。

Calibration：

- GPT-5.6 Sol / 輕度。
- formal Level 3A runtime sample：2。
- user-observed 5HR usage：14%。
- files inspected：約 22。
- runtime/test files changed：20。
- tool operations：24。
- wall time：unavailable。
- token/context：unavailable。

Next：

GAP-RECON-001 READY_FOR_ARCHITECTURE_REVIEW。

本 ACTIVE 保留為 completed Work Package evidence。

新的 runtime ACTIVE 必須等 GAP-RECON-001 architecture review / design freeze 完成後才建立。
