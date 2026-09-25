# ACTIVE WORK PACKAGE

## 1. Work Package ID

GAP-RECON-001A

Parent GAP：

GAP-RECON-001

---

## 2. Title

Reconciliation Policy / Result / Case

---

## 3. Status

READY_FOR_EXECUTION

Architecture review：

COMPLETED。

Architecture / Design Freeze：

COMPLETED。

Runtime execution authorization：

HOLD。

Launch Gate：

`HOLD_FOR_ARCHITECTURE_FREEZE_COMMIT`

Architecture freeze / Work Package 必須先 commit、push、remote verify。

---

## 4. Recommended Model

GPT-5.6 Sol

Effort：

輕度

Calibration rule：

本 Work Package 中途不得切換 model 或 effort。

本次預計作為第 3 筆正式 Level 3A runtime calibration sample。

---

## 5. Execution Mode

LEVEL_3A_BOUNDED

只執行 GAP-RECON-001A。

完成後 STOP。

不得自動開始 GAP-RECON-001B。

不得自動開始 GAP-BROKER-002。

---

## 6. Goal

在既有 pure pairwise reconciliation foundation 上建立：

- ReconciliationResult evidence semantics。
- UNKNOWN_EXTERNAL_STATE。
- ReconciliationPolicy。
- ReconciliationCase。
- pure case creation / resolution。
- explicit no-corrective-action policy boundary。

不處理 collection matching 或 startup orchestration。

---

## 7. Why This Is Next

GAP-ACCOUNT-001 已接受 expected / actual models 與 pairwise comparator。

GAP-BROKER-001 已接受 explicit OrderIntent / PositionEffect。

GAP-RECON-001 public semantics 已凍結。

先完成 001A domain policy/case，才進 001B startup readiness orchestration。

---

## 8. Baseline

Expected branch：

master

Required closure baseline ancestor：

171b8f87024aa0abe444870f1f7a25dc506b57be

Recorded full regression：

800 passed

Known warning：

GAP-ENV-001 / PytestCacheWarning。

Known local untracked：

data/

不得修改、刪除、stage data/。

Runtime precheck：

- master。
- local master == origin/master。
- execution HEAD 必須包含 architecture-freeze commit。
- tracked working tree clean。
- only known untracked data/。

---

## 9. Dependencies

Accepted：

- trading.account.AccountPosition。
- trading.account.BrokerPositionSnapshot。
- ReconciliationStatus six existing values。
- ReconciliationResult foundation。
- compare_positions()。
- fixed comparison precedence。
- GAP-BROKER-001 explicit execution semantics。

Not required for 001A：

- PostgreSQL。
- BrokerPositionProvider orchestration。
- startup state loader。

---

## 10. Canonical Ownership

Owner：

    trading/reconciliation.py

不得建立 parallel reconciliation domain model。

trading.reconciliation 不得 depend on：

- backtest models。
- Shioaji native SDK objects。
- persistence implementation。
- execution Broker port。

---

## 11. ReconciliationStatus

保留 existing：

    MATCH
    INTERNAL_ONLY
    BROKER_ONLY
    CONTRACT_MISMATCH
    DIRECTION_MISMATCH
    QUANTITY_MISMATCH

新增：

    UNKNOWN_EXTERNAL_STATE

Exact enum values 不得再擴充。

compare_positions() 不自行產生 UNKNOWN_EXTERNAL_STATE。

---

## 12. ReconciliationResult

Existing fields：

    status
    expected
    actual

新增：

    evidence: tuple[str, ...] = ()

Rules：

- frozen / immutable。
- extra forbid。
- evidence item trim + nonblank。
- existing compare_positions() callers 可不傳 evidence。
- UNKNOWN_EXTERNAL_STATE 必須至少一筆 evidence。
- UNKNOWN_EXTERNAL_STATE 的 actual 必須為 None。
- UNKNOWN_EXTERNAL_STATE 不得 fabricated actual snapshot。

---

## 13. ExternalStateUnknownError

建立：

    ExternalStateUnknownError

Base：

    RuntimeError

責任：

- 明確表示 broker external observation 無法安全取得或 canonicalize。

不代表：

- programming error。
- validation bug。
- arbitrary Exception。

001A 只定義 contract。

001B 才負責 orchestration conversion。

---

## 14. ReconciliationPolicy

Exact enum：

    STRICT_HALT
    MANUAL_REVIEW
    BROKER_AUTHORITATIVE
    INTERNAL_AUTHORITATIVE

