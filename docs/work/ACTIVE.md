# ACTIVE WORK PACKAGE

## 1. Work Package ID

GAP-RECON-001B

Parent GAP：

GAP-RECON-001

---

## 2. Title

Collection / Startup Readiness

---

## 3. Status

READY_FOR_EXECUTION

Architecture review：

COMPLETED。

Architecture / Design Freeze：

COMPLETED for J710-J780。

Runtime execution authorization：

AUTHORIZED。

Launch Gate：

`RELEASED_WORK_PACKAGE_COMMIT`

Architecture freeze commit：

`a5f98bea429b964bab05782d1f71bad3e9393888`

001A accepted runtime dependency：

`d7dbd884f09e72d7737726409e11e0679206ed8d`

001A deterministic closure：

`c4d799ed2fce3d09836aec41b5b91cb12ccc408f`

001B Work Package preparation commit：

`1772949978f18186d26460434130757f1670a0ea`

---

## 4. Recommended Model

GPT-5.6 Sol

Effort：

輕度

Calibration rule：

本 Work Package 中途不得切換 model 或 effort。

Level 3B 已達 evaluation threshold，但本 Work Package 維持 LEVEL_3A_BOUNDED。

---

## 5. Execution Mode

LEVEL_3A_BOUNDED

只執行 GAP-RECON-001B。

完成後 STOP。

不得自動開始 GAP-BROKER-002。

不得自動開始 GAP-08。

不得自動啟用 Level 3B。

---

## 6. Goal

在已接受的 GAP-RECON-001A reconciliation policy/case foundation 上建立：

- deterministic multi-position collection reconciliation。
- ExpectedPositionLoader read-only seam。
- BrokerPositionProvider startup observation orchestration。
- StartupReadinessState。
- StartupReconciliationResult。
- explicit ExternalStateUnknownError conversion boundary。
- strategy_state_ready explicit dependency。
- READY / HALT / REVIEW startup decision。

不實作 persistence、strategy reconstruction 或 corrective action。

---

## 7. Why This Is Next

GAP-RECON-001A 已 COMPLETED / ACCEPTED。

J710-J780 已完成 design freeze。

GAP-08 persistence/recovery 依賴 reconciliation startup foundation。

因此 001B 為目前唯一 P1 mainline runtime slice。

---

## 8. Baseline

Expected branch：

master

Accepted dependency baseline：

`c4d799ed2fce3d09836aec41b5b91cb12ccc408f`

Architecture freeze ancestor：

`a5f98bea429b964bab05782d1f71bad3e9393888`

Accepted 001A runtime：

`d7dbd884f09e72d7737726409e11e0679206ed8d`

Recorded full regression：

821 passed

Known warning：

GAP-ENV-001 / PytestCacheWarning。

Known local untracked：

data/

不得修改、刪除、stage data/。

Runtime precheck：

- branch = master。
- local master == origin/master。
- execution HEAD 必須包含本 Work Package gate-release commit。
- tracked working tree clean。
- only known untracked data/。

---

## 9. Dependencies

Accepted：

- BrokerAccount。
- AccountPosition。
- BrokerPositionSnapshot。
- BrokerPositionProvider。
- ReconciliationResult。
- ReconciliationPolicy。
- ReconciliationStatus including UNKNOWN_EXTERNAL_STATE。
- ExternalStateUnknownError。
- compare_positions()。
- GAP-RECON-001A policy/case foundation。

Not required：

- PostgreSQL implementation。
- strategy reconstruction implementation。
- broker execution port changes。
- corrective OrderIntent。

---

## 10. Canonical Ownership

Owner：

    trading/reconciliation.py

不得建立 parallel startup/reconciliation domain module。

Dependency direction：

    trading.reconciliation
        -> trading.account read-only contracts

不得 depend on：

- backtest domain models。
- Shioaji native SDK objects。
- persistence implementation。
- execution Broker port。

---

## 11. ReconciliationCollectionError

建立：

    ReconciliationCollectionError

Base：

    ValueError

用途：

- duplicate exact position key。
- ambiguous unmatched collection。
- startup provider 回傳錯誤 account scope。

不得 silent drop / arbitrary pair。

---

## 12. Collection Identity

Scope key：

    broker
    account_ref
    instrument_id

Exact position key：

    broker
    account_ref
    instrument_id
    contract_id

同一 side duplicate exact key：

    ReconciliationCollectionError

