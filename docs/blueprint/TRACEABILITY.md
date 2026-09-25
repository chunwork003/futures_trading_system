# Blueprint Traceability

## Status

AUTHORITATIVE
---

## 1. Required Chain

每個正式 engineering leaf 最終必須可追蹤：

    V1 Capability
    → Blueprint Leaf
    → GAP
    → Work Package
    → Runtime File
    → Test
    → External Source
    → Commit
    → Acceptance

---

## 2. Traceability Fields

| Field | Meaning |
|---|---|
| Capability ID | V1_CAPABILITY_MAP ID |
| Blueprint ID | engineering leaf |
| GAP | problem / required development |
| Work Package | bounded execution contract |
| Runtime Path | implementation |
| Test Path | verification |
| Source ID | official/internal semantics source |
| Commit | accepted implementation commit |
| Lifecycle | blueprint lifecycle |
| Acceptance | PASS/FAIL |

---

## 3. GAP-ACCOUNT-001 Accepted Mapping

此 mapping 已由 accepted runtime commit `50813b679f818f3837a9f50fdcda9921495ab507` 驗證。

### Canonical / Broker Identity

    D630
        Reverse broker contract resolution

### Broker Adapter

    I510
        Broker account identity mapping

    I520
        Account type normalization

    I530
        Native / PII filtering

    I610
        Futures position mapping

    I620
        Direction mapping

    I630
        Quantity / price mapping

    I640
        Contract reverse-resolution integration

    I650
        Observation-time injection

### Account

    J210
        BrokerAccount model

    J220
        Broker stable account reference

    J230
        Broker account metadata validation

    J240
        BrokerAccountProvider

    J310
        Canonical AccountPosition

    J320
        Expected position identity

    J330
        Quantity / direction semantics

    J410
        BrokerPositionProvider

    J420
        BrokerPositionSnapshot

    J430
        Actual position identity

    J440
        Observation / Decimal semantics

### Pure Comparison

    J510
        Pairwise comparator

    J520
        ReconciliationStatus

    J530
        MATCH

    J540
        INTERNAL_ONLY

    J550
        BROKER_ONLY

    J560
        CONTRACT_MISMATCH

    J570
        DIRECTION_MISMATCH

    J580
        QUANTITY_MISMATCH

    J590
        Non-comparable identity error

### Explicitly Not Implemented

    J600
        Reconciliation policies

    J700
        Startup readiness

    H200
        OrderIntent / PositionEffect

---

## 4. Current Known Runtime Paths

Existing compatibility：

    domain/broker_instruments.py
    backtest/account_position.py
    backtest/broker.py
    backtest/shioaji_*

Target GAP-ACCOUNT-001：

    trading/account.py
    trading/reconciliation.py
    adapters/sinopac/account_mapping.py

Tests：

    tests/unit/

Final exact path：

以 accepted runtime commit 為準。

---

## 5. GAP-ACCOUNT-001 Acceptance Evidence

Work Package：

    GAP-ACCOUNT-001

Runtime commit：

    50813b679f818f3837a9f50fdcda9921495ab507

Accepted Blueprint leaves：

    D630

    I510 I520 I530
    I610 I620 I630 I640 I650

    J210 J220 J230 J240
    J310 J320 J330
    J410 J420 J430 J440
    J510 J520 J530 J540 J550 J560 J570 J580 J590

Runtime paths：

    trading/account.py
    trading/reconciliation.py
    adapters/sinopac/account_mapping.py
    domain/broker_instruments.py

Verification：

    targeted tests: 50 passed
    compatibility tests: 48 passed
    full regression: 776 passed
    git diff --check: PASS

Acceptance：

    PASS

Conservative metric rule：

只有 ACTIVE 明確 Implements 的 29 leaves 在本次 closure 升為 ACCEPTED。
其他因 implementation 產生的 supporting evidence 不在本次自動升級 lifecycle。

---

## 6. GAP-BROKER-001 Acceptance Evidence

Work Package：

    GAP-BROKER-001

Runtime commit：

    b5d309cc91c6dbdf539c17a46662cdde46716224

Accepted Blueprint leaves：

    H210 H220 H230 H240 H250
    I340 I350

Runtime paths：

    trading/execution.py
    backtest/broker.py
    backtest/paper_broker.py
    backtest/shioaji_broker.py
    backtest/shioaji_mapping.py

Primary verification paths：

    tests/unit/test_trading_execution.py
    tests/unit/test_shioaji_mapping.py
    tests/unit/test_shioaji_broker.py
    tests/unit/test_paper_broker.py

Runtime evidence：