不得新增 AUTO_REPAIR。

不得新增 SILENT_SYNC。

---

## 15. ReconciliationCaseState

Exact enum：

    HALT
    REVIEW_REQUIRED
    RESOLVED

不得用 READY 作 case state。

READY 屬 001B startup readiness。

---

## 16. ReconciliationCase

Immutable model：

    case_id: str
    result: ReconciliationResult
    policy: ReconciliationPolicy
    state: ReconciliationCaseState
    resolution_note: str | None = None

Rules：

- extra forbid。
- case_id trim + nonblank。
- caller supplies case_id。
- no hidden UUID。
- no hidden now()。
- HALT / REVIEW_REQUIRED -> resolution_note must be None。
- RESOLVED -> resolution_note required, trim + nonblank。
- no DB/persistence ID。

---

## 17. ReconciliationCaseError

建立 explicit：

    ReconciliationCaseError

Base：

    ValueError

使用於：

- MATCH result attempted to create case。
- invalid state transition。
- resolution without valid note。

---

## 18. Case Creation Contract

Public pure function：

    create_reconciliation_case(
        *,
        case_id: str,
        result: ReconciliationResult,
        policy: ReconciliationPolicy
    ) -> ReconciliationCase

Rules：

- MATCH -> ReconciliationCaseError。
- STRICT_HALT mismatch -> HALT。
- MANUAL_REVIEW mismatch -> REVIEW_REQUIRED。
- BROKER_AUTHORITATIVE mismatch -> REVIEW_REQUIRED。
- INTERNAL_AUTHORITATIVE mismatch -> REVIEW_REQUIRED。
- UNKNOWN_EXTERNAL_STATE follows the same policy mapping。
- resolution_note initially None。
- no mutation。
- no broker action。

---

## 19. Case Resolution Contract

Public pure function：

    resolve_reconciliation_case(
        case: ReconciliationCase,
        *,
        resolution_note: str
    ) -> ReconciliationCase

Rules：

- HALT -> RESOLVED allowed。
- REVIEW_REQUIRED -> RESOLVED allowed。
- already RESOLVED -> ReconciliationCaseError。
- resolution_note trim + nonblank。
- returns new immutable case。
- input case unchanged。
- no expected-state overwrite。
- no broker order。

---

## 20. Authority Policies

BROKER_AUTHORITATIVE：

- indicates explicit human/system resolution authority only。
- does not copy actual -> expected。

INTERNAL_AUTHORITATIVE：

- indicates explicit resolution authority only。
- does not create corrective OrderIntent。

Neither authority policy auto-resolves a case。

Both start REVIEW_REQUIRED。

---

## 21. Existing Comparator Compatibility

Must preserve：

    compare_positions(expected, actual)

Precedence：

    contract
    -> direction
    -> quantity
    -> MATCH

Existing six statuses retain exact values。

Existing tests must remain green。

compare_positions() remains：

- pure。
- no mutation。
- no broker call。
- no corrective order。

---

## 22. Scope Freeze

Implement only：

- J610 ReconciliationResult。
- J620 ReconciliationCase。
- J630 STRICT_HALT。
- J640 MANUAL_REVIEW。
- J650 BROKER_AUTHORITATIVE。
- J660 INTERNAL_AUTHORITATIVE。
- J670 comparison precedence verification。
- J680 UNKNOWN_EXTERNAL_STATE。
- J690 no automatic corrective action。

Do not implement：

- J710-J780。
- ExpectedPositionLoader。
- collection matching。
- startup orchestration。
- startup READY/HALT/REVIEW result。
- J340 expected fill/event projection。
- J810-J830。
- PostgreSQL。
- persistence。
- strategy reconstruction。
- broker mapping changes。
- corrective execution。
- automatic position adoption。

---

## 23. Allowed Runtime Files

Primary：

    trading/reconciliation.py

Tests：

    tests/unit/test_reconciliation.py

Only if directly required for compatibility：

    trading/__init__.py

No other runtime files without direct dependency evidence。

---

## 24. Forbidden Areas

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

unless frozen contract is impossible to implement without a direct dependency conflict；then HARD_BLOCK。

No real broker login。

No network-dependent tests。

No credentials。

---

## 25. Required Tests

At minimum：