contract_id=None 仍是 exact key 的合法值。

---

## 13. Collection Public Contract

Public pure function：

    reconcile_position_collections(
        *,
        expected_positions: tuple[AccountPosition, ...],
        actual_positions: tuple[BrokerPositionSnapshot, ...]
    ) -> tuple[ReconciliationResult, ...]

Function 必須 pure：

- 不 mutate input。
- 不 broker call。
- 不 persistence。
- 不 create OrderIntent。
- 不 create corrective action。

---

## 14. Deterministic Collection Matching

所有 scope 先依下列 key deterministic sort：

    broker
    account_ref
    instrument_id

每個 scope：

1. 先配對 exact contract_id。
2. exact pair 使用 compare_positions()。
3. 若剩餘只有 expected side，依 contract_id deterministic order 產生 INTERNAL_ONLY。
4. 若剩餘只有 actual side，依 contract_id deterministic order 產生 BROKER_ONLY。
5. 若 exactly one expected + one actual leftover，建立 CONTRACT_MISMATCH pair。
6. 若雙方都有 unmatched 且不是唯一 one-to-one，raise ReconciliationCollectionError。

contract_id deterministic ordering：

- None 先於 numeric contract_id。
- numeric contract_id ascending。

禁止：

- list-order pairing。
- quantity-based pairing。
- direction-based pairing。
- silent duplicate removal。

輸入順序不同不得改變 output order。

---

## 15. ExpectedPositionLoader

Public read-only Protocol：

    ExpectedPositionLoader

Contract：

    load_positions(
        account: BrokerAccount
    ) -> tuple[AccountPosition, ...]

Rules：

- owner = trading.reconciliation。
- read-only。
- 不 mutation。
- 不實作 PostgreSQL repository。
- persisted backend 留 GAP-08。

---

## 16. Broker Observation

使用既有：

    BrokerPositionProvider

Contract：

    list_positions(
        account: BrokerAccount
    ) -> tuple[BrokerPositionSnapshot, ...]

Rules：

- 不擴充 execution Broker。
- read-only。
- native broker objects 不得進 reconciliation domain。

Startup orchestration 必須驗證 loader/provider 回傳 position 的 broker/account_ref 與 supplied BrokerAccount 一致。

不一致：

    ReconciliationCollectionError

---

## 17. StartupReadinessState

Exact enum：

    READY
    HALT
    REVIEW

不得新增其他 values。

READY：

- expected load success。
- broker observation success。
- collection reconciliation complete。
- results 全部 MATCH。
- strategy_state_ready=True。

空 expected + 空 actual collection 視為 clean；strategy_state_ready=True 時可 READY。

HALT：

- strategy_state_ready=False。
- STRICT_HALT 有任何 unresolved non-MATCH。
- STRICT_HALT 遇 UNKNOWN_EXTERNAL_STATE。

REVIEW：

- MANUAL_REVIEW 有 unresolved non-MATCH。
- BROKER_AUTHORITATIVE 有 unresolved non-MATCH。
- INTERNAL_AUTHORITATIVE 有 unresolved non-MATCH。
- non-STRICT policy 遇 UNKNOWN_EXTERNAL_STATE。

strategy_state_ready=False 的 HALT 優先於 REVIEW。

---

## 18. StartupReconciliationResult

Canonical immutable model：

    policy: ReconciliationPolicy
    state: StartupReadinessState
    results: tuple[ReconciliationResult, ...]
    strategy_state_ready: bool

Rules：

- frozen / immutable。
- extra forbid。
- READY 只允許 strategy_state_ready=True 且 results 全 MATCH。
- result 不 repair。
- result 不 persistence。
- result 不啟動 strategy。

---

## 19. Startup Public Contract

Public function：

    reconcile_startup(
        *,
        account: BrokerAccount,
        expected_loader: ExpectedPositionLoader,
        broker_position_provider: BrokerPositionProvider,
        policy: ReconciliationPolicy,
        strategy_state_ready: bool
    ) -> StartupReconciliationResult

Flow：

1. expected_loader.load_positions(account)。
2. broker_position_provider.list_positions(account)。
3. validate returned account scope。
4. reconcile_position_collections()。
5. evaluate policy。
6. apply explicit strategy_state_ready dependency。
7. return READY / HALT / REVIEW。

不得啟動 strategy。

---

## 20. ExternalStateUnknownError Conversion

