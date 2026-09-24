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
    adapters/sinopac/**
    domain/broker_instruments.py
    backtest/broker.py
    backtest/account_position.py
    backtest/shioaji_*
    pyproject.toml

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
---

## 29. Architect Design Freeze — GAP-ACCOUNT-001

本節為人工 architecture review 的最終 implementation contract。

Codex 不得重新設計以下 public semantics。

### 29.1 Minimal Runtime Layout

本 Work Package 預期只建立立即需要的 target modules：

    trading/__init__.py
    trading/account.py
    trading/reconciliation.py

    adapters/__init__.py
    adapters/sinopac/__init__.py
    adapters/sinopac/account_mapping.py

必要時修改：

    domain/broker_instruments.py
    pyproject.toml

Existing：

    backtest/account_position.py
    backtest/broker.py
    backtest/shioaji_*

保持 compatibility。

不得把既有 Shioaji execution implementation 搬入 adapters。

新 account observation mapping 直接放：

    adapters/sinopac/

這不是 full adapter relocation。

如果建立 `trading/`：

`pyproject.toml` 加入：

    "trading*"

如果建立 `adapters/`：

加入：

    "adapters*"

不得加入尚未存在的 future packages。

### 29.2 Canonical Position Direction

`trading.account` 建立 broker-neutral：

    PositionDirection

只允許：

    LONG
    SHORT

不得讓 trading core import：

    backtest.models.Direction

Existing backtest Direction 保持 compatibility，不在本 GAP migration。

### 29.3 BrokerAccount Contract

`BrokerAccount` 至少：

    broker: str
    account_ref: str
    account_type: str | None
    display_name: str | None

Rules：

- `broker` trim + uppercase。
- `account_ref` trim、不可 blank。
- `account_type` 是 broker-neutral metadata，不保存 native SDK object。
- extra fields forbid。
- 不保存 password。
- 不保存 API key / secret。
- 不保存 person_id。
- 不保存 username。
- 不保存 Shioaji native account object。

Shioaji mapping：

    broker = "SINOPAC"

`account_ref` 使用官方 CLI/API 已採用的：

    BROKER_ID-ACCOUNT_ID

形式組成 opaque provider-scoped reference。

Native：

    F → FUTURES_OPTIONS
    S → SECURITIES
    H → INTERNATIONAL

本 Work Package 的 position mapping 只處理 futures/options account。

### 29.4 Canonical AccountPosition Contract

建立新的：

    trading.account.AccountPosition

表示：

internal expected physical account state。

至少：

    broker: str
    account_ref: str
    instrument_id: int
    contract_id: int | None
    direction: PositionDirection
    quantity: int > 0

Rules：

- futures listed position 的 `contract_id` 必須存在。
- future stocks / non-listed instruments 可允許 `contract_id=None`。
- quantity=0 不表示 FLAT。
- FLAT 使用「position absence」表示。

Existing：

    backtest.account_position.AccountPosition

保持原樣。

本 GAP 不 rename、不刪除、不搬移。

### 29.5 BrokerPositionSnapshot Contract

至少：

    broker: str
    account_ref: str
    instrument_id: int
    contract_id: int | None
    direction: PositionDirection
    quantity: int > 0
    observed_at: timezone-aware datetime
    average_price: Decimal | None

Rules：

- broker actual observation。
- extra fields forbid。
- quantity=0 不建立 snapshot。
- `observed_at` 必須 timezone-aware。
- 禁止 naive datetime。
- operational price 使用 Decimal。
- adapter 若來源為 float，使用 `Decimal(str(value))`。
- 不保存 native broker position object。

### 29.6 Read-Only Ports

建立 two interface-segregated read-only capabilities：

    BrokerAccountProvider
    BrokerPositionProvider

Conceptual signatures：

    list_accounts() -> tuple[BrokerAccount, ...]

    list_positions(
        account: BrokerAccount
    ) -> tuple[BrokerPositionSnapshot, ...]

Rules：

- 不擴充 `backtest.broker.Broker`。
- port 本身無 corrective methods。
- port 不包含 submit/cancel/repair。
- 本 Work Package 不實作 real network provider。

### 29.7 Reverse Broker Instrument Resolution

Shioaji position 回報 broker `code`。

Existing `BrokerInstrumentResolver.resolve()` 是：

canonical → broker。

本 Work Package 允許在：

    domain/broker_instruments.py

新增 exact reverse contract-level lookup：

    resolve_by_broker_contract_code(
        broker,
        broker_contract_code,
        as_of_date
    )

Rules：

- broker normalize。
- broker contract code trim。
- broker contract code 保持 case-sensitive。
- 只接受 `contract_id is not None` 的 contract-level reference。
- effective date 使用既有 inclusive semantics。
- listed broker position 禁止 instrument-level fallback。
- missing → existing explicit mapping-not-found error。
- multiple valid mappings → existing ambiguous mapping error。

不得猜 canonical contract。

### 29.8 Approved Shioaji Account Semantics

人工 architecture review 已以 Sinopac 官方 Shioaji documentation 確認：

Account query：

    api.list_accounts()

native account 可提供：

    account_type
    broker_id
    account_id
    signed
    username
    person_id

Core mapping 本 GAP 只使用：

    account_type
    broker_id
    account_id

不得把：

    person_id
    username

帶入 canonical BrokerAccount。

### 29.9 Approved Shioaji Futures Position Semantics

官方 `FuturePosition` 明確提供：

    id
    code
    direction
    quantity
    price
    last_price
    pnl

本 Work Package 只使用：

    code
    direction
    quantity
    price

Mapping：

    Buy  → LONG
    Sell → SHORT

    quantity → quantity
    price → average_price

不將：

    last_price
    pnl

納入本 GAP canonical snapshot。

Futures top-level `FuturePosition` 不提供 yd_quantity：

不得自行建立 today/yesterday position semantics。

### 29.10 Pure Sinopac Mapping

建立 pure mapping seam：

    adapters/sinopac/account_mapping.py

不得登入。

不得 network。

不得建立 real Shioaji session。

Mapper 必須由 caller 明確提供：

    observed_at
    as_of_date
    BrokerInstrumentResolver

禁止 hidden current date/time。

Unknown：

- direction。
- account type。
- broker contract code。
- ambiguous canonical mapping。

必須 explicit error。

不得猜。

### 29.11 Reconciliation Foundation

本 Gap 只做 pairwise pure comparison。

建立：

    ReconciliationStatus
    ReconciliationResult
    compare_positions(...)

Required statuses：

    MATCH
    INTERNAL_ONLY
    BROKER_ONLY
    CONTRACT_MISMATCH
    DIRECTION_MISMATCH
    QUANTITY_MISMATCH

Expected：

    trading.account.AccountPosition | None

Actual：

    BrokerPositionSnapshot | None

Semantics：

- expected=None + actual=None → MATCH。
- expected!=None + actual=None → INTERNAL_ONLY。
- expected=None + actual!=None → BROKER_ONLY。

兩邊都有 position 時：

先確認：

    broker
    account_ref
    instrument_id

相同。

若上述 identity 不同：

不是同一可比較 position pair。

raise explicit comparison error。

Comparison precedence：

1. contract_id 不同 → CONTRACT_MISMATCH。
2. direction 不同 → DIRECTION_MISMATCH。
3. quantity 不同 → QUANTITY_MISMATCH。
4. otherwise → MATCH。

`ReconciliationResult` 至少保存：

    status
    expected
    actual

不得：

- mutate expected。
- mutate actual。
- submit order。
- repair broker state。
- silent overwrite。

多 position collection matching / startup policy：

留給 GAP-RECON-001。

### 29.12 Compatibility Boundary

本 GAP 不修改既有：

    backtest.account_position.AccountPosition

public behavior。

不要求 legacy AccountPosition 立即轉為 canonical AccountPosition。

Compatibility acceptance：

existing account/paper/backtest tests 必須保持 green。

Canonical AccountPosition 將供新 account/reconciliation path 使用。

Legacy migration 留 GAP-ARCH-001 / GAP-ARCH-002。

### 29.13 Expected New Tests

至少新增：

    tests/unit/test_trading_account.py
    tests/unit/test_reconciliation.py
    tests/unit/test_sinopac_account_mapping.py

並擴充：

    tests/unit/test_broker_instrument_reference.py

Required cases：

- model normalization / validation。
- native object extra rejection。
- timezone-aware observed_at。
- Decimal average price。
- exact reverse broker contract mapping。
- missing mapping。
- ambiguous mapping。
- Buy/LONG。
- Sell/SHORT。
- account identity mapping。
- no PII/native object leakage。
- MATCH。
- INTERNAL_ONLY。
- BROKER_ONLY。
- CONTRACT_MISMATCH。
- DIRECTION_MISMATCH。
- QUANTITY_MISMATCH。
- non-comparable identity explicit error。
- no corrective behavior。

### 29.14 Re-entry Precheck Scope

Codex restart 不做 whole-repo re-analysis。

預設只重新讀：

    AGENTS.md
    docs/work/ACTIVE.md
    pyproject.toml
    domain/broker_instruments.py
    backtest/broker.py
    backtest/account_position.py
    backtest/shioaji_mapping.py

以及直接相關 tests。

只有發現 dependency conflict 才擴大讀取範圍。

### 29.15 Architect / Codex Responsibility Freeze

人工已決定：

- package ownership。
- account identity。
- canonical models。
- read-only port split。
- operational time semantics。
- numeric semantics。
- Shioaji field mapping。
- reverse contract resolution。
- reconciliation precedence。
- compatibility boundary。
- migration boundary。
- corrective execution prohibition。

Codex 只需決定：

- private helper implementation。
- local code decomposition。
- test fixture organization。
- scope-internal implementation detail。

如果 implementation 需要改變上述人工決策：

STOP。

回報 LEVEL 3 architecture conflict。

不得自行重新設計。