1. existing six ReconciliationStatus values unchanged。
2. UNKNOWN_EXTERNAL_STATE exact value。
3. existing compare_positions status matrix remains green。
4. existing comparison precedence remains green。
5. ReconciliationResult evidence default = empty tuple。
6. evidence normalization。
7. blank evidence reject。
8. UNKNOWN requires evidence。
9. UNKNOWN actual must be None。
10. ReconciliationPolicy exact four values。
11. ReconciliationCaseState exact three values。
12. case_id normalization / nonblank validation。
13. MATCH cannot create case。
14. STRICT_HALT mismatch -> HALT。
15. MANUAL_REVIEW mismatch -> REVIEW_REQUIRED。
16. BROKER_AUTHORITATIVE mismatch -> REVIEW_REQUIRED。
17. INTERNAL_AUTHORITATIVE mismatch -> REVIEW_REQUIRED。
18. UNKNOWN + STRICT_HALT -> HALT。
19. UNKNOWN + non-STRICT -> REVIEW_REQUIRED。
20. valid HALT resolution -> RESOLVED。
21. valid REVIEW_REQUIRED resolution -> RESOLVED。
22. blank resolution note reject。
23. already RESOLVED cannot resolve again。
24. original case remains unchanged。
25. models extra-forbid / immutable。
26. no submit / repair / overwrite capability exposed。
27. GAP-ACCOUNT reconciliation compatibility。
28. GAP-BROKER execution compatibility。
29. full regression。

---

## 26. Compatibility Test Scope

Targeted：

    tests/unit/test_reconciliation.py

Compatibility should include at least：

    tests/unit/test_trading_account.py
    tests/unit/test_trading_execution.py

plus any directly affected existing reconciliation tests。

Then full regression。

---

## 27. Acceptance Criteria

PASS requires：

- frozen public contracts implemented exactly。
- existing pairwise comparator compatibility preserved。
- all authority policies remain non-corrective。
- no hidden UUID。
- no hidden now()。
- no persistence。
- no startup orchestration。
- no broker action。
- targeted tests PASS。
- compatibility tests PASS。
- full regression PASS。
- git diff --check PASS。
- no scope creep。

---

## 28. Stop Conditions

HARD_BLOCK if：

- frozen policy semantics require change。
- ReconciliationResult compatibility cannot be preserved。
- implementation requires persistence。
- implementation requires broker execution。
- implementation requires account model redesign。
- startup semantics become necessary for 001A correctness。
- unrelated core regression。
- data/ modified。
- secret exposure。

---

## 29. Git

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

    feat(trading): add reconciliation policy foundation

No amend / force push / reset --hard。

---

## 30. Documentation Responsibility

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

001A runtime complete 後 STOP。

---

## 31. Blueprint Scope

Implements：

    J610
    J620
    J630
    J640
    J650
    J660
    J670
    J680
    J690

Touches：

    J510
    J520
    J530
    J540
    J550
    J560
    J570
    J580
    J590

Does Not Implement：

    J710-J780
    J340
    J810-J830
    K000+
    L000+

---

## 32. Source Requirements

Source IDs：

    SRC-PYDANTIC-001
    SRC-ADR-001
    SRC-ARCH-001
    SRC-BLUEPRINT-001

External broker source revalidation：

NOT_REQUIRED for 001A。

Reason：

001A 只建立 broker-neutral internal reconciliation policy/case semantics，不新增 native broker mapping。

---

## 33. Re-entry Precheck Scope

Default reads：

    AGENTS.md
    docs/work/ACTIVE.md
    trading/reconciliation.py
    trading/account.py
    tests/unit/test_reconciliation.py
    tests/unit/test_trading_account.py

Only read trading/execution.py / execution tests if compatibility validation requires。

No whole-repo rescan。

---

## 34. Architect / Codex Responsibility Freeze

Architect has frozen：

- ownership。
- enums。
- public model fields。
- evidence rules。
- policy mapping。
- case lifecycle。
- creation function。
- resolution function。
- error contracts。
- compatibility boundary。
- no-corrective-action boundary。
- 001A / 001B split。

Codex may decide only：

- private helper decomposition。
- fixture organization。
- local error message wording。
- non-public implementation details。

Any required frozen semantic change：

STOP + LEVEL 3。

---

## 35. Runtime Launch Gate

Current：

    HOLD_FOR_ARCHITECTURE_FREEZE_COMMIT

Release requires：

1. J610-J780 design freeze committed。
2. GAP-RECON-001A ACTIVE committed。
3. CURRENT_STATE / CURRENT_WORK / GAP_REGISTER / AI_HANDOFF synchronized。
4. architecture freeze push verified。
5. local master == origin/master。

Release only authorizes 001A。

001B remains blocked。