只允許：

    ExternalStateUnknownError

從 broker observation path 轉成：

    ReconciliationResult(
        status=UNKNOWN_EXTERNAL_STATE,
        expected=None,
        actual=None,
        evidence=(nonblank explicit error evidence,)
    )

若 exception message blank：

使用 deterministic nonblank evidence：

    broker external state unavailable

Policy mapping：

- STRICT_HALT -> HALT。
- other policies -> REVIEW。
- strategy_state_ready=False -> HALT。

不得 catch：

- arbitrary Exception。
- programming errors。
- expected loader errors。
- unrelated validation/runtime errors。

上述錯誤必須 propagate。

---

## 21. Policy Evaluation

Regular collection results：

- results 全 MATCH + strategy_state_ready=True -> READY。
- any non-MATCH + STRICT_HALT -> HALT。
- any non-MATCH + non-STRICT policy -> REVIEW。
- strategy_state_ready=False -> HALT。

BROKER_AUTHORITATIVE / INTERNAL_AUTHORITATIVE：

- 不 auto resolve。
- 不 adopt position。
- 不 overwrite expected。
- 不 corrective execution。

---

## 22. Strategy-State Dependency

本 Work Package 只接受 caller supplied：

    strategy_state_ready: bool

不實作：

- strategy persistence。
- reconstruction algorithm。
- feature state restoration。

False：

    HALT

True：

    account reconciliation clean 才可 READY

真正 recovery 留 GAP-08。

---

## 23. Scope Freeze

Implement only：

- J710 Startup Expected-State Load seam。
- J720 Startup Broker Observation orchestration。
- J730 Collection Matching。
- J740 Startup Reconciliation。
- J750 Strategy-State Reconstruction Dependency seam。
- J760 Readiness Decision。
- J770 HALT / REVIEW Startup State。
- J780 No Silent Startup Repair。

Do not implement：

- J340 expected fill/event projection。
- J810-J830 AccountSnapshot。
- PostgreSQL。
- persistence repositories。
- restart persistence recovery。
- strategy reconstruction algorithm。
- feature-state recovery。
- broker native mapping changes。
- corrective execution。
- automatic position adoption。
- LIVE authorization。

---

## 24. Allowed Runtime Files

Primary：

    trading/reconciliation.py

Tests：

    tests/unit/test_reconciliation.py

Only if directly required for compatibility：

    trading/__init__.py

No other runtime files without direct dependency evidence。

---

## 25. Forbidden Areas