- PositionEffect exact values：OPEN / REDUCE / CLOSE。
- immutable broker-neutral OrderIntent。
- pure expected-position validation。
- ShioajiBroker requires explicit intent。
- LONG OPEN -> Buy + New。
- SHORT OPEN -> Sell + New。
- LONG REDUCE/CLOSE -> Sell + Cover。
- SHORT REDUCE/CLOSE -> Buy + Cover。
- ENTRY-prefixed CLOSE -> Cover。
- EXIT-prefixed OPEN -> New。
- no order-ID New/Cover inference。
- no Auto business inference。
- no DayTrade mapping。

Verification：

    targeted tests: 49 passed
    compatibility tests: 80 passed
    full regression: 800 passed
    git diff --check: PASS

Acceptance：

    PASS

Calibration：

    model: GPT-5.6 Sol
    effort: 輕度
    user-observed 5HR usage: 14%
    files inspected: about 22
    runtime/test files changed: 20
    tool operations: 24
    implementation correction cycles: 0
    command syntax retries: 2
    wall time: unavailable
    token/context usage: unavailable

Conservative metric rule：

只有 ACTIVE Implements 的 7 leaves 在本次 acceptance 升為 ACCEPTED。

H910-H940 保持 DESIGN_FROZEN，不因本 Work Package 自動升級。

---

## 7. GAP-RECON-001A Acceptance Evidence

Work Package：

    GAP-RECON-001A

Parent GAP：

    GAP-RECON-001

Runtime commit：

    d7dbd884f09e72d7737726409e11e0679206ed8d

Accepted Blueprint leaves：

    J610 J620 J630 J640 J650 J660 J670 J680 J690

Runtime path：

    trading/reconciliation.py

Primary verification path：

    tests/unit/test_reconciliation.py

Runtime evidence：

- ReconciliationStatus 保留既有六值並新增 UNKNOWN_EXTERNAL_STATE。
- ReconciliationResult evidence immutable、trim / nonblank。
- UNKNOWN_EXTERNAL_STATE 必須有 evidence 且 actual=None。
- ExternalStateUnknownError 為 explicit RuntimeError contract。
- ReconciliationPolicy exact four values。
- ReconciliationCaseState exact HALT / REVIEW_REQUIRED / RESOLVED。
- MATCH 不建立 ReconciliationCase。
- STRICT_HALT mismatch -> HALT。
- 其他 frozen policies mismatch -> REVIEW_REQUIRED。
- resolution pure transition，原 case 不 mutation。
- BROKER_AUTHORITATIVE / INTERNAL_AUTHORITATIVE 不執行 corrective action。
- compare_positions precedence 保持 contract -> direction -> quantity -> MATCH。
- no persistence。
- no startup orchestration。
- no corrective OrderIntent / broker action。
- GAP-RECON-001B 未開始。

Verification：

    targeted tests: 32 passed
    compatibility tests: 22 passed
    full regression: 821 passed
    git diff --check: PASS

Acceptance：

    PASS

Calibration：

    model: GPT-5.6 Sol
    effort: 輕度
    user-observed 5HR usage: 11%
    files read: 8
    runtime/test files changed: 2
    tool operations: 19
    implementation correction cycles: 0
    command/tool retries: 0
    wall time: unavailable
    token/context usage: unavailable

Conservative metric rule：

只有 ACTIVE Implements 的 9 leaves 在本次 acceptance 升為 ACCEPTED。

J710-J780 保持 DESIGN_FROZEN。

GAP-RECON-001 parent remains IN_PROGRESS。

GAP-RECON-001B 尚未授權。

---

## 8. GAP-RECON-001B Acceptance Evidence

Work Package：

    GAP-RECON-001B

Parent GAP：

    GAP-RECON-001

Runtime commit：

    4049f982474454556baf8734a5729ecbedc7a438

Accepted Blueprint leaves：

    J710 J720 J730 J740 J750 J760 J770 J780

Runtime path：

    trading/reconciliation.py

Primary verification path：

    tests/unit/test_reconciliation.py

Runtime evidence：

- ReconciliationCollectionError explicit collection failure contract。
- deterministic broker/account/instrument scope matching。
- exact contract identity 優先。
- unique opposite leftovers -> CONTRACT_MISMATCH。
- ambiguous unmatched collections explicit reject。
- no list-order / quantity / direction guessing。
- ExpectedPositionLoader read-only Protocol。
- existing BrokerPositionProvider startup observation。
- startup returned account scope validation。
- StartupReadinessState exact READY / HALT / REVIEW。
- StartupReconciliationResult immutable / extra-forbid。
- strategy_state_ready=False 優先 HALT。
- only broker ExternalStateUnknownError converts to UNKNOWN_EXTERNAL_STATE。
- unrelated loader/provider/programming errors propagate。
- no automatic repair / adoption / corrective OrderIntent。
- no persistence backend。
- no strategy reconstruction implementation。

