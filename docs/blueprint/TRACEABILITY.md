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