Forbidden：

    data/**
    database/**
    adapters/**
    strategy/**
    strategies/**
    features/**
    backtest/**

Do not modify：

    trading/account.py
    trading/execution.py

unless frozen contract is impossible without direct dependency conflict；then HARD_BLOCK。

No real broker login。

No network-dependent tests。

No credentials。

---

## 26. Required Tests

At minimum：

1. ReconciliationCollectionError explicit type。
2. exact-key duplicate expected rejected。
3. exact-key duplicate actual rejected。
4. exact contract pair uses compare_positions。
5. expected-only -> INTERNAL_ONLY。
6. actual-only -> BROKER_ONLY。
7. unique leftover pair -> CONTRACT_MISMATCH。
8. ambiguous unmatched collections rejected。
9. no list-order pairing。
10. no quantity/direction guessing。
11. deterministic output under permuted input。
12. deterministic multi-scope ordering。
13. contract_id None deterministic handling。
14. ExpectedPositionLoader protocol contract。
15. StartupReadinessState exact READY/HALT/REVIEW。
16. StartupReconciliationResult immutable / extra-forbid。
17. clean empty collections + strategy ready -> READY。
18. clean matched collections + strategy ready -> READY。
19. strategy_state_ready=False -> HALT。
20. STRICT_HALT mismatch -> HALT。
21. MANUAL_REVIEW mismatch -> REVIEW。
22. BROKER_AUTHORITATIVE mismatch -> REVIEW。
23. INTERNAL_AUTHORITATIVE mismatch -> REVIEW。
24. ExternalStateUnknownError + STRICT -> HALT。
25. ExternalStateUnknownError + non-STRICT -> REVIEW。
26. UNKNOWN conversion has actual=None and nonblank evidence。
27. blank external-error message still produces deterministic evidence。
28. unexpected broker exception propagates。
29. expected loader exception propagates。
30. wrong-account expected/provider output rejected。
31. provider/loader receives supplied BrokerAccount。
32. no input mutation。
33. no submit / repair / overwrite / adoption capability。
34. all existing GAP-RECON-001A tests remain green。
35. GAP-ACCOUNT compatibility。
36. GAP-BROKER compatibility。
37. full regression。

---

## 27. Compatibility Test Scope

Targeted：

    tests/unit/test_reconciliation.py

Compatibility at least：

    tests/unit/test_trading_account.py
    tests/unit/test_trading_execution.py

Then full regression。

---

## 28. Acceptance Criteria

PASS requires：

- J710-J780 frozen contracts implemented。
- collection matching deterministic。
- duplicate/ambiguity explicit。
- startup account scope enforced。
- only ExternalStateUnknownError converted to UNKNOWN。
- unexpected exceptions propagate。
- READY only on clean reconciliation + strategy_state_ready=True。
- all non-STRICT mismatches remain REVIEW。
- no automatic repair/adoption/order。
- no persistence。
- no strategy reconstruction implementation。
- targeted tests PASS。
- compatibility tests PASS。
- full regression PASS。
- git diff --check PASS。
- no scope creep。

---

## 29. Stop Conditions

HARD_BLOCK if：

- frozen collection matching semantics require change。
- account identity contract requires redesign。
- UNKNOWN semantics require widening catch boundary。
- implementation requires persistence。
- implementation requires broker execution。
- implementation requires strategy reconstruction。
- unrelated core regression。
- data/ modified。
- secret exposure。

---

## 30. Git

After runtime gate release：

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

Commit message：

    feat(trading): add startup reconciliation readiness

No amend / force push / reset --hard。

---

## 31. Documentation Responsibility

Runtime Codex：

- implementation。
- tests。
- debugging。
- integration。
- runtime commit/push。
- final report。

Manual deterministic acceptance：

- Blueprint lifecycle。
- metrics。
- traceability。
- CURRENT_STATE。
- CURRENT_WORK。
- GAP_REGISTER。
- DEVELOPMENT_LOG。

001B runtime complete 後 STOP。

Parent GAP 不由 runtime executor 自動 close。

---

## 32. Blueprint Scope

Implements：

    J710
    J720
    J730
    J740
    J750
    J760
    J770
    J780

Touches：

    J510-J690
    J210-J440

Does Not Implement：

    J340
    J810-J830
    K000+
    L000+

---

## 33. Source Requirements

Source IDs：

    SRC-PYDANTIC-001
    SRC-ADR-001
    SRC-ARCH-001
    SRC-BLUEPRINT-001

External broker source revalidation：

NOT_REQUIRED。

Reason：

本 Work Package 使用既有 broker-neutral BrokerPositionProvider contract，不新增 native Shioaji mapping。

---

## 34. Re-entry Precheck Scope

Default reads：

    AGENTS.md
    docs/work/ACTIVE.md
    trading/reconciliation.py
    trading/account.py
    tests/unit/test_reconciliation.py
    tests/unit/test_trading_account.py

Only read trading/execution.py / tests/unit/test_trading_execution.py when compatibility validation requires。

No whole-repo rescan。

---

## 35. Architect / Codex Responsibility Freeze

Architect has frozen：

- canonical ownership。
- public error type。
- collection keys。
- public collection function signature。
- matching algorithm。
- deterministic ordering。
- ExpectedPositionLoader contract。
- broker observation boundary。
- StartupReadinessState。
- StartupReconciliationResult fields。
- reconcile_startup() public signature。
- UNKNOWN conversion boundary。
- state precedence。
- strategy-state dependency。
- no-corrective-action boundary。
- persistence boundary。

Codex may decide only：

- private helper decomposition。
- fixture organization。
- local error message wording。
- internal sort helper representation。
- other non-public implementation details。

Any required frozen semantic change：

STOP + LEVEL 3。

---

## 36. Runtime Launch Gate

Current：

    RELEASED_WORK_PACKAGE_COMMIT

Release requires：

1. complete GAP-RECON-001B ACTIVE committed。
2. CURRENT_STATE / CURRENT_WORK / GAP_REGISTER / AI_HANDOFF synchronized。
3. Work Package preparation push verified。
4. local master == origin/master。

Release only authorizes GAP-RECON-001B。

GAP-BROKER-002 remains blocked。

Level 3B remains NOT_ENABLED。