Verification：

    targeted tests: 58 passed
    compatibility tests: 22 passed
    full regression: 847 passed
    git diff --check: PASS

Acceptance：

    PASS

Calibration：

    model: GPT-5.6 Sol
    effort: 輕度
    user-observed 5HR usage: 16%
    files read: 8
    runtime/test files changed: 2
    tool operations: 22
    implementation correction cycles: 1
    command/tool retries: 0
    wall time: unavailable
    token/context usage: unavailable

Correction note：

唯一 correction cycle 為測試 fixture 修正，使唯一雙側 leftover 正確遵循 frozen CONTRACT_MISMATCH rule。

Conservative metric rule：

只有 ACTIVE Implements 的 8 leaves 在本次 acceptance 升為 ACCEPTED。

GAP-RECON-001 runtime scope 已完成；parent closure 由 deterministic documentation phase 執行。

---

## 9. GAP-BROKER-002 Acceptance Evidence

Work Package：

    GAP-BROKER-002

Runtime commit：

    7d7fdabcb99da59d3d23ccec62b11c6572ceea82

Accepted Blueprint leaves：

    I120 I130 I140 I940

Runtime paths：

    adapters/capabilities.py
    adapters/sinopac/capabilities.py

Primary verification path：

    tests/unit/test_broker_capabilities.py

Runtime evidence：

- BrokerCapability exact 8 frozen values。
- BrokerCapabilitySupport exact SUPPORTED / UNSUPPORTED / UNKNOWN。
- BrokerVerificationMode exact DOCUMENTATION / FAKE / SIMULATION / PRODUCTION。
- verification modes have no implicit hierarchy。
- immutable BrokerCapabilityEvidence with source/version/date/mode evidence。
- immutable deterministic BrokerCapabilityMatrix。
- duplicate capability / evidence inconsistencies explicit reject。
- BrokerCapabilityUnavailableError for missing / unsupported / unknown / insufficient verification。
- SINOPAC matrix contains exact 8 capabilities。
- SDK evidence version 1.7.6。
- evidence date 2026-09-25。
- concrete initial matrix is DOCUMENTATION-only。
- no SIMULATION evidence claimed。
- no PRODUCTION evidence claimed。
- no network/login/logout/CA/credential/order/LIVE action surface added。

Verification：

    targeted tests: 22 passed
    compatibility tests: 45 passed
    full regression: 869 passed
    git diff --check: PASS

Acceptance：

    PASS

Calibration：

    model: GPT-5.6 Sol
    effort: 輕度
    user-observed 5HR usage: 10%
    files read: 12
    files created: 3
    existing files modified: 0
    tool operations: 17
    implementation correction cycles: 0
    command/tool retries: 2
    wall time: approximately 3m44s
    token/context usage: unavailable

Five-sample calibration：

    5HR observations: 12%, 14%, 11%, 16%, 10%
    average: 12.60%
    total implementation correction cycles: 1

Retry note：

- sandbox fetch escalation。
- pytest executable path correction。
- neither retry changed frozen public semantics。

Conservative metric rule：

只有 ACTIVE Implements 的 I120 / I130 / I140 / I940 在本次升為 ACCEPTED。

I720 / I730 / I740 / I820 / I920 / I930 remain outside this accepted runtime scope。

## 10. GAP-08ABCD Acceptance Evidence

Work Package：

    GAP-08ABCD

Runtime commit：

    98dc38ce39bdab191ce0bc6d71e37ef69059ec9c

Accepted Blueprint leaves：

    K110 K120 K130 K140 K150 K160 K170
    K210 K220 K230 K240
    K610 K620 K630 K640 K650 K660 K670 K680

Accepted weight：

    77

Verification：

    targeted: 28 passed
    PostgreSQL integration: 2 skipped
    compatibility: 80 passed
    full regression: 897 passed / 2 skipped
    git diff --check: PASS

PostgreSQL compatibility：

    17: PENDING
    18: PENDING

Calibration：

    model: GPT-5.6 Sol
    effort: 輕度
    user-observed 5HR usage: 12%
    files read: 8
    files created: 14
    existing files modified: 1
    tool operations: 23
    implementation correction cycles: 1
    command/tool retries: 1
    wall time: approximately 12m09s
    token/context usage: unavailable

Six-sample calibration：

    5HR observations: 12%, 14%, 11%, 16%, 10%, 12%
    average: 12.50%
    total implementation correction cycles: 2

Sizing conclusion：

expanded coherent scope did not increase observed quota usage，
but future expansion remains bounded by canonical ownership / authority / recovery safety seams。
